"""APPLE HEALTHKIT coverage next to Fitbit (RAPID TA1 wearables tab).

"How much Apple HealthKit data is there, for whom, and how many ED / inpatient episodes
would it cover that Fitbit doesn't?"

AoU published HealthKit (Sep 2026, a CDR v9 off-cycle release) as a STAND-ALONE BigQuery
dataset next to the CDR, joined by participant id. Its table names were not known when
this was written, so the audit discovers them:

  DATASET   --hk-dataset <project>.<dataset>, else the BigQuery datasets in `wb resource
            list` and in the CDR's project whose name looks like HealthKit (health /
            apple / hk), else CDR tables whose name does. With several candidates it lists
            them and stops; rerun with --hk-dataset.
  TABLES    each table with a person column (`person_id`, else a name with person /
            participant) and a DATE / DATETIME / TIMESTAMP column (preferring `date`, then
            names with date, then start) counts as one KIND of HealthKit data, a day being
            a day with >= 1 row. Tables over --max-gb (BigQuery's own size) are skipped
            unless named in --hk-tables; --hk-date-cols table=col overrides the pick.

Sections of the report:
  1. dataset, tables (rows, GB, picked columns or why skipped) and every column's type
     (metadata only; also in `_hk-schema.tsv`)
  2. all participants: persons per HealthKit table, how many of them are in the CDR's
     `person` table, persons per year of data, and persons with Fitbit / HealthKit / both
  3. device-like STRING columns (tables or columns named device / source / product /
     model): only values held by >= 20 persons, the rest pooled as "(other)" (HealthKit
     source names can carry a person's name, e.g. "Jane's iPhone")
  4. the cohort (same disease selection as wearables_events): persons with Fitbit,
     HealthKit, both, HealthKit only; their days after the first dx by source
  5. ED / inpatient EPISODES after the first dx (wearables_events rules: --washout,
     --ip-overnight), COVERED when >= --min-cov days in the --lookback days before by
     Fitbit, by HealthKit, by either, and by HealthKit only (covered with either, not with
     Fitbit alone); pooled (ALL) by class, then by disease for ED or inpatient

EGRESS: every participant count goes through `cell` (1..19 -> "<20"). The columns are
NESTED (either >= Fitbit, either >= HealthKit; "HealthKit only" is computed from the raw
counts and masked itself); do not subtract published cells. Row counts and GB are table
metadata, not participant counts. Nothing person-level is written.

OUTPUT: `<out-dir>/<CDR dataset>/<run>_hk-report.md`, `_hk-schema.tsv`,
`_hk-cohort.tsv`, `_hk-events.tsv`, `_hk-run.json`.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

import pandas as pd

from audits.wearables_events import CLASSES, event_class_mask, events_ctes
from audits.wearables_rare import _SOURCE_FLAGS, build_rare_map
from audits.wearables_timing import (ALL, N_DX_SELECT, run_name, timing_ctes,
                                     typed_wear_sql, _TIMING_TABLES)
from rapidaudit.aou import bq_client, query, workspace_env
from rapidaudit.egress import EGRESS_FLOOR, cell, mask_counts

HK_NAME = re.compile(r"health|apple|(^|[_\W])hk([_\W]|$)", re.I)
DEVICE_NAME = re.compile(r"device|source|product|model|hardware", re.I)
DATE_TYPES = ("DATE", "DATETIME", "TIMESTAMP")
HK = "hk_"        # src prefix of HealthKit kinds in `wear_days` (Fitbit kinds have none)


# ---------------------------------------------------------------- discovery (pure parts)

def hk_candidates(datasets: list[str], cdr: str, cdr_tables: list[str]) -> list[str]:
    """Candidate HealthKit locations: '<project>.<dataset>' names that look like
    HealthKit (not the CDR itself), else 'CDR:<table>' entries for CDR tables that do."""
    seen, out = set(), []
    for d in datasets:
        if d != cdr and d not in seen and HK_NAME.search(d.split(".")[-1]):
            seen.add(d)
            out.append(d)
    if not out:
        out = [f"CDR:{t}" for t in cdr_tables if HK_NAME.search(t)]
    return out


def pick_columns(schema: pd.DataFrame, overrides: dict | None = None) -> pd.DataFrame:
    """One row per table: person column, date column (or None) and `why` when unusable.
    `schema` has table_name, column_name, data_type."""
    overrides = overrides or {}
    rows = []
    for t, g in schema.groupby("table_name", sort=True):
        cols = dict(zip(g["column_name"], g["data_type"].str.upper()))
        pc = ("person_id" if "person_id" in cols else
              next((c for c in cols if re.search(r"person|participant", c, re.I)), None))
        dates = [c for c, ty in cols.items() if ty.split("(")[0] in DATE_TYPES]
        dc = overrides.get(t)
        if dc is None and dates:
            dc = next((c for c in dates if c.lower() == "date"), None) \
                or next((c for c in dates if "date" in c.lower()), None) \
                or next((c for c in dates if "start" in c.lower()), None) or dates[0]
        why = ("no person column" if pc is None else
               "no date column" if dc is None else
               f"date column {dc!r} not in table" if dc not in cols else "")
        rows.append({"table_name": t, "person_col": pc, "date_col": dc,
                     "person_type": cols.get(pc), "why": why})
    return pd.DataFrame(rows, columns=["table_name", "person_col", "date_col",
                                       "person_type", "why"])


def hk_wear_sql(hk: str, picks: pd.DataFrame, cohort: bool = True) -> str:
    """UNION ALL of (person_id, src, d) over usable HealthKit tables, src = 'hk_<table>';
    restricted to the `cohort` CTE when `cohort`."""
    parts = []
    for r in picks[picks["why"] == ""].itertuples():
        pid = (f"t.{r.person_col}" if str(r.person_type).upper() == "INT64"
               else f"SAFE_CAST(t.{r.person_col} AS INT64)")
        join = f" JOIN cohort c ON {pid} = c.person_id" if cohort else ""
        parts.append(f"SELECT {pid} AS person_id, '{HK}{r.table_name}' AS src, "
                     f"CAST(t.{r.date_col} AS DATE) AS d FROM `{hk}.{r.table_name}` t{join}")
    if not parts:
        raise SystemExit("[healthkit] no usable HealthKit table (see the schema above)")
    return "\n    UNION ALL\n    ".join(parts)


# ---------------------------------------------------------------- queries

# Whole dataset (all participants), on `all_days` = (person_id, src, d) over HealthKit
# and the Fitbit daily summaries (src without the hk_ prefix).
ALL_PERSONS_SELECT = """
SELECT src, COUNT(DISTINCT person_id) AS n_persons,
       COUNT(DISTINCT IF(in_cdr, person_id, NULL)) AS n_in_cdr
