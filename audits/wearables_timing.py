"""WEARABLES TIMING around the first diagnosis (RAPID TA1 wearables tab).

"For participants with a given rare disease, how much Fitbit data of each kind do they
have before and after their first diagnosis?"

Diseases are chosen and mapped exactly as in `wearables_rare` (`build_rare_map`: Mondo
rare subsets, `--under`, `--exact`, OMOP descendants unless `--no-descendants`,
`--min-dx-dates`). A person's first diagnosis for a disease is their earliest in-disease
condition_occurrence. The `ALL` row pools the selected diseases: each person once, at
their earliest first diagnosis among them.

KINDS of wearables data = each Fitbit table present in the CDR, counted as distinct days
with at least one row: the daily summaries (`activity_summary`, `heart_rate_summary`,
`sleep_daily_summary`) and, unless `--no-intraday`, the intraday tables
(`heart_rate_minute_level`, `steps_intraday`, `sleep_level`). `any` = a day in any of
them. Days strictly before the first diagnosis count as BEFORE; the diagnosis day and
later count as AFTER.

Per (disease, kind), over persons with the disease and at least one day of that kind:
  n_wear                persons with any day of this kind
  n_before / n_after    ... with >= 1 day before / on-or-after the first diagnosis
  n_pre<t> / n_post<t> / n_both<t>
                        ... with >= t days (each t in --window-thresholds, default 7
                        and 30) in the --window-days before the diagnosis / from it on /
                        both (the before-vs-after contrast)
  before_p25/p50/p75    quartiles of days before, among n_before (blank if n_before < 20)
  after_p25/p50/p75     quartiles of days after, among n_after
  lead_p25/p50/p75      days from the first wear day to the diagnosis, among n_before
  follow_p25/p50/p75    days from the diagnosis to the last wear day, among n_after
  before_<bin>, after_<bin>
                        persons by days before / after, in bins (1-29, 30-89, ...)

EGRESS: every count goes through `cell` (1..19 -> "<20"); quartiles are published only
when the persons behind them number >= 20, with no min/max. The columns are NESTED
(n_wear >= n_before >= n_pre7 >= n_pre30, `any` >= each kind, ALL >= each disease), so a
difference of two published cells can be a small count: check before sharing a table
beyond the Workbench team.

BigQuery returns one aggregated row per (person, disease, kind) without person ids; the
distributions are computed in pandas. Nothing person-level is written, except the
optional `--patient-plots` PNGs, whose names carry DO_NOT_EGRESS.

OUTPUT: one flat folder per CDR (`<out-dir>/<CDR dataset>/`); every file starts with the
run name (`run_name`, e.g. `autoimmune-disease_exact`) and says what it is:
`_report.md`, `_table.tsv`, `_mapping.tsv`, `_run.json`, `_plot-*.png`, and
`_DO_NOT_EGRESS_patients-*.png`.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

import pandas as pd

from audits.wearables_rare import _SOURCE_FLAGS, build_rare_map
from rapidaudit.aou import bq_client, query, workspace_env
from rapidaudit.egress import EGRESS_FLOOR, cell, mask_counts

# (table, candidate date columns, intraday?) — the Fitbit tables of the AoU CDR.
_TIMING_TABLES = (("activity_summary", ("date",), False),
                  ("heart_rate_summary", ("date",), False),
                  ("sleep_daily_summary", ("sleep_date", "date"), False),
                  ("heart_rate_minute_level", ("datetime",), True),
                  ("steps_intraday", ("datetime",), True),
                  ("sleep_level", ("sleep_date", "start_datetime"), True))
ALL = "ALL"
ANY = "any"
# Bin lower edges for persons' day counts (persons with 0 days are not binned).
DAY_BINS = (1, 30, 90, 365, 730)
QUARTILES = (("p25", 0.25), ("p50", 0.5), ("p75", 0.75))
WINDOW_THRESHOLDS = (7, 30)
# The default rare-source set (Orphanet / GARD / NORD / Mondo, not inferred): left out of
# run names; any other --flags set is spelled out.
STANDARD_FLAGS = {"orphanet_rare", "gard_rare", "nord_rare", "mondo_rare"}


def bin_labels(edges=DAY_BINS) -> list[str]:
    return [f"{lo}-{hi - 1}" for lo, hi in zip(edges, edges[1:])] + [f"{edges[-1]}+"]


def typed_wear_sql(cdr: str, columns_by_table: dict, intraday: bool = True
                   ) -> tuple[str, list]:
    """UNION ALL of (person_id, src, d) over the Fitbit tables present in the CDR, each
    restricted (by a JOIN, not IN: BigQuery rejects the correlated
    form) to persons in the `cohort` CTE. Returns (sql, tables used)."""
    parts, found = [], []
    for t, cols, is_intraday in _TIMING_TABLES:
        if is_intraday and not intraday:
            continue
        have = columns_by_table.get(t)
        if not have:
            print(f"[timing] {t}: not in this CDR; skipped", flush=True)
            continue
        dc = next((c for c in cols if c in have), None)
        if dc is None:
            print(f"[timing] {t}: no date column among {cols}; skipped", flush=True)
            continue
        parts.append(f"SELECT t.person_id, '{t}' AS src, CAST(t.{dc} AS DATE) AS d "
                     f"FROM `{cdr}.{t}` t JOIN cohort c ON t.person_id = c.person_id")
        found.append(t)
    if not parts:
        raise SystemExit("[timing] no Fitbit table found in this CDR")
    return "\n    UNION ALL\n    ".join(parts), found


def timing_ctes(cdr: str, wear_sql: str, descendants: bool = True) -> str:
    """WITH clause. Params: @mondo ARRAY<STRING> / @cid ARRAY<INT64> (the rare map, as in
    wearables_rare.census_ctes) and @min_dx_dates INT64. `dx_all` = (person, disease,
    first_dx) plus one ALL row per person; `wd` = (person, kind, day), with kind 'any'
    for a day of any kind."""
    node_concepts = (f"""
  SELECT DISTINCT r.mondo_id, ca.descendant_concept_id AS cid
  FROM rmap r
  JOIN `{cdr}.concept_ancestor` ca ON ca.ancestor_concept_id = r.standard_concept_id"""
                     if descendants else """
  SELECT DISTINCT mondo_id, standard_concept_id AS cid FROM rmap""")
    return f"""
