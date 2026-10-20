"""WEARABLES × RARE DISEASE census (RAPID TA1 wearables tab).

"How many All of Us participants have Fitbit data AND a rare-disease diagnosis, and
which rare diseases have the most wearables data?"

RARE = Mondo's rare-disease subsets. Mondo tags each disease with the sources that call
it rare (`orphanet_rare`, `gard_rare`, `nord_rare`, `inferred_rare`, `mondo_rare`, and
the union `rare`), so GARD / Orphanet / NORD are each a filter on one Mondo download.
Mondo -> OMOP goes through CHARMPheno's port of Monarch's mondo2omop
(`rapidaudit.mondo_to_omop_mapping.build_mondo_to_omop`: Mondo `same_as` SNOMED / ICD10CM / MeSH
xref -> concept -> 'Maps to' -> standard Condition), then each mapped standard concept
is widened to its OMOP descendants (`concept_ancestor`).

WEARABLES = the Fitbit daily-summary tables of the CDR (`activity_summary`,
`heart_rate_summary`, `sleep_daily_summary` — whichever exist in this CDR version; the
driver says which it found). A participant's wear is the number of DISTINCT DAYS with
any daily summary, plus the first and last such day. A handful of days is not usable
data, so the headline columns require `--min-days` (default 30).

Per Mondo rare disease (pooled counts of persons):
  n_dx             persons with any in-subtree condition_occurrence
  n_wear           ... who also have >= --min-days of Fitbit data
  n_wear_before    ... whose Fitbit data STARTS on or before the first diagnosis
                   (wearables data from before the diagnosis — the early-detection case)
  n_wear_span      ... whose Fitbit span covers the first diagnosis date
Plus `group` (another mapped rare node sits under it, so its counts include its
children's) and `suspect` (n_dx above --suspect-share of the condition population: far
too common for a rare disease, usually an over-broad SNOMED xref).

EGRESS: rows with n_wear < 20 are dropped; any remaining cell in 1..19 prints as "<20".
`wearables_rare_<tag>_all.tsv` keeps EVERY mapped rare node (0 where undiagnosed), with
cells in 1..19 as "<20" and no % column.
Output goes to --out-dir (a workspace run dir), never the tree.

The heavy joins run in BigQuery (google-cloud-bigquery from a Workbench VM; no
Spark). The small (mondo_id, concept_id) rare map goes in as array query parameters.

Ported from CHARMPheno analysis/cloud/diag_wearables_rare.py (branch
claude/dismech-ribbon, a6a3a776), a Spark/Dataproc driver: same method and outputs, plus
the _all.tsv output.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import pandas as pd

from rapidaudit.egress import EGRESS_FLOOR, cell, mask_counts
from rapidaudit.aou import bq_client, download_cached, query, workspace_env
from rapidaudit.mondo_to_omop_mapping import (_disease_child_adjacency,
                                              build_mondo_to_omop, seed_source_xrefs)

_SOURCE_FLAGS = ("rare", "orphanet_rare", "gard_rare", "nord_rare", "inferred_rare",
                 "mondo_rare")
# (table, candidate date columns) — the Fitbit daily summaries of the AoU CDR.
_WEAR_TABLES = (("activity_summary", ("date",)),
                ("heart_rate_summary", ("date",)),
                ("sleep_daily_summary", ("sleep_date", "date")))


def rare_concept_map(mapping: pd.DataFrame, flags) -> pd.DataFrame:
    """(mondo_id, standard_concept_id) rows for Mondo nodes carrying ANY of `flags`,
    with one 0/1 column per known source flag (so the report can split by source)."""
    flags = list(flags)
    have = [f for f in _SOURCE_FLAGS if f in mapping.columns]
    m = mapping.copy()
    for f in have:
        m[f] = m[f].fillna(0).astype(int)
    sel = m[[f for f in flags if f in m.columns]].sum(axis=1) > 0
    out = (m.loc[sel, ["mondo_id", "standard_concept_id", *have]]
           .drop_duplicates(["mondo_id", "standard_concept_id"]))
    out["standard_concept_id"] = out["standard_concept_id"].astype("int64")
    return out.reset_index(drop=True)


def group_nodes(mondo_ids, child_adj) -> set:
    """Mapped rare nodes that have ANOTHER mapped rare node below them in Mondo: their
    counts include their descendants' patients (a grouping, not one disease)."""
    ids = set(mondo_ids)
    out = set()
    for m in ids:
        stack, seen = list(child_adj.get(m, ())), set()
        while stack:
            n = stack.pop()
            if n in seen:
                continue
            seen.add(n)
            if n in ids:
                out.add(m)
                break
            stack.extend(child_adj.get(n, ()))
    return out