FROM (SELECT a.person_id, a.src, p.person_id IS NOT NULL AS in_cdr
      FROM (SELECT DISTINCT person_id, src FROM all_days) a
      LEFT JOIN `{cdr}.person` p ON p.person_id = a.person_id)
WHERE STARTS_WITH(src, 'hk_')
GROUP BY src
UNION ALL
SELECT 'any HealthKit', COUNT(DISTINCT person_id), COUNT(DISTINCT IF(in_cdr, person_id, NULL))
FROM (SELECT a.person_id, p.person_id IS NOT NULL AS in_cdr
      FROM (SELECT DISTINCT person_id FROM all_days WHERE STARTS_WITH(src, 'hk_')) a
      LEFT JOIN `{cdr}.person` p ON p.person_id = a.person_id)
"""

ALL_YEARS_SELECT = """
SELECT IF(STARTS_WITH(src, 'hk_'), 'HealthKit', 'Fitbit') AS source,
       EXTRACT(YEAR FROM d) AS year, COUNT(DISTINCT person_id) AS n_persons
FROM all_days WHERE d IS NOT NULL GROUP BY 1, 2 ORDER BY 1, 2
"""

ALL_OVERLAP_SELECT = """
SELECT LOGICAL_OR(NOT STARTS_WITH(src, 'hk_')) AS has_fitbit,
       LOGICAL_OR(STARTS_WITH(src, 'hk_')) AS has_hk