WITH rmap AS (
  SELECT m AS mondo_id, @cid[OFFSET(i)] AS standard_concept_id
  FROM UNNEST(@mondo) AS m WITH OFFSET i),
node_concepts AS ({node_concepts}),
dx AS (
  SELECT co.person_id, nc.mondo_id, MIN(CAST(co.condition_start_date AS DATE)) AS first_dx
  FROM `{cdr}.condition_occurrence` co
  JOIN node_concepts nc ON co.condition_concept_id = nc.cid
  GROUP BY 1, 2
  HAVING COUNT(DISTINCT CAST(co.condition_start_date AS DATE)) >= @min_dx_dates),
dx_all AS (
  SELECT person_id, mondo_id, first_dx FROM dx
  UNION ALL
  SELECT person_id, '{ALL}' AS mondo_id, MIN(first_dx) AS first_dx FROM dx GROUP BY person_id),
cohort AS (SELECT DISTINCT person_id FROM dx),
wear_days AS (
  SELECT DISTINCT person_id, src, d FROM (
    {wear_sql})
  WHERE d IS NOT NULL),
wd AS (
  SELECT person_id, src, d FROM wear_days
  UNION ALL
  SELECT DISTINCT person_id, '{ANY}' AS src, d FROM wear_days)
"""


N_DX_SELECT = "SELECT mondo_id, COUNT(*) AS n_dx FROM dx_all GROUP BY mondo_id"

# One row per (person, disease, kind); person_id is grouped on but not returned.
# Extra param: @win_days INT64.
PER_PERSON_SELECT = """
SELECT x.mondo_id, w.src,
  COUNTIF(w.d < x.first_dx) AS days_before,
  COUNTIF(w.d >= x.first_dx) AS days_after,
  COUNTIF(w.d < x.first_dx AND w.d >= DATE_SUB(x.first_dx, INTERVAL @win_days DAY))
    AS days_pre_win,
  COUNTIF(w.d >= x.first_dx AND w.d < DATE_ADD(x.first_dx, INTERVAL @win_days DAY))
    AS days_post_win,
  DATE_DIFF(x.first_dx, MIN(w.d), DAY) AS lead_days,
  DATE_DIFF(MAX(w.d), x.first_dx, DAY) AS follow_days