def format_report(rows: pd.DataFrame, overall: dict, *, min_days, top,
                  floor=EGRESS_FLOOR) -> str:
    """Markdown: the overall counts, then the top-`top` rare diseases by n_wear. Rows
    under the floor are dropped before this is called (`table_rows`)."""
    L = ["# Wearables × rare disease (All of Us)", "",
         f"Fitbit tables found: {', '.join(overall['wear_tables']) or 'NONE'} · "
         f"usable wear = >= {min_days} distinct days · rare = Mondo subsets "
         f"{', '.join(overall['flags'])} · {overall['n_rare_nodes']:,} rare Mondo nodes "
         f"mapped to {overall['n_rare_concepts']:,} standard concepts "
         f"({overall['n_rare_concepts_desc']:,} with descendants)", "",
         "| population | persons |", "|---|--:|"]
    for k, v in overall["counts"].items():
        L.append(f"| {k} | {cell(v, floor)} |")
    L += ["", f"## Rare diseases with the most wearables data (top {top}; "
          f"n_wear >= {floor})", "",
          "| Mondo | disease | n_dx | n_wear | % | wear before dx | wear spans dx | "
          "sources | note |", "|---|---|--:|--:|--:|--:|--:|---|---|"]
    for _, r in rows.head(int(top)).iterrows():
        note = ", ".join(x for x, f in (("group", r["group"]), ("SUSPECT broad", r["suspect"]))
                         if f)
        L.append(f"| {r['mondo_id']} | {str(r['name'])[:48]} | {cell(r['n_dx'], floor)} | "
                 f"{cell(r['n_wear'], floor)} | {100 * r['n_wear'] / max(r['n_dx'], 1):.1f} | "
                 f"{cell(r['n_wear_before'], floor)} | {cell(r['n_wear_span'], floor)} | "
                 f"{r['sources']} | {note} |")
    return "\n".join(L) + "\n"


def table_rows(per: pd.DataFrame, names: dict, groups: set, flags_by_node: dict, *,
               n_cond_pop, suspect_share, floor=EGRESS_FLOOR,
               keep_small=False) -> pd.DataFrame:
    """Per-node rows over the floor (all rows if `keep_small`; mask them with `cell`
    before egress), sorted by n_wear, with name / group / suspect / sources
    annotations."""
    d = per.copy() if keep_small else per[per["n_wear"] >= floor].copy()
    d["name"] = d["mondo_id"].map(lambda m: names.get(m, m))
    d["group"] = d["mondo_id"].isin(groups)
    d["suspect"] = d["n_dx"] > float(suspect_share) * max(int(n_cond_pop), 1)
    d["sources"] = d["mondo_id"].map(
        lambda m: ",".join(f.replace("_rare", "") for f in flags_by_node.get(m, ())))
    return d.sort_values(["n_wear", "n_dx"], ascending=False).reset_index(drop=True)


def wear_union_sql(cdr: str, columns_by_table: dict) -> tuple[str, list]:
    """UNION ALL of (person_id, d) over the Fitbit daily-summary tables present in the
    CDR, picking each table's first available date column. Returns (sql, tables used)."""
    parts, found = [], []
    for t, cols in _WEAR_TABLES:
        have = columns_by_table.get(t)
        if not have:
            print(f"[wear] {t}: not in this CDR; skipped", flush=True)
            continue
        dc = next((c for c in cols if c in have), None)
        if dc is None:
            print(f"[wear] {t}: no date column among {cols}; skipped", flush=True)
            continue
        parts.append(f"SELECT person_id, CAST({dc} AS DATE) AS d FROM `{cdr}.{t}`")
        found.append(t)
    if not parts:
        raise SystemExit("[wear] no Fitbit daily-summary table found in this CDR")
    return "\n    UNION ALL\n    ".join(parts), found