FROM (SELECT DISTINCT person_id, src FROM all_days) GROUP BY person_id
"""

# Persons per value of one STRING column; format with hk, table, col, pcol.
DEVICE_VALUES_SELECT = """
SELECT CAST(t.{col} AS STRING) AS value, COUNT(DISTINCT t.{pcol}) AS n_persons
FROM `{hk}.{table}` t GROUP BY 1 ORDER BY n_persons DESC LIMIT 200
"""

# One row per (person, disease): days by source, all and after the first dx.
COHORT_SELECT = """
SELECT x.mondo_id,
  COUNT(DISTINCT IF(NOT STARTS_WITH(w.src, 'hk_'), w.d, NULL)) AS fb_days,
  COUNT(DISTINCT IF(STARTS_WITH(w.src, 'hk_'), w.d, NULL)) AS hk_days,
  COUNT(DISTINCT IF(NOT STARTS_WITH(w.src, 'hk_') AND w.d > x.first_dx, w.d, NULL))
    AS fb_after,
  COUNT(DISTINCT IF(STARTS_WITH(w.src, 'hk_') AND w.d > x.first_dx, w.d, NULL)) AS hk_after,
  COUNT(DISTINCT IF(w.d > x.first_dx, w.d, NULL)) AS any_after
FROM dx_all x JOIN wear_days w USING (person_id)
GROUP BY x.person_id, x.mondo_id
"""

# One row per (person, disease, episode): covered days in the lookback by source.
# Extra param: @lookback INT64.
HK_EVENTS_SELECT = """
SELECT p.pid, e.mondo_id, DATE_DIFF(e.vd, e.first_dx, DAY) AS rel_day, e.is_ed, e.is_ip,
  COUNT(DISTINCT IF(NOT STARTS_WITH(w.src, 'hk_'), w.d, NULL)) AS cov_fb,
  COUNT(DISTINCT IF(STARTS_WITH(w.src, 'hk_'), w.d, NULL)) AS cov_hk,
  COUNT(DISTINCT w.d) AS cov_any
FROM ev e
JOIN pids p ON p.person_id = e.person_id
LEFT JOIN wear_days w ON w.person_id = e.person_id
  AND w.d >= DATE_SUB(e.vd, INTERVAL @lookback DAY) AND w.d < e.vd