FROM dx_all x JOIN wd w USING (person_id)
GROUP BY x.person_id, x.mondo_id, x.first_dx, w.src
"""


def _quartiles(s: pd.Series, prefix: str, floor: int) -> dict:
    ok = len(s) >= floor
    return {f"{prefix}_{k}": (round(float(s.quantile(q))) if ok else None)
            for k, q in QUARTILES}


def _bins(s: pd.Series, prefix: str, edges=DAY_BINS) -> dict:
    hi = list(edges[1:]) + [float("inf")]
    return {f"{prefix}_{lab}": int(((s >= lo) & (s < h)).sum())
            for lab, lo, h in zip(bin_labels(edges), edges, hi)}


def profile(per: pd.DataFrame, n_dx: pd.DataFrame, *, thresholds=WINDOW_THRESHOLDS,
            floor: int = EGRESS_FLOOR) -> pd.DataFrame:
    """Raw (unmasked) per-(disease, kind) summary of the PER_PERSON_SELECT rows. Every
    disease in `n_dx` gets a row per kind seen anywhere in `per` (0 where nobody has it).
    Quartiles are None where fewer than `floor` persons are behind them."""
    kinds = sorted(per["src"].unique(), key=lambda k: (k != ANY, k))
    rows = []
    for m, nd in zip(n_dx["mondo_id"], n_dx["n_dx"]):
        for k in kinds:
            g = per[(per["mondo_id"] == m) & (per["src"] == k)]
            b, a = g[g["days_before"] > 0], g[g["days_after"] > 0]
            win = {}
            for t in thresholds:
                pre, post = g["days_pre_win"] >= t, g["days_post_win"] >= t
                win |= {f"n_pre{t}": int(pre.sum()), f"n_post{t}": int(post.sum()),
                        f"n_both{t}": int((pre & post).sum())}
            rows.append({
                "mondo_id": m, "src": k, "n_dx": int(nd), "n_wear": len(g),
                "n_before": len(b), "n_after": len(a), **win,
                **_quartiles(b["days_before"], "before", floor),
                **_quartiles(a["days_after"], "after", floor),
                **_quartiles(b["lead_days"], "lead", floor),
                **_quartiles(a["follow_days"], "follow", floor),
                **_bins(g["days_before"], "before"), **_bins(g["days_after"], "after")})
    return pd.DataFrame(rows)


def count_columns(prof: pd.DataFrame) -> list[str]:
    bins = {f"{side}_{lab}" for side in ("before", "after") for lab in bin_labels()}
    return [c for c in prof.columns if c.startswith("n_") or c in bins]


def masked(prof: pd.DataFrame, names: dict, floor: int = EGRESS_FLOOR) -> pd.DataFrame:
    """Egress-safe copy: counts via `cell`, quartiles as ints or blank."""
    out = mask_counts(prof, count_columns(prof), floor)
    for c in out.columns:
        if c.endswith(tuple(k for k, _ in QUARTILES)):
            out[c] = prof[c].map(lambda v: "" if v is None or pd.isna(v) else str(int(v)))
    out.insert(1, "name", out["mondo_id"].map(
        lambda m: "all selected diseases" if m == ALL else names.get(m, m)))
    return out


def _iqr(r, prefix) -> str:
    if r[f"{prefix}_p50"] is None or pd.isna(r[f"{prefix}_p50"]):
        return "—"
    return (f"{int(r[f'{prefix}_p50']):,} ({int(r[f'{prefix}_p25']):,}–"
            f"{int(r[f'{prefix}_p75']):,})")


def format_report(prof: pd.DataFrame, names: dict, meta: dict, *, top: int,
                  floor: int = EGRESS_FLOOR) -> str:
    """Markdown: the pooled ALL rows by kind (counts, quartiles, bins), then per disease
    (n_wear in `any` >= floor) the `any` summary and a kinds table."""
    w, ts = meta["window_days"], meta["window_thresholds"]
    win_head = "".join(f"≥{t} in {w} before | ≥{t} in {w} after | both ≥{t} | " for t in ts)
    win_align = "--:|" * (3 * len(ts))

    def win_cells(r):
        return "".join(f"{cell(r[f'n_pre{t}'], floor)} | {cell(r[f'n_post{t}'], floor)} | "
                       f"{cell(r[f'n_both{t}'], floor)} | " for t in ts)
    L = ["# Wearables data before and after first diagnosis (All of Us)", "",
         f"CDR: `{meta['cdr']}`", "",
         f"Fitbit tables: {', '.join(meta['wear_tables'])} · rare = Mondo subsets "
         f"{', '.join(meta['flags'])} · {meta['n_rare_nodes']:,} diseases mapped", ""]
    scope = [f"under {', '.join(meta['under'])}" if meta.get("under") else "",
             "exact SNOMED-only mapping" if meta.get("exact") else "",
             "mapped concepts only (no descendants)"
             if meta.get("descendants") is False else "",
             f"dx on >= {meta['min_dx_dates']} distinct dates"
             if meta.get("min_dx_dates", 1) > 1 else ""]
    if any(scope):
        L += ["Scope: " + " · ".join(x for x in scope if x), ""]
    L += ["Days = distinct days with any row in that table. Before = strictly before the "
          "first diagnosis; after = that day or later. Medians are shown as "
          "median (p25–p75), and only where >= 20 persons are behind them. Columns are "
          "nested, so differences between cells can be small counts: check before "
          f"sharing. '≥t in {w} before' = at least t days of data in the {w} days before "
          "the first diagnosis (after: from it on); 'both' = both.", ""]

    a = prof[prof["mondo_id"] == ALL]
    nd = int(a["n_dx"].iloc[0]) if len(a) else 0
    L += ["## All selected diseases, by kind of data", "",
          f"Persons with any selected diagnosis: {cell(nd, floor)} (first diagnosis = "
          "earliest among the selected diseases).", "",
          f"| kind | persons | ≥1 day before | ≥1 day after | {win_head}days before | "
          "days after | first wear → dx (days) | dx → last wear (days) |",
          f"|---|--:|--:|--:|{win_align}--:|--:|--:|--:|"]
    for _, r in a.iterrows():
        L.append(f"| {r['src']} | {cell(r['n_wear'], floor)} | {cell(r['n_before'], floor)} | "
                 f"{cell(r['n_after'], floor)} | {win_cells(r)}"
                 f"{_iqr(r, 'before')} | {_iqr(r, 'after')} | {_iqr(r, 'lead')} | "
                 f"{_iqr(r, 'follow')} |")
    labs = bin_labels()
    for side in ("before", "after"):
        L += ["", f"Persons by number of days {side} the first diagnosis:", "",
              "| kind | " + " | ".join(labs) + " |", "|---|" + "--:|" * len(labs)]
        for _, r in a.iterrows():
            L.append(f"| {r['src']} | "
                     + " | ".join(cell(r[f"{side}_{x}"], floor) for x in labs) + " |")

    d = prof[(prof["mondo_id"] != ALL) & (prof["src"] == ANY)]
    win_cols = [f"n_{side}{t}" for t in ts for side in ("pre", "post", "both")]
    d = d[d[win_cols].max(axis=1) >= floor]
    d = d.sort_values(["n_wear", "n_dx"], ascending=False)
    if top:
        d = d.head(int(top))
    L += ["", f"## By disease (any kind of data; every mapped disease with a window count "
          f">= {floor}{f'; top {top}' if top else ''})",
          "", f"| Mondo | disease | n_dx | with data | ≥1 day before | ≥1 day after | "
          f"{win_head}days before | days after |",
          f"|---|---|--:|--:|--:|--:|{win_align}--:|--:|"]
    for _, r in d.iterrows():
        L.append(f"| {r['mondo_id']} | {str(names.get(r['mondo_id'], r['mondo_id']))[:44]} | "
                 f"{cell(r['n_dx'], floor)} | {cell(r['n_wear'], floor)} | "
                 f"{cell(r['n_before'], floor)} | {cell(r['n_after'], floor)} | "
                 f"{win_cells(r)}{_iqr(r, 'before')} | {_iqr(r, 'after')} |")

    kinds = [k for k in prof["src"].unique() if k != ANY]
    L += ["", "## By disease and kind: persons with ≥1 day before / after the first "
          "diagnosis", "", "| disease | " + " | ".join(kinds) + " |",
          "|---|" + "--:|" * len(kinds)]
    for m in [ALL] + list(d["mondo_id"]):
        g = prof[prof["mondo_id"] == m].set_index("src")
        label = "all selected diseases" if m == ALL else names.get(m, m)
        L.append(f"| {str(label)[:44]} | " + " | ".join(
            f"{cell(g.loc[k, 'n_before'], floor)} / {cell(g.loc[k, 'n_after'], floor)}"
            for k in kinds) + " |")
    return "\n".join(L) + "\n"


def _slug(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", str(s).lower()).strip("-")


def run_name(roots, names: dict, flags, *, exact=False, descendants=True,
             min_dx_dates=1) -> str:
    """Short readable run name: the Mondo root labels (or 'all-rare'), then only the
    options that differ from the usual ones, e.g. 'autoimmune-disease_exact'."""
    parts = ["+".join(_slug(names.get(r, r)) for r in roots) or "all-rare"]
    if set(flags) != STANDARD_FLAGS:
        parts.append("-".join(f.replace("_rare", "") or "rare" for f in flags))
    parts += (["exact"] if exact else []) + ([] if descendants else ["nodesc"])
    parts += [f"dx{min_dx_dates}"] if min_dx_dates > 1 else []
    return "_".join(parts)


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    p.add_argument("--out-dir", required=True)
    p.add_argument("--flags", default="rare",
                   help="comma list of Mondo rare subsets to include (any-of): "
                        + ", ".join(_SOURCE_FLAGS))
    p.add_argument("--under", default="",
                   help="comma list of Mondo ids: only rare nodes in these subtrees")
    p.add_argument("--exact", action="store_true",
                   help="map only via a node's own standard SNOMED Condition xref")
    p.add_argument("--no-descendants", action="store_true",
                   help="count the mapped standard concept only, not its OMOP subtree")
    p.add_argument("--min-dx-dates", type=int, default=1)
    p.add_argument("--window-days", type=int, default=365,
                   help="window before / after the first diagnosis for n_pre/post/both")
    p.add_argument("--window-thresholds", default="7,30",
                   help="comma list: days of data in the window needed to count")
    p.add_argument("--no-intraday", action="store_true",
                   help="skip the (large) intraday tables")
    p.add_argument("--top", type=int, default=0,
                   help="cap the per-disease table at this many rows (0 = no cap)")
    p.add_argument("--mondo-version", default="2026-06-02")
    p.add_argument("--mondo-cache-dir", default="data/mondo")
    p.add_argument("--tag", default="", help="run name (default: built by run_name)")
    p.add_argument("--patient-plots", default="",
                   help="comma list of kinds (e.g. any,heart_rate_minute_level): also draw "
                        "participant-level faceted dot plots (<run>_DO_NOT_EGRESS_*.png; "
                        "Workbench only, never egress)")
    p.add_argument("--patient-facets", type=int, default=20,
                   help="diseases per participant-level plot (largest first, plus ALL)")
    args = p.parse_args(argv)
    cdr, billing = workspace_env()
    flags = [f.strip() for f in args.flags.split(",") if f.strip()]
    bad = [f for f in flags if f not in _SOURCE_FLAGS]
    if bad:
        raise SystemExit(f"unknown --flags {bad}; known: {_SOURCE_FLAGS}")
    out = Path(args.out_dir) / cdr.split(".")[-1]
    out.mkdir(parents=True, exist_ok=True)
    client = bq_client(billing)

    roots = [r.strip() for r in args.under.split(",") if r.strip()]
    rm = build_rare_map(client, cdr, flags=flags, roots=roots, exact=args.exact,
                        mondo_version=args.mondo_version,
                        cache_dir=Path(args.mondo_cache_dir))
    rmap, names = rm.rmap, rm.names

    cols = query(client, f"""
