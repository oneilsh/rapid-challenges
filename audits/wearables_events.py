"""WEARABLES x ACUTE CARE EVENTS: is there enough data for "predict an ED / inpatient
visit in the next N days from the preceding Fitbit data"?

Diseases are chosen and mapped as in `wearables_timing` (`build_rare_map`, `--under`,
`--exact`, `--min-dx-dates`; `ALL` pools them, first dx = earliest among them). The
cohort is persons with a selected diagnosis AND at least one Fitbit daily-summary day.

EVENTS = distinct (person, date) with an ED or inpatient visit start in
visit_occurrence: visit concepts under 9203 Emergency Room Visit, 9201 Inpatient Visit
or 262 Emergency Room and Inpatient Visit (OMOP `concept_ancestor`). Classes:
  ed_or_inpatient   any of them
  ed / inpatient    ED (9203 or 262) / inpatient (9201 or 262)
  related           ED or inpatient, with the disease (any selected disease for ALL)
                    coded on that visit or that day
An event is AFTER the first dx when it is strictly later (the dx day itself is often the
diagnosing visit, so it is neither before nor after), BEFORE when strictly earlier. It
is COVERED when the person has >= --min-cov Fitbit days in the --lookback days before it
(the input window a model would see).

Per (disease, class), over the cohort:
  n_wear            persons with the disease and Fitbit data
  wear_days_after   their Fitbit days after the first dx (exposure)
  n_ev / n_ev_p     events after dx / persons with one
  n_cov / n_cov_p   covered events after dx / persons with one
  n_cov_p2          persons with >= 2 covered events after dx (repeat events)
  cov_per_1k        covered events per 1,000 Fitbit days after dx (only where n_cov >= 20)
  n_cov_pre / n_cov_pre_p
                    covered events before dx / persons with one
plus the visit types present for the cohort, and covered-ness of the pooled events.

EGRESS: every count through `cell`; the rate only where the count behind it is >= 20.
Columns are nested (n_ev >= n_cov, ed_or_inpatient >= each class): check differences
before sharing beyond the Workbench team. Person ids stay in BigQuery: rows come back
keyed by a per-run rank, and nothing person-level is written.

OUTPUT: `<out-dir>/<CDR dataset>/<run>_events-report.md`, `_events-table.tsv`,
`_visit-types.tsv`, `_events-run.json`.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import pandas as pd

from audits.wearables_rare import _SOURCE_FLAGS, build_rare_map
from audits.wearables_timing import (ALL, N_DX_SELECT, run_name, timing_ctes,
                                     typed_wear_sql, _TIMING_TABLES)
from rapidaudit.aou import bq_client, query, workspace_env
from rapidaudit.egress import EGRESS_FLOOR, cell, mask_counts

ED, INPATIENT, ED_AND_INPATIENT = 9203, 9201, 262
CLASSES = ("ed_or_inpatient", "ed", "inpatient", "related")
COV_BINS = (0, 1, 7, 14, 21)   # lower edges of covered-days bins in the lookback


def events_ctes() -> str:
    """Appended to `timing_ctes(...)` (daily summaries only). Extra params: none.
    `wdays` = (person, Fitbit day); `wp` = cohort persons with Fitbit data; `pids` = a
    per-run rank standing in for person_id; `ev` = (person, disease, first_dx, event
    date) with ED / inpatient / related flags."""
    return f""",
wdays AS (SELECT DISTINCT person_id, d FROM wear_days),
wp AS (SELECT DISTINCT person_id FROM wdays),
pids AS (SELECT person_id, DENSE_RANK() OVER (ORDER BY person_id) AS pid FROM wp),
vt AS (
  SELECT descendant_concept_id AS cid,
         LOGICAL_OR(ancestor_concept_id IN ({ED}, {ED_AND_INPATIENT})) AS is_ed,
         LOGICAL_OR(ancestor_concept_id IN ({INPATIENT}, {ED_AND_INPATIENT})) AS is_ip
  FROM `{{cdr}}.concept_ancestor`
  WHERE ancestor_concept_id IN ({ED}, {INPATIENT}, {ED_AND_INPATIENT})
  GROUP BY descendant_concept_id),
vis AS (
  SELECT v.person_id, v.visit_occurrence_id, CAST(v.visit_start_date AS DATE) AS vd,
         vt.is_ed, vt.is_ip
  FROM `{{cdr}}.visit_occurrence` v
  JOIN vt ON v.visit_concept_id = vt.cid
  JOIN wp ON v.person_id = wp.person_id),
dxc AS (
  SELECT co.person_id, nc.mondo_id, co.visit_occurrence_id,
         CAST(co.condition_start_date AS DATE) AS cd
  FROM `{{cdr}}.condition_occurrence` co
  JOIN node_concepts nc ON co.condition_concept_id = nc.cid
  JOIN wp ON co.person_id = wp.person_id),