GROUP BY p.pid, e.mondo_id, e.vd, e.first_dx, e.is_ed, e.is_ip
"""


# ---------------------------------------------------------------- summaries (raw counts)

def cohort_summary(per: pd.DataFrame, n_dx: pd.DataFrame) -> pd.DataFrame:
    """Per disease (ALL first): persons with the dx, with Fitbit / HealthKit / both /
    HealthKit only, and their days after the first dx by source."""
    order = [ALL] + [m for m in n_dx["mondo_id"] if m != ALL]
    ndx = dict(zip(n_dx["mondo_id"], n_dx["n_dx"]))
    rows = []
    for m in order:
        x = per[per["mondo_id"] == m]
        fb, hk = x["fb_days"] > 0, x["hk_days"] > 0
        rows.append({"mondo_id": m, "n_dx": int(ndx.get(m, 0)),
                     "n_fitbit": int(fb.sum()), "n_hk": int(hk.sum()),
                     "n_both": int((fb & hk).sum()), "n_hk_only": int((hk & ~fb).sum()),
                     "n_hk_after": int((x["hk_after"] > 0).sum()),
                     "fb_days_after": int(x["fb_after"].sum()),
                     "hk_days_after": int(x["hk_after"].sum()),
                     "any_days_after": int(x["any_after"].sum())})
    return pd.DataFrame(rows)


def events_summary(ev: pd.DataFrame, *, min_cov: int, by_disease: bool = False
                   ) -> pd.DataFrame:
    """Episodes after the first dx (rel_day > 0) covered by Fitbit / HealthKit / either /
    HealthKit only, with persons. ALL by class, or (by_disease) every disease for the
    ed_or_inpatient class."""
    keys = ([(m, "ed_or_inpatient") for m in ev["mondo_id"].unique()] if by_disease
            else [(ALL, c) for c in CLASSES])
    rows = []
    for m, cls in keys:
        e = ev[(ev["mondo_id"] == m) & (ev["rel_day"] > 0)]
        e = e[event_class_mask(e, cls)]
        fb, hk, anyc = (e["cov_fb"] >= min_cov, e["cov_hk"] >= min_cov,
                        e["cov_any"] >= min_cov)
        only = anyc & ~fb
        row = {"mondo_id": m, "event_class": cls, "n_ev": len(e),
               "n_ev_p": int(e["pid"].nunique())}
        for k, sel in (("fb", fb), ("hk", hk), ("any", anyc), ("hk_only", only)):
            row[f"cov_{k}"] = int(sel.sum())
            row[f"cov_{k}_p"] = int(e.loc[sel, "pid"].nunique())
        rows.append(row)
    out = pd.DataFrame(rows)
    if by_disease and len(out):
        out = out.sort_values(["cov_any", "mondo_id"], ascending=[False, True])
    return out.reset_index(drop=True)


def device_values(vals: pd.DataFrame, floor: int = EGRESS_FLOOR) -> pd.DataFrame:
    """Keep values held by >= floor persons; pool the rest as '(other)' with how many
    values went in (the pooled person count is a sum, so it can double count)."""
    big = vals[vals["n_persons"] >= floor].copy()
    rest = vals[vals["n_persons"] < floor]
    if len(rest):
        big = pd.concat([big, pd.DataFrame(
            {"value": [f"(other: {cell(len(rest), floor)} values)"],
             "n_persons": [int(rest["n_persons"].sum())]})], ignore_index=True)
    big["value"] = big["value"].fillna("(null)")
    return big


# ---------------------------------------------------------------- report

def _t(header, rows) -> list[str]:
    return (["| " + " | ".join(header) + " |", "|" + "---|" * len(header)]
            + ["| " + " | ".join(str(c) for c in r) + " |" for r in rows])


def format_report(meta, tables, schema, persons, years, overlap, devices, coh, evs,
                  evd, names, floor: int = EGRESS_FLOOR) -> str:
    c = lambda n: cell(n, floor)  # noqa: E731
    L = [f"# Apple HealthKit next to Fitbit — {meta['run']}", "",
         f"CDR `{meta['cdr']}` · HealthKit `{meta['hk']}` (found by: {meta['hk_how']}) · "
         f"Fitbit daily summaries: {', '.join(meta['fitbit_tables'])}", "",
         "Counts are participants unless they say rows; 1-19 show as <20. Columns are "
         "nested (either >= each source): don't subtract published cells.", "",
         "## 1. Tables", ""]
    L += _t(["table", "rows", "GB", "person col", "date col", "used"],
            [(r.table_name, f"{int(r.row_count):,}" if pd.notna(r.row_count) else "",
              f"{r.gb:.1f}" if pd.notna(r.gb) else "", r.person_col or "",
              r.date_col or "", "yes" if r.used else f"no: {r.why}")
             for r in tables.itertuples()])
    L += ["", "<details><summary>Columns</summary>", ""]
    L += _t(["table", "column", "type"],
            [(r.table_name, r.column_name, r.data_type) for r in schema.itertuples()])
    L += ["", "</details>", "", "## 2. All participants", ""]
    L += _t(["HealthKit kind", "persons", "of those in the CDR person table"],
            [(r.src.removeprefix(HK), c(r.n_persons), c(r.n_in_cdr))
             for r in persons.itertuples()])
    fb, hk = overlap["has_fitbit"].astype(bool), overlap["has_hk"].astype(bool)
    L += ["", "Persons with Fitbit daily data / HealthKit data / both / HealthKit only: "
          f"{c(fb.sum())} / {c(hk.sum())} / {c((fb & hk).sum())} / {c((hk & ~fb).sum())}",
          "", "Persons with data by year:", ""]
    yrs = sorted(years["year"].dropna().astype(int).unique())
    piv = {(r.source, int(r.year)): r.n_persons for r in years.dropna().itertuples()}
    L += _t(["year", "Fitbit", "HealthKit"],
            [(y, c(piv.get(("Fitbit", y), 0)), c(piv.get(("HealthKit", y), 0)))
             for y in yrs])
    L += ["", "## 3. Device-like columns", ""]
    if not devices:
        L += ["None found."]
    for (t, col), d in devices.items():
        L += [f"`{t}.{col}` (values held by >= {floor} persons; the rest pooled):", ""]
        L += _t(["value", "persons"], [(r.value, c(r.n_persons)) for r in d.itertuples()])
        L += [""]
    a = coh.iloc[0]
    L += ["", f"## 4. Cohort ({meta['scope']})", "",
          f"Persons with a selected diagnosis: {c(a.n_dx)} · with Fitbit: {c(a.n_fitbit)} · "
          f"with HealthKit: {c(a.n_hk)} · both: {c(a.n_both)} · HealthKit only: "
          f"{c(a.n_hk_only)} · with HealthKit days after dx: {c(a.n_hk_after)}", "",
          f"Days after dx: Fitbit {int(a.fb_days_after):,} · HealthKit "
          f"{int(a.hk_days_after):,} · either {int(a.any_days_after):,}", "",
          f"By disease (persons with HealthKit >= {floor}):", ""]
    sub = coh[(coh["mondo_id"] != ALL) & (coh["n_hk"] >= floor)].sort_values(
        "n_hk", ascending=False)
    L += _t(["Mondo", "disease", "dx", "Fitbit", "HealthKit", "both", "HealthKit only"],
            [(r.mondo_id, names.get(r.mondo_id, ""), c(r.n_dx), c(r.n_fitbit), c(r.n_hk),
              c(r.n_both), c(r.n_hk_only)) for r in sub.itertuples()])
    L += ["", "## 5. Covered episodes after dx", "",
          f"Episode = ED / inpatient visit starts within {meta['washout']} days merged"
          + (", inpatient only with a stay (a row past its start day or consecutive "
             "inpatient days)" if meta["ip_overnight"] else "")
          + f"; covered = >= {meta['min_cov']} days of that source in the {meta['lookback']} "
          "days before. Episodes are counted among persons with any Fitbit or HealthKit "
          "day. Cells: episodes (persons).", ""]
    hdr = ["episodes", "Fitbit", "HealthKit", "either", "HealthKit only"]
    pc = lambda r, k: f"{c(getattr(r, f'cov_{k}'))} ({c(getattr(r, f'cov_{k}_p'))})"  # noqa: E731
    L += _t(["class"] + hdr,
            [(r.event_class, f"{c(r.n_ev)} ({c(r.n_ev_p)})", pc(r, "fb"), pc(r, "hk"),
              pc(r, "any"), pc(r, "hk_only")) for r in evs.itertuples()])
    L += ["", f"ED or inpatient by disease (either >= {floor}):", ""]
    sub = evd[(evd["mondo_id"] != ALL) & (evd["cov_any"] >= floor)]
    L += _t(["Mondo", "disease"] + hdr,
            [(r.mondo_id, names.get(r.mondo_id, ""), f"{c(r.n_ev)} ({c(r.n_ev_p)})",
              pc(r, "fb"), pc(r, "hk"), pc(r, "any"), pc(r, "hk_only"))
             for r in sub.itertuples()])
    return "\n".join(L) + "\n"


# ---------------------------------------------------------------- discovery (I/O)

def _wb_datasets() -> list[str]:
    try:
        p = subprocess.run(["wb", "resource", "list", "--format=json"], capture_output=True,
                           text=True, check=True)
        return [f"{r['projectId']}.{r['datasetId']}" for r in json.loads(p.stdout)
                if r.get("resourceType") in ("BQ_DATASET", "BIGQUERY_DATASET")]
    except Exception as e:  # noqa: BLE001 (not on a Workbench VM, or wb failed)
        print(f"[healthkit] wb resource list: {e}", flush=True)
        return []


def _project_datasets(client, project: str) -> list[str]:
    try:
        return [f"{project}.{d.dataset_id}" for d in client.list_datasets(project)]
    except Exception as e:  # noqa: BLE001 (no list permission on the CDR project)
        print(f"[healthkit] list datasets in {project}: {e}", flush=True)
        return []


def find_hk(client, cdr: str, given: str) -> tuple[str, str, list[str] | None]:
    """(dataset, how it was found, table filter or None)."""
    if given:
        return given, "--hk-dataset", None
    wb = _wb_datasets()
    proj = _project_datasets(client, cdr.split(".")[0])
    print(f"[healthkit] datasets seen: {sorted(set(wb + proj)) or 'none'}", flush=True)
    cdr_tables = list(query(client, f"SELECT table_name FROM `{cdr}.INFORMATION_SCHEMA."
                                    "TABLES`", {})["table_name"])
    cands = hk_candidates(wb + proj, cdr, cdr_tables)
    if len(cands) == 1 and not cands[0].startswith("CDR:"):
        return cands[0], "name match", None
    if cands and all(x.startswith("CDR:") for x in cands):
        return cdr, "CDR tables named like HealthKit", [x[4:] for x in cands]
    raise SystemExit(
        "[healthkit] " + (f"several candidates {cands}" if cands else
                          "no HealthKit-looking dataset found")
        + "; rerun with ARGS='--hk-dataset <project>.<dataset>' (the Workbench's data "
        "collection / AoU release notes give the name)")


# ---------------------------------------------------------------- main

def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    p.add_argument("--out-dir", required=True)
    p.add_argument("--hk-dataset", default="", help="<project>.<dataset> of HealthKit")
    p.add_argument("--hk-tables", default="",
                   help="comma list: only these HealthKit tables (any size)")
    p.add_argument("--hk-date-cols", default="", help="comma list of table=column overrides")
    p.add_argument("--max-gb", type=float, default=100,
                   help="skip larger HealthKit tables unless listed in --hk-tables")
    p.add_argument("--flags", default="rare")
    p.add_argument("--under", default="")
    p.add_argument("--exact", action="store_true")
    p.add_argument("--no-descendants", action="store_true")
    p.add_argument("--min-dx-dates", type=int, default=1)
    p.add_argument("--lookback", type=int, default=30)
    p.add_argument("--min-cov", type=int, default=14)
    p.add_argument("--washout", type=int, default=7)
    p.add_argument("--ip-overnight", action="store_true")
    p.add_argument("--mondo-version", default="2026-06-02")
    p.add_argument("--mondo-cache-dir", default="data/mondo")
    p.add_argument("--tag", default="")
    args = p.parse_args(argv)
    cdr, billing = workspace_env()
    flags = [f.strip() for f in args.flags.split(",") if f.strip()]
    bad = [f for f in flags if f not in _SOURCE_FLAGS]
    if bad:
        raise SystemExit(f"unknown --flags {bad}; known: {_SOURCE_FLAGS}")
    out = Path(args.out_dir) / cdr.split(".")[-1]
    out.mkdir(parents=True, exist_ok=True)
    client = bq_client(billing)

    hk, how, only = find_hk(client, cdr, args.hk_dataset)
    print(f"[healthkit] HealthKit dataset: {hk} ({how})", flush=True)
    schema = query(client, f"""