SELECT table_name, column_name FROM `{cdr}.INFORMATION_SCHEMA.COLUMNS`
WHERE table_name IN UNNEST(@tables)""",
                 {"tables": ("STRING", [t for t, _, _ in _TIMING_TABLES])})
    wear_sql, found = typed_wear_sql(
        cdr, cols.groupby("table_name")["column_name"].apply(set).to_dict(),
        intraday=not args.no_intraday)
    ctes = timing_ctes(cdr, wear_sql, descendants=not args.no_descendants)
    params = {"mondo": ("STRING", rmap["mondo_id"].tolist()),
              "cid": ("INT64", [int(c) for c in rmap["standard_concept_id"]]),
              "min_dx_dates": ("INT64", int(args.min_dx_dates))}
    print("[timing] diagnosis counts query…", flush=True)
    n_dx = query(client, ctes + N_DX_SELECT, params)
    print("[timing] per-person timing query…", flush=True)
    per = query(client, ctes + PER_PERSON_SELECT,
                {**params, "win_days": ("INT64", int(args.window_days))})
    ts = tuple(int(t) for t in args.window_thresholds.split(",") if t.strip())
    prof = profile(per, n_dx, thresholds=ts)

    meta = {"cdr": cdr, "wear_tables": found, "flags": flags, "under": roots,
            "exact": args.exact, "descendants": not args.no_descendants,
            "min_dx_dates": args.min_dx_dates, "window_days": args.window_days,
            "window_thresholds": list(ts),
            "n_rare_nodes": int(rmap["mondo_id"].nunique())}
    text = format_report(prof, names, meta, top=args.top)
    tag = args.tag or run_name(roots, names, flags, exact=args.exact,
                               descendants=not args.no_descendants,
                               min_dx_dates=args.min_dx_dates)
    meta["run"] = tag
    (out / f"{tag}_report.md").write_text(text)
    masked(prof, names).to_csv(out / f"{tag}_table.tsv", sep="\t", index=False)
    rm.review.to_csv(out / f"{tag}_mapping.tsv", sep="\t", index=False)
    (out / f"{tag}_run.json").write_text(json.dumps(meta, indent=1, default=str))
    try:  # plots are drawn from the masked report text only
        from audits.wearables_timing_plots import write_plots
        for path in write_plots(text, out, prefix=f"{tag}_plot-"):
            print(f"[timing] plot {path}", flush=True)
    except ImportError as e:
        print(f"[timing] no plots ({e}); install matplotlib or run "
              "`make plot-wearables-timing REPORT=...` locally", flush=True)
    if args.patient_plots:
        from audits.wearables_timing_plots import write_patient_plots
        kinds = [k.strip() for k in args.patient_plots.split(",") if k.strip()]
        for path in write_patient_plots(per, names, out, prefix=f"{tag}_DO_NOT_EGRESS_",
                                        kinds=kinds, max_facets=args.patient_facets,
                                        all_id=ALL, thresholds=ts):
            print(f"[timing] PARTICIPANT-LEVEL plot (do not egress) {path}", flush=True)
    print(text, flush=True)
    print(f"[timing] wrote {out}/{tag}_report.md, _table.tsv, _run.json (cells 1-19 as "
          f"<20; quartiles only where >= {EGRESS_FLOOR} persons)", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