dxc_all AS (
  SELECT person_id, mondo_id, visit_occurrence_id, cd FROM dxc
  UNION ALL
  SELECT person_id, '{ALL}' AS mondo_id, visit_occurrence_id, cd FROM dxc),
ev AS (
  SELECT x.person_id, x.mondo_id, x.first_dx, v.vd,
         LOGICAL_OR(v.is_ed) AS is_ed, LOGICAL_OR(v.is_ip) AS is_ip,
         LOGICAL_OR(r.person_id IS NOT NULL) AS related
  FROM dx_all x
  JOIN vis v ON v.person_id = x.person_id
  LEFT JOIN dxc_all r ON r.person_id = v.person_id AND r.mondo_id = x.mondo_id
    AND (r.visit_occurrence_id = v.visit_occurrence_id OR r.cd = v.vd)
  GROUP BY x.person_id, x.mondo_id, x.first_dx, v.vd)
"""


# One row per (person, disease, event date). Extra param: @lookback INT64.
EVENTS_SELECT = """
SELECT p.pid, e.mondo_id, DATE_DIFF(e.vd, e.first_dx, DAY) AS rel_day,
       e.is_ed, e.is_ip, e.related, COUNT(w.d) AS cov_days
FROM ev e
JOIN pids p ON p.person_id = e.person_id
LEFT JOIN wdays w ON w.person_id = e.person_id
  AND w.d >= DATE_SUB(e.vd, INTERVAL @lookback DAY) AND w.d < e.vd
GROUP BY p.pid, e.mondo_id, e.vd, e.first_dx, e.is_ed, e.is_ip, e.related
"""

# One row per (person, disease): Fitbit days before / after the first dx.
EXPOSURE_SELECT = """
SELECT p.pid, x.mondo_id, COUNTIF(w.d < x.first_dx) AS wd_before,
       COUNTIF(w.d > x.first_dx) AS wd_after
FROM dx_all x
JOIN wdays w ON w.person_id = x.person_id
JOIN pids p ON p.person_id = x.person_id
GROUP BY p.pid, x.mondo_id
"""

VISIT_TYPES_SELECT = """
SELECT v.visit_concept_id, c.concept_name, COUNT(*) AS n_visits,
       COUNT(DISTINCT v.person_id) AS n_persons