SELECT table_name, column_name, data_type FROM `{hk}.INFORMATION_SCHEMA.COLUMNS`
ORDER BY table_name, ordinal_position""", {})
    want = [t.strip() for t in args.hk_tables.split(",") if t.strip()]
    if only is not None:
        schema = schema[schema["table_name"].isin(only)]
    if want:
        schema = schema[schema["table_name"].isin(want)]
    try:
        sizes = query(client, f"SELECT table_id AS table_name, row_count, size_bytes "
                              f"FROM `{hk}.__TABLES__`", {})
    except Exception as e:  # noqa: BLE001 (metadata view not readable: sizes unknown)
        print(f"[healthkit] table sizes: {e}", flush=True)
        sizes = pd.DataFrame(columns=["table_name", "row_count", "size_bytes"])
    overrides = dict(kv.split("=", 1) for kv in args.hk_date_cols.split(",") if "=" in kv)
    picks = pick_columns(schema, overrides)
    tables = picks.merge(sizes, on="table_name", how="left")
    tables["gb"] = tables["size_bytes"] / 1e9
    big = (tables["gb"] > args.max_gb) & ~tables["table_name"].isin(want)
    tables.loc[big & (tables["why"] == ""), "why"] = f"over --max-gb {args.max_gb:g}"
    tables["used"] = tables["why"] == ""
    print(tables.to_string(index=False), flush=True)
    used = tables[tables["used"]]

    # Fitbit daily summaries, as wearables_events uses them.
    fcols = query(client, f"""