def census_ctes(cdr: str, wear_union: str) -> str:
    """Shared WITH clause. Params: @mondo ARRAY<STRING> and @cid ARRAY<INT64> (parallel:
    the rare map), @min_days INT64. `j` = one row per (person, rare node) with the first
    in-subtree diagnosis and that person's Fitbit wear."""
    return f"""
WITH rmap AS (
  SELECT m AS mondo_id, @cid[OFFSET(i)] AS standard_concept_id
  FROM UNNEST(@mondo) AS m WITH OFFSET i),
node_concepts AS (
  SELECT DISTINCT r.mondo_id, ca.descendant_concept_id AS cid
  FROM rmap r
  JOIN `{cdr}.concept_ancestor` ca ON ca.ancestor_concept_id = r.standard_concept_id),
dx AS (
  SELECT co.person_id, nc.mondo_id, MIN(CAST(co.condition_start_date AS DATE)) AS first_dx
  FROM `{cdr}.condition_occurrence` co
  JOIN node_concepts nc ON co.condition_concept_id = nc.cid
  GROUP BY 1, 2),
wear_days AS (
    {wear_union}),
wear AS (
  SELECT person_id, COUNT(DISTINCT d) AS fb_days, MIN(d) AS fb_start, MAX(d) AS fb_end
  FROM wear_days WHERE d IS NOT NULL GROUP BY person_id),
j AS (
  SELECT dx.person_id, dx.mondo_id, dx.first_dx, w.fb_start, w.fb_end,
         COALESCE(w.fb_days >= @min_days, FALSE) AS ok
  FROM dx LEFT JOIN wear w USING (person_id))
"""


PER_NODE_SELECT = """
SELECT mondo_id,
  COUNT(DISTINCT person_id) AS n_dx,
  COUNT(DISTINCT IF(ok, person_id, NULL)) AS n_wear,
  COUNT(DISTINCT IF(ok AND fb_start <= first_dx, person_id, NULL)) AS n_wear_before,
  COUNT(DISTINCT IF(ok AND fb_start <= first_dx AND fb_end >= first_dx, person_id, NULL))
    AS n_wear_span
FROM j GROUP BY mondo_id
"""