FROM `{cdr}.visit_occurrence` v
JOIN wp ON v.person_id = wp.person_id
LEFT JOIN `{cdr}.concept` c ON c.concept_id = v.visit_concept_id
GROUP BY v.visit_concept_id, c.concept_name
ORDER BY n_visits DESC
"""


def event_class_mask(ev: pd.DataFrame, cls: str) -> pd.Series:
    if cls == "ed":
        return ev["is_ed"].astype(bool)
    if cls == "inpatient":
        return ev["is_ip"].astype(bool)
    acute = ev["is_ed"].astype(bool) | ev["is_ip"].astype(bool)
    return acute & ev["related"].astype(bool) if cls == "related" else acute


def summarize(ev: pd.DataFrame, expo: pd.DataFrame, n_dx: pd.DataFrame, *,
              min_cov: int, floor: int = EGRESS_FLOOR) -> pd.DataFrame:
    """Raw (unmasked) per-(disease, class) counts; see the module docstring. Diseases
    come in `n_dx` order, ALL first."""
    order = [ALL] + [m for m in n_dx["mondo_id"] if m != ALL]
    ndx = dict(zip(n_dx["mondo_id"], n_dx["n_dx"]))
    rows = []
    for m in order:
        x = expo[expo["mondo_id"] == m]
        e_m = ev[ev["mondo_id"] == m]
        for cls in CLASSES:
            e = e_m[event_class_mask(e_m, cls)]
            after, before = e[e["rel_day"] > 0], e[e["rel_day"] < 0]
            cov = after[after["cov_days"] >= min_cov]
            cov_pre = before[before["cov_days"] >= min_cov]
            per_p = cov.groupby("pid").size()
            wda = int(x["wd_after"].sum())
            rows.append({
                "mondo_id": m, "event_class": cls, "n_dx": int(ndx.get(m, 0)),
                "n_wear": int(x["pid"].nunique()), "wear_days_after": wda,
                "n_ev": len(after), "n_ev_p": int(after["pid"].nunique()),
                "n_cov": len(cov), "n_cov_p": int(cov["pid"].nunique()),
                "n_cov_p2": int((per_p >= 2).sum()),
                "cov_per_1k": (round(1000 * len(cov) / wda, 2)
                               if len(cov) >= floor and wda else None),
                "n_cov_pre": len(cov_pre), "n_cov_pre_p": int(cov_pre["pid"].nunique())})
    return pd.DataFrame(rows)


def coverage_bins(ev: pd.DataFrame, cls: str, edges=COV_BINS) -> dict:
    """Pooled (ALL) events after dx of class `cls`, by Fitbit days in the lookback."""
    e = ev[(ev["mondo_id"] == ALL) & (ev["rel_day"] > 0)]
    e = e[event_class_mask(e, cls)]
    hi = list(edges[1:]) + [float("inf")]
    labs = ["0" if lo == 0 and h == 1 else (f"{lo}+" if h == float("inf") else f"{lo}-{h - 1}")
            for lo, h in zip(edges, hi)]
    return {lab: int(((e["cov_days"] >= lo) & (e["cov_days"] < h)).sum())
            for lab, lo, h in zip(labs, edges, hi)}


COUNT_COLS = ["n_dx", "n_wear", "n_ev", "n_ev_p", "n_cov", "n_cov_p", "n_cov_p2",
              "n_cov_pre", "n_cov_pre_p"]


def masked_table(summ: pd.DataFrame, names: dict, floor: int = EGRESS_FLOOR) -> pd.DataFrame:
    out = mask_counts(summ, COUNT_COLS, floor)
    out["cov_per_1k"] = summ["cov_per_1k"].map(lambda v: "" if v is None or pd.isna(v)
                                                else f"{v:.2f}")
    out.insert(1, "name", out["mondo_id"].map(
        lambda m: "all selected diseases" if m == ALL else names.get(m, m)))
    return out


def _row(r, floor) -> str:
    rate = "—" if r["cov_per_1k"] is None or pd.isna(r["cov_per_1k"]) else f"{r['cov_per_1k']:.2f}"
    return (f"{cell(r['n_ev'], floor)} | {cell(r['n_ev_p'], floor)} | "
            f"{cell(r['n_cov'], floor)} | {cell(r['n_cov_p'], floor)} | "
            f"{cell(r['n_cov_p2'], floor)} | {rate} | {cell(r['n_cov_pre'], floor)} | "
            f"{cell(r['n_cov_pre_p'], floor)} |")


EVENT_HEAD = ("events after dx | persons | covered events | persons | persons with ≥2 | "
              "covered per 1k wear-days | covered events before dx | persons |")


def format_report(summ: pd.DataFrame, vtypes: pd.DataFrame, cov: dict, names: dict,
                  meta: dict, *, floor: int = EGRESS_FLOOR, top_visit_types: int = 15) -> str:
    lb, mc = meta["lookback"], meta["min_cov"]
    L = ["# Wearables x ED / inpatient events (All of Us)", "",
         f"CDR: `{meta['cdr']}`", "",
         f"Fitbit tables: {', '.join(meta['wear_tables'])} · rare = Mondo subsets "
         f"{', '.join(meta['flags'])} · {meta['n_rare_nodes']:,} diseases mapped", ""]
    scope = [f"under {', '.join(meta['under'])}" if meta.get("under") else "",
             "exact SNOMED-only mapping" if meta.get("exact") else "",
             f"dx on >= {meta['min_dx_dates']} distinct dates"
             if meta.get("min_dx_dates", 1) > 1 else ""]
    if any(scope):
        L += ["Scope: " + " · ".join(x for x in scope if x), ""]
    L += ["Event = a distinct (person, date) with an ED or inpatient visit start. After / "
          "before = strictly after / before the first diagnosis (the dx day itself is "
          f"excluded). Covered = >= {mc} Fitbit days in the {lb} days before the event. "
          "Related = the disease coded on that visit or day. Cohort = persons with the "
          "disease and any Fitbit day. Columns are nested: check differences before "
          "sharing.", ""]

    a = summ[summ["mondo_id"] == ALL]
    if len(a):
        r0 = a.iloc[0]
        L += ["## All selected diseases", "",
              f"Persons with a selected diagnosis: {cell(r0['n_dx'], floor)} · with Fitbit "
              f"data: {cell(r0['n_wear'], floor)} · their Fitbit days after dx: "
              f"{int(r0['wear_days_after']):,}", "",
              f"| event class | {EVENT_HEAD}", "|---|" + "--:|" * 8]
        for _, r in a.iterrows():
            L.append(f"| {r['event_class']} | {_row(r, floor)}")
    if cov:
        L += ["", f"Pooled events after dx by Fitbit days in the {lb} days before them:", "",
              "| event class | " + " | ".join(next(iter(cov.values()))) + " |",
              "|---|" + "--:|" * len(next(iter(cov.values())))]
        for cls, bins in cov.items():
            L.append(f"| {cls} | " + " | ".join(cell(v, floor) for v in bins.values()) + " |")

    d = summ[(summ["mondo_id"] != ALL) & (summ["n_wear"] >= floor)]
    show = d[d["event_class"] == "ed_or_inpatient"].sort_values("n_wear", ascending=False)
    L += ["", f"## By disease (persons with Fitbit data >= {floor})", ""]
    for cls in ("ed_or_inpatient", "related"):
        L += [f"### {cls}", "", f"| Mondo | disease | with data | {EVENT_HEAD}",
              "|---|---|--:|" + "--:|" * 8]
        for m in show["mondo_id"]:
            r = d[(d["mondo_id"] == m) & (d["event_class"] == cls)].iloc[0]
            L.append(f"| {m} | {str(names.get(m, m))[:44]} | {cell(r['n_wear'], floor)} | "
                     f"{_row(r, floor)}")
        L.append("")

    L += [f"## Visit types for the cohort (top {top_visit_types} by visits)", "",
          "| visit concept | name | visits | persons |", "|--:|---|--:|--:|"]
    for _, r in vtypes.head(top_visit_types).iterrows():
        L.append(f"| {r['visit_concept_id']} | {r['concept_name']} | "
                 f"{cell(r['n_visits'], floor)} | {cell(r['n_persons'], floor)} |")
    return "\n".join(L) + "\n"


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    p.add_argument("--out-dir", required=True)
    p.add_argument("--flags", default="rare",
                   help="comma list of Mondo rare subsets (any-of): " + ", ".join(_SOURCE_FLAGS))
    p.add_argument("--under", default="")
    p.add_argument("--exact", action="store_true")
    p.add_argument("--no-descendants", action="store_true")
    p.add_argument("--min-dx-dates", type=int, default=1)
    p.add_argument("--lookback", type=int, default=30,
                   help="days before an event that a model would see")
    p.add_argument("--min-cov", type=int, default=14,
                   help="Fitbit days in the lookback for an event to count as covered")
    p.add_argument("--mondo-version", default="2026-06-02")
    p.add_argument("--mondo-cache-dir", default="data/mondo")
    p.add_argument("--tag", default="", help="run name (default: built by run_name)")
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
        cdr, cols.groupby("table_name")["column_name"].apply(set).to_dict(), intraday=False)
    ctes = (timing_ctes(cdr, wear_sql, descendants=not args.no_descendants)
            + events_ctes().replace("{cdr}", cdr))
    params = {"mondo": ("STRING", rmap["mondo_id"].tolist()),
              "cid": ("INT64", [int(c) for c in rmap["standard_concept_id"]]),
              "min_dx_dates": ("INT64", int(args.min_dx_dates))}
    print("[events] diagnosis counts query…", flush=True)
    n_dx = query(client, ctes + N_DX_SELECT, params)
    print("[events] exposure query…", flush=True)
    expo = query(client, ctes + EXPOSURE_SELECT, params)
    print("[events] events query…", flush=True)
    ev = query(client, ctes + EVENTS_SELECT,
               {**params, "lookback": ("INT64", int(args.lookback))})
    print("[events] visit types query…", flush=True)
    vtypes = query(client, ctes + VISIT_TYPES_SELECT.format(cdr=cdr), params)

    summ = summarize(ev, expo, n_dx, min_cov=args.min_cov)
    cov = {cls: coverage_bins(ev, cls) for cls in ("ed_or_inpatient", "related")}
    meta = {"cdr": cdr, "wear_tables": found, "flags": flags, "under": roots,
            "exact": args.exact, "descendants": not args.no_descendants,
            "min_dx_dates": args.min_dx_dates, "lookback": args.lookback,
            "min_cov": args.min_cov, "n_rare_nodes": int(rmap["mondo_id"].nunique())}
    tag = args.tag or run_name(roots, names, flags, exact=args.exact,
                               descendants=not args.no_descendants,
                               min_dx_dates=args.min_dx_dates)
    meta["run"] = tag
    text = format_report(summ, vtypes, cov, names, meta)
    (out / f"{tag}_events-report.md").write_text(text)
    masked_table(summ, names).to_csv(out / f"{tag}_events-table.tsv", sep="\t", index=False)
    mask_counts(vtypes, ["n_visits", "n_persons"]).to_csv(
        out / f"{tag}_visit-types.tsv", sep="\t", index=False)
    (out / f"{tag}_events-run.json").write_text(json.dumps(meta, indent=1, default=str))
    print(text, flush=True)
    print(f"[events] wrote {out}/{tag}_events-report.md, _events-table.tsv, "
          f"_visit-types.tsv (cells 1-19 as <20)", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