SELECT table_name, column_name FROM `{cdr}.INFORMATION_SCHEMA.COLUMNS`
WHERE table_name IN UNNEST(@tables)""", {"tables": ("STRING", [t for t, _, _ in _TIMING_TABLES])})
    fb_sql, fb_found = typed_wear_sql(
        cdr, fcols.groupby("table_name")["column_name"].apply(set).to_dict(), intraday=False)

    all_days = ("WITH all_days AS (SELECT DISTINCT person_id, src, d FROM (\n    "
                + fb_sql.replace(" JOIN cohort c ON t.person_id = c.person_id", "")
                + "\n    UNION ALL\n    " + hk_wear_sql(hk, used, cohort=False)
                + ") WHERE d IS NOT NULL)\n")
    print("[healthkit] all-participant queries…", flush=True)
    persons = query(client, all_days + ALL_PERSONS_SELECT.format(cdr=cdr), {})
    years = query(client, all_days + ALL_YEARS_SELECT, {})
    overlap = query(client, all_days + ALL_OVERLAP_SELECT, {})

    devices = {}
    for r in tables.itertuples():
        if not r.person_col:
            continue
        g = schema[(schema["table_name"] == r.table_name)
                   & schema["data_type"].str.upper().eq("STRING")]
        for col in g["column_name"]:
            if col != r.person_col and (DEVICE_NAME.search(col)
                                        or (DEVICE_NAME.search(r.table_name)
                                            and not col.endswith("_id"))):
                vals = query(client, DEVICE_VALUES_SELECT.format(
                    hk=hk, table=r.table_name, col=col, pcol=r.person_col), {})
                devices[(r.table_name, col)] = device_values(vals)

    roots = [x.strip() for x in args.under.split(",") if x.strip()]
    rm = build_rare_map(client, cdr, flags=flags, roots=roots, exact=args.exact,
                        mondo_version=args.mondo_version,
                        cache_dir=Path(args.mondo_cache_dir))
    rmap, names = rm.rmap, rm.names
    wear_sql = fb_sql + "\n    UNION ALL\n    " + hk_wear_sql(hk, used, cohort=True)
    ctes = (timing_ctes(cdr, wear_sql, descendants=not args.no_descendants)
            + events_ctes(None).replace("{cdr}", cdr))
    params = {"mondo": ("STRING", rmap["mondo_id"].tolist()),
              "cid": ("INT64", [int(x) for x in rmap["standard_concept_id"]]),
              "min_dx_dates": ("INT64", int(args.min_dx_dates)),
              "washout": ("INT64", int(args.washout)),
              "ip_overnight": ("BOOL", bool(args.ip_overnight))}
    print("[healthkit] cohort queries…", flush=True)
    n_dx = query(client, ctes + N_DX_SELECT, params)
    per = query(client, ctes + COHORT_SELECT, params)
    ev = query(client, ctes + HK_EVENTS_SELECT,
               {**params, "lookback": ("INT64", int(args.lookback))})
    coh = cohort_summary(per, n_dx)
    evs = events_summary(ev, min_cov=args.min_cov)
    evd = events_summary(ev, min_cov=args.min_cov, by_disease=True)

    tag = args.tag or run_name(roots, names, flags, exact=args.exact,
                               descendants=not args.no_descendants,
                               min_dx_dates=args.min_dx_dates)
    meta = {"run": tag, "cdr": cdr, "hk": hk, "hk_how": how, "fitbit_tables": fb_found,
            "hk_tables": list(used["table_name"]), "max_gb": args.max_gb,
            "flags": flags, "under": roots, "exact": args.exact,
            "scope": ", ".join(names.get(r, r) for r in roots) or "all rare",
            "lookback": args.lookback, "min_cov": args.min_cov, "washout": args.washout,
            "ip_overnight": bool(args.ip_overnight), "min_dx_dates": args.min_dx_dates}
    text = format_report(meta, tables, schema, persons, years, overlap, devices, coh, evs,
                         evd, names)
    (out / f"{tag}_hk-report.md").write_text(text)
    schema.to_csv(out / f"{tag}_hk-schema.tsv", sep="\t", index=False)
    cc = ["n_dx", "n_fitbit", "n_hk", "n_both", "n_hk_only", "n_hk_after"]
    mask_counts(coh, cc).to_csv(out / f"{tag}_hk-cohort.tsv", sep="\t", index=False)
    ec = [c for c in evd.columns if c.startswith(("n_", "cov_"))]
    mask_counts(pd.concat([evs, evd]), ec).to_csv(out / f"{tag}_hk-events.tsv", sep="\t",
                                                  index=False)
    (out / f"{tag}_hk-run.json").write_text(json.dumps(meta, indent=1, default=str))
    print(text, flush=True)
    print(f"[healthkit] wrote {out}/{tag}_hk-report.md (cells 1-19 as <20)", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