def overall_select(cdr: str) -> str:
    """One row of population counts. Extra params: @nongroup and one ARRAY<STRING> per
    source flag in _SOURCE_FLAGS[1:4] (empty arrays are fine)."""
    per_src = ",\n".join(
        f"  COUNT(DISTINCT IF(mondo_id IN UNNEST(@{f}), person_id, NULL)) AS {f}_dx,\n"
        f"  COUNT(DISTINCT IF(ok AND mondo_id IN UNNEST(@{f}), person_id, NULL)) "
        f"AS {f}_wear" for f in _SOURCE_FLAGS[1:4])
    return f"""
SELECT
  (SELECT COUNT(DISTINCT person_id) FROM `{cdr}.condition_occurrence`) AS n_cond_pop,
  (SELECT COUNT(*) FROM wear) AS n_wear_any,
  (SELECT COUNTIF(fb_days >= @min_days) FROM wear) AS n_wear_ok,
  (SELECT COUNT(DISTINCT cid) FROM node_concepts) AS n_desc,
  COUNT(DISTINCT person_id) AS rare_dx,
  COUNT(DISTINCT IF(ok, person_id, NULL)) AS rare_wear,
  COUNT(DISTINCT IF(ok AND mondo_id IN UNNEST(@nongroup), person_id, NULL)) AS nongroup_wear,
{per_src}
FROM j
"""


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    p.add_argument("--out-dir", required=True)
    p.add_argument("--flags", default="rare",
                   help="comma list of Mondo rare subsets to include (any-of): "
                        + ", ".join(_SOURCE_FLAGS))
    p.add_argument("--min-days", type=int, default=30)
    p.add_argument("--top", type=int, default=60)
    p.add_argument("--suspect-share", type=float, default=0.005,
                   help="flag a 'rare' node diagnosed in more than this share of the "
                        "persons with any condition (over-broad mapping)")
    p.add_argument("--mondo-version", default="2026-06-02")
    p.add_argument("--mondo-cache-dir", default="data/mondo")
    args = p.parse_args(argv)
    cdr, billing = workspace_env()
    flags = [f.strip() for f in args.flags.split(",") if f.strip()]
    bad = [f for f in flags if f not in _SOURCE_FLAGS]
    if bad:
        raise SystemExit(f"unknown --flags {bad}; known: {_SOURCE_FLAGS}")
    out = Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    client = bq_client(billing)

    # 1) Mondo rare nodes -> OMOP standard conditions (mondo2omop recipe). Only the
    #    concepts the Mondo xrefs can hit, plus their 'Maps to' targets, are fetched.
    cache = Path(args.mondo_cache_dir)
    edges = pd.read_csv(download_cached(args.mondo_version, "mondo_edges.tsv", cache),
                        sep="\t", low_memory=False)
    nodes = pd.read_csv(download_cached(args.mondo_version, "mondo_nodes.tsv", cache),
                        sep="\t", low_memory=False)
    same_as = seed_source_xrefs(mondo_edges_df=edges, mondo_nodes_df=nodes,
                                restrict_mondo_ids=set(nodes["id"]))
    keys = sorted(set(same_as["vocabulary_id"] + "|" + same_as["concept_code"].astype(str)))
    src_cte = f"""
WITH src AS (
  SELECT concept_id, concept_name, vocabulary_id, domain_id, concept_code, standard_concept
  FROM `{cdr}.concept`
  WHERE vocabulary_id IN ('SNOMED', 'ICD10CM', 'MeSH')
    AND CONCAT(vocabulary_id, '|', concept_code) IN UNNEST(@keys)),
mt AS (
  SELECT concept_id_1, concept_id_2, relationship_id
  FROM `{cdr}.concept_relationship`
  WHERE relationship_id = 'Maps to' AND concept_id_1 IN (SELECT concept_id FROM src))
"""
    kp = {"keys": ("STRING", keys)}
    cr_pd = query(client, src_cte + "SELECT * FROM mt", kp)
    concept_pd = query(client, src_cte + f"""
SELECT * FROM src
UNION DISTINCT
SELECT concept_id, concept_name, vocabulary_id, domain_id, concept_code, standard_concept
FROM `{cdr}.concept`
WHERE vocabulary_id IN ('SNOMED', 'ICD10CM', 'MeSH')
  AND concept_id IN (SELECT concept_id_2 FROM mt)""", kp)
    print(f"[wear] {len(keys):,} Mondo xrefs -> {len(concept_pd):,} concepts, "
          f"{len(cr_pd):,} 'Maps to' rows", flush=True)
    mapping = build_mondo_to_omop(mondo_edges_df=edges, mondo_nodes_df=nodes,
                                  concept_df=concept_pd, concept_relationship_df=cr_pd)
    rmap = rare_concept_map(mapping, flags)
    names = dict(zip(nodes["id"], nodes["name"].astype(str)))
    flags_by_node = {m: [f for f in _SOURCE_FLAGS[1:] if f in g.columns and g[f].max()]
                     for m, g in rmap.groupby("mondo_id")}
    groups = group_nodes(set(rmap["mondo_id"]), _disease_child_adjacency(edges, nodes))
    print(f"[wear] rare map: {rmap['mondo_id'].nunique():,} Mondo nodes -> "
          f"{rmap['standard_concept_id'].nunique():,} standard concepts "
          f"({len(groups):,} are groupings)", flush=True)

    # 2) Fitbit tables present in this CDR.
    cols = query(client, f"""
SELECT table_name, column_name FROM `{cdr}.INFORMATION_SCHEMA.COLUMNS`
WHERE table_name IN UNNEST(@tables)""",
                 {"tables": ("STRING", [t for t, _ in _WEAR_TABLES])})
    wear_union, found = wear_union_sql(
        cdr, cols.groupby("table_name")["column_name"].apply(set).to_dict())

    # 3) per-node and overall counts, computed in BigQuery.
    ctes = census_ctes(cdr, wear_union)
    params = {"mondo": ("STRING", rmap["mondo_id"].tolist()),
              "cid": ("INT64", [int(c) for c in rmap["standard_concept_id"]]),
              "min_days": ("INT64", int(args.min_days))}
    print("[wear] per-node counts query…", flush=True)
    per = query(client, ctes + PER_NODE_SELECT, params)
    src_ids = {f: sorted(rmap.loc[rmap[f] == 1, "mondo_id"].unique()) if f in rmap else []
               for f in _SOURCE_FLAGS[1:4]}
    print("[wear] overall counts query…", flush=True)
    o = query(client, ctes + overall_select(cdr), {
        **params, "nongroup": ("STRING", sorted(set(rmap["mondo_id"]) - groups)),
        **{f: ("STRING", ids) for f, ids in src_ids.items()}}).iloc[0]
    o = {k: int(v) for k, v in o.items()}

    n_cond_pop = o["n_cond_pop"]
    counts = {
        "persons with any condition": n_cond_pop,
        "persons with any Fitbit day": o["n_wear_any"],
        f"persons with >= {args.min_days} Fitbit days": o["n_wear_ok"],
        "persons with any rare dx": o["rare_dx"],
        f"... and >= {args.min_days} Fitbit days": o["rare_wear"],
        "... rare dx on a non-grouping node, with wear": o["nongroup_wear"]}
    for f, ids in src_ids.items():
        if ids:
            counts[f"  {f} dx"] = o[f"{f}_dx"]
            counts[f"  {f} dx with wear"] = o[f"{f}_wear"]

    rows = table_rows(per, names, groups, flags_by_node, n_cond_pop=n_cond_pop,
                      suspect_share=args.suspect_share)
    overall = {"wear_tables": found, "flags": flags,
               "n_rare_nodes": int(rmap["mondo_id"].nunique()),
               "n_rare_concepts": int(rmap["standard_concept_id"].nunique()),
               "n_rare_concepts_desc": o["n_desc"], "counts": counts}
    text = format_report(rows, overall, min_days=args.min_days, top=args.top)
    tag = "_".join(flags) + f"_d{args.min_days}"
    (out / f"wearables_rare_{tag}.md").write_text(text)
    keep = ["mondo_id", "name", "n_dx", "n_wear", "n_wear_before", "n_wear_span",
            "group", "suspect", "sources"]
    tsv = mask_counts(rows[keep], ["n_dx", "n_wear", "n_wear_before", "n_wear_span"])
    tsv.to_csv(out / f"wearables_rare_{tag}.tsv", sep="\t", index=False)
    # Every mapped rare node, nothing dropped: undiagnosed nodes as 0, cells 1-19 as <20.
    # No % column here (it would back out a masked n_wear).
    per_all = (pd.DataFrame({"mondo_id": sorted(set(rmap["mondo_id"]))})
               .merge(per, on="mondo_id", how="left").fillna(0))
    every = table_rows(per_all, names, groups, flags_by_node, n_cond_pop=n_cond_pop,
                       suspect_share=args.suspect_share, keep_small=True)[keep]
    every = mask_counts(every, ["n_dx", "n_wear", "n_wear_before", "n_wear_span"])
    every.to_csv(out / f"wearables_rare_{tag}_all.tsv", sep="\t", index=False)
    (out / f"wearables_rare_{tag}.json").write_text(json.dumps(overall, indent=1,
                                                               default=str))
    print(text, flush=True)
    print(f"[wear] wrote {out}/wearables_rare_{tag}.md/.tsv/.json (rows with n_wear < "
          f"{EGRESS_FLOOR} dropped, cells 1-19 as <20) and _all.tsv ({len(every):,} "
          f"rows, none dropped, cells 1-19 as <20)", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
