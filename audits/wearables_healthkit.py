"""APPLE HEALTHKIT coverage next to Fitbit (RAPID TA1 wearables tab).

"How much Apple HealthKit data is there, for whom, and how many ED / inpatient episodes
would it cover that Fitbit doesn't?"

AoU published HealthKit (Sep 2026, a CDR v9 off-cycle release) as a STAND-ALONE BigQuery
dataset next to the CDR (V9 CT: `C_V9_R6_offcycle_healthkit`), joined by person_id:
`activity_measurements` (steps, energy, ... by `data_type`), `vital_measurements` (heart
rate, ... by `activity_type`), `physical_measurements` (weight and the like) and
`device_and_source` (one row per device / app, keyed by `device_source_id`).

  DATASET   --hk-dataset <project>.<dataset>, else the BigQuery datasets in `wb resource
            list` and in the CDR's project whose name looks like HealthKit (health /
            apple / hk), else CDR tables whose name does.
  TABLES    each table with a person column and a DATE / DATETIME / TIMESTAMP column
            (preferring `date`, then names with date, then start; --hk-date-cols
            table=col overrides) is one KIND of HealthKit data; --hk-skip tables
            (default physical_measurements: sporadic, often hand-entered) are described
            but not counted as coverage. Rows with is_user_entered are dropped.
  WATCH     a row is from an Apple Watch when its device_source_id's model or
            product_type in the device table says Watch; src = 'hk_<table>:watch' or
            ':other'. A day is a day with >= 1 row of that kind.
  COST      every query is dry-run first; the run stops if they total over --max-tb.

Sections: 1 tables and columns (metadata) · 2 all participants: persons per kind, in the
CDR `person` table, Fitbit / HealthKit / watch overlap, persons by year · 3 data types per
table and device models, values with >= 20 persons only (source and device names can
carry a person's name, so they are never read) · 4 the cohort (same disease selection as
wearables_events) · 5 ED / inpatient EPISODES after the first dx (wearables_events rules),
COVERED when >= --min-cov days of a source in the --lookback days before: by Fitbit, by
HealthKit, by watch days alone, and ADDED by HealthKit (covered with Fitbit + HealthKit
days, not with Fitbit alone).

EGRESS: every participant count goes through `cell` (1..19 -> "<20"), and NESTED cells
are suppressed together (`nested_cells`): where a total splits into parts (HealthKit =
both + HealthKit only, persons with episodes = with a covered one + without, ...) and a
part is 1..19, the larger parts show "—" so no subtraction gives the small one. The
"either source" count is never published (Fitbit + added gives it). Row counts and GB
are table metadata. Nothing person-level is written.

OUTPUT: `<out-dir>/<CDR dataset>/<run>_hk-report.md`, `_hk-schema.tsv`, `_hk-run.json`.
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
from rapidaudit.aou import bq_client, dry_run_bytes, query, workspace_env
from rapidaudit.egress import EGRESS_FLOOR, cell

HK_NAME = re.compile(r"health|apple|(^|[_\W])hk([_\W]|$)", re.I)
DATE_TYPES = ("DATE", "DATETIME", "TIMESTAMP")
TYPE_COLS = ("data_type", "activity_type", "type")
HK = "hk_"          # src prefix of HealthKit kinds (Fitbit kinds have none)
WATCH = ":watch"    # src suffix of rows from an Apple Watch
SUPPRESSED = "—"
USD_PER_TB = 6.25


# ---------------------------------------------------------------- egress

def nested_cells(vals: dict, groups, floor: int = EGRESS_FLOOR) -> dict:
    """`cell` for every key of `vals`, but for each (total, parts) group in `groups`
    where a part is 1..floor-1, parts >= floor become SUPPRESSED, so total minus the
    published parts never gives a small count. Parts may be hidden keys (not shown)."""
    out = {k: cell(v, floor) for k, v in vals.items()}
    for _total, parts in groups:
        if any(0 < vals[p] < floor for p in parts):
            for p in parts:
                if vals[p] >= floor:
                    out[p] = SUPPRESSED
    return out


# ---------------------------------------------------------------- discovery (pure)

def hk_candidates(datasets: list[str], cdr: str, cdr_tables: list[str]) -> list[str]:
    """'<project>.<dataset>' names that look like HealthKit (not the CDR), else
    'CDR:<table>' entries for CDR tables that do."""
    seen, out = set(), []
    for d in datasets:
        if d != cdr and d not in seen and HK_NAME.search(d.split(".")[-1]):
            seen.add(d)
            out.append(d)
    if not out:
        out = [f"CDR:{t}" for t in cdr_tables if HK_NAME.search(t)]
    return out


def pick_columns(schema: pd.DataFrame, overrides: dict | None = None,
                 skip=()) -> pd.DataFrame:
    """One row per table: person / date / type columns, whether it has device_source_id
    and is_user_entered, and `why` it isn't counted as coverage ('' when it is)."""
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
               f"date column {dc!r} not in table" if dc not in cols else
               "--hk-skip" if t in skip else "")
        rows.append({"table_name": t, "person_col": pc, "date_col": dc,
                     "person_type": cols.get(pc),
                     "type_col": next((c for c in TYPE_COLS if cols.get(c) == "STRING"), None),
                     "has_device": "device_source_id" in cols,
                     "has_user": "is_user_entered" in cols, "why": why})
    return pd.DataFrame(rows, columns=["table_name", "person_col", "date_col", "person_type",
                                       "type_col", "has_device", "has_user", "why"])


def device_table(schema: pd.DataFrame) -> str | None:
    """The table describing devices: device_source_id plus model or product_type, no
    person column."""
    for t, g in schema.groupby("table_name", sort=True):
        c = set(g["column_name"])
        if ("device_source_id" in c and c & {"model", "product_type"}
                and not any(re.search(r"person|participant", x, re.I) for x in c)):
            return t
    return None


def _dev_subquery(hk: str, dev: str, dev_cols: set) -> str:
    """(device_source_id, is_watch) from the device table: model or product_type says
    Watch."""
    cols = [f"IFNULL({c}, '')" for c in ("model", "product_type") if c in dev_cols]
    text = "LOWER(CONCAT(" + ", ' ', ".join(cols) + "))"
    return (f"(SELECT device_source_id, LOGICAL_OR(REGEXP_CONTAINS({text}, r'watch')) "
            f"AS is_watch FROM `{hk}.{dev}` GROUP BY device_source_id)")


def hk_rows_sql(hk: str, r, dev_sql: str | None, cohort: bool, select: str) -> str:
    """FROM ... for one HealthKit table: the row filter (no user-entered rows), optional
    device and cohort joins; `select` is the SELECT list (t. = the table, dv. = device)."""
    pid = (f"t.{r.person_col}" if str(r.person_type).upper() == "INT64"
           else f"SAFE_CAST(t.{r.person_col} AS INT64)")
    sel = select.replace("{pid}", pid)
    dj = (f" LEFT JOIN {dev_sql} dv ON dv.device_source_id = t.device_source_id"
          if dev_sql and r.has_device else "")
    cj = f" JOIN cohort c ON {pid} = c.person_id" if cohort else ""
    where = " WHERE NOT IFNULL(t.is_user_entered, FALSE)" if r.has_user else ""
    return f"SELECT {sel} FROM `{hk}.{r.table_name}` t{dj}{cj}{where}"


def hk_wear_sql(hk: str, picks: pd.DataFrame, dev_sql: str | None = None,
                cohort: bool = True) -> str:
    """UNION ALL of (person_id, src, d) over the coverage tables, src =
    'hk_<table>:watch' / ':other'; restricted to the `cohort` CTE when `cohort`."""
    parts = []
    for r in picks[picks["why"] == ""].itertuples():
        watch = ("IF(IFNULL(dv.is_watch, FALSE), 'watch', 'other')"
                 if dev_sql and r.has_device else "'other'")
        parts.append(hk_rows_sql(
            hk, r, dev_sql, cohort,
            f"{{pid}} AS person_id, CONCAT('{HK}{r.table_name}:', {watch}) AS src, "
            f"CAST(t.{r.date_col} AS DATE) AS d"))
    if not parts:
        raise SystemExit("[healthkit] no usable HealthKit table (see the schema above)")
    return "\n    UNION ALL\n    ".join(parts)


def all_days_sql(fb_sql: str, hk_sql: str) -> str:
    return ("WITH all_days AS (SELECT DISTINCT person_id, src, d FROM (\n    "
            + fb_sql.replace(" JOIN cohort c ON t.person_id = c.person_id", "")
            + "\n    UNION ALL\n    " + hk_sql + ") WHERE d IS NOT NULL)\n")


# ---------------------------------------------------------------- queries

_IS_HK = "STARTS_WITH(src, 'hk_')"
_IS_W = "ENDS_WITH(src, ':watch')"

ALL_KINDS_SELECT = f"""
SELECT a.src, COUNT(DISTINCT a.person_id) AS n_persons,
       COUNT(DISTINCT p.person_id) AS n_in_cdr
FROM (SELECT DISTINCT person_id, src FROM all_days WHERE {_IS_HK}
      UNION ALL
      SELECT DISTINCT person_id, 'any HealthKit' FROM all_days WHERE {_IS_HK}) a
LEFT JOIN `{{cdr}}.person` p ON p.person_id = a.person_id
GROUP BY a.src ORDER BY a.src
"""

ALL_OVERLAP_SELECT = f"""
SELECT COUNTIF(fb) AS n_fitbit, COUNTIF(hk) AS n_hk, COUNTIF(w) AS n_watch,
       COUNTIF(fb AND hk) AS n_both, COUNTIF(hk AND NOT fb) AS n_hk_only
FROM (SELECT person_id, LOGICAL_OR(NOT {_IS_HK}) AS fb, LOGICAL_OR({_IS_HK}) AS hk,
             LOGICAL_OR({_IS_HK} AND {_IS_W}) AS w
      FROM all_days GROUP BY person_id)
"""

ALL_YEARS_SELECT = f"""
SELECT EXTRACT(YEAR FROM d) AS year,
       COUNT(DISTINCT IF(NOT {_IS_HK}, person_id, NULL)) AS n_fitbit,
       COUNT(DISTINCT IF({_IS_HK}, person_id, NULL)) AS n_hk,
       COUNT(DISTINCT IF({_IS_HK} AND {_IS_W}, person_id, NULL)) AS n_watch
FROM all_days GROUP BY 1 ORDER BY 1
"""

# Persons and rows per value of a table's type column; format with the FROM sql.
TYPES_SELECT = """
SELECT value, COUNT(DISTINCT person_id) AS n_persons, COUNT(*) AS n_rows
FROM ({rows}) GROUP BY value ORDER BY n_persons DESC
"""

# Persons per (manufacturer, model) over the coverage tables; format with rows, hk, dev.
MODELS_SELECT = """
SELECT IFNULL(d.manufacturer, '(none)') AS manufacturer, IFNULL(d.model, '(none)') AS model,
       COUNT(DISTINCT r.person_id) AS n_persons
FROM ({rows}) r
LEFT JOIN (SELECT DISTINCT device_source_id, manufacturer, model FROM `{hk}.{dev}`) d
  ON d.device_source_id = r.device_source_id
GROUP BY 1, 2 ORDER BY n_persons DESC
"""

_FB = f"NOT STARTS_WITH(w.src, 'hk_')"
_HKW = "STARTS_WITH(w.src, 'hk_')"
_WW = "STARTS_WITH(w.src, 'hk_') AND ENDS_WITH(w.src, ':watch')"

# One row per (person, disease): days by source, all and after the first dx.
COHORT_SELECT = f"""
SELECT x.mondo_id,
  COUNT(DISTINCT IF({_FB}, w.d, NULL)) AS fb_days,
  COUNT(DISTINCT IF({_HKW}, w.d, NULL)) AS hk_days,
  COUNT(DISTINCT IF({_WW}, w.d, NULL)) AS watch_days,
  COUNT(DISTINCT IF({_FB} AND w.d > x.first_dx, w.d, NULL)) AS fb_after,
  COUNT(DISTINCT IF({_HKW} AND w.d > x.first_dx, w.d, NULL)) AS hk_after,
  COUNT(DISTINCT IF({_WW} AND w.d > x.first_dx, w.d, NULL)) AS watch_after,
  COUNT(DISTINCT IF(w.d > x.first_dx, w.d, NULL)) AS any_after
FROM dx_all x JOIN wear_days w USING (person_id)
GROUP BY x.person_id, x.mondo_id
"""

# One row per (person, disease, episode): covered days in the lookback by source.
# Extra param: @lookback INT64.
HK_EVENTS_SELECT = f"""
SELECT p.pid, e.mondo_id, DATE_DIFF(e.vd, e.first_dx, DAY) AS rel_day, e.is_ed, e.is_ip,
  COUNT(DISTINCT IF({_FB}, w.d, NULL)) AS cov_fb,
  COUNT(DISTINCT IF({_HKW}, w.d, NULL)) AS cov_hk,
  COUNT(DISTINCT IF({_WW}, w.d, NULL)) AS cov_watch,
  COUNT(DISTINCT w.d) AS cov_any
FROM ev e
JOIN pids p ON p.person_id = e.person_id
LEFT JOIN wear_days w ON w.person_id = e.person_id
  AND w.d >= DATE_SUB(e.vd, INTERVAL @lookback DAY) AND w.d < e.vd
GROUP BY p.pid, e.mondo_id, e.vd, e.first_dx, e.is_ed, e.is_ip
"""


# ---------------------------------------------------------------- summaries (raw counts)

def cohort_summary(per: pd.DataFrame, n_dx: pd.DataFrame) -> pd.DataFrame:
    """Per disease (ALL first): persons with the dx, Fitbit / HealthKit / watch / both /
    HealthKit only / HealthKit after dx (+ hidden complements), days after dx."""
    order = [ALL] + [m for m in n_dx["mondo_id"] if m != ALL]
    ndx = dict(zip(n_dx["mondo_id"], n_dx["n_dx"]))
    rows = []
    for m in order:
        x = per[per["mondo_id"] == m]
        fb, hk, w = x["fb_days"] > 0, x["hk_days"] > 0, x["watch_days"] > 0
        ha = x["hk_after"] > 0
        rows.append({"mondo_id": m, "n_dx": int(ndx.get(m, 0)),
                     "n_fitbit": int(fb.sum()), "n_hk": int(hk.sum()),
                     "n_watch": int(w.sum()), "n_both": int((fb & hk).sum()),
                     "n_hk_only": int((hk & ~fb).sum()), "n_hk_after": int(ha.sum()),
                     "x_fb_only": int((fb & ~hk).sum()), "x_hk_no_watch": int((hk & ~w).sum()),
                     "x_hk_not_after": int((hk & ~ha).sum()),
                     "fb_days_after": int(x["fb_after"].sum()),
                     "hk_days_after": int(x["hk_after"].sum()),
                     "watch_days_after": int(x["watch_after"].sum()),
                     "any_days_after": int(x["any_after"].sum())})
    return pd.DataFrame(rows)


COHORT_GROUPS = (("n_hk", ("n_both", "n_hk_only")), ("n_fitbit", ("n_both", "x_fb_only")),
                 ("n_hk", ("n_watch", "x_hk_no_watch")),
                 ("n_hk", ("n_hk_after", "x_hk_not_after")))
COHORT_KEYS = ("n_dx", "n_fitbit", "n_hk", "n_watch", "n_both", "n_hk_only", "n_hk_after",
               "x_fb_only", "x_hk_no_watch", "x_hk_not_after")


def events_summary(ev: pd.DataFrame, *, min_cov: int, by_disease: bool = False
                   ) -> pd.DataFrame:
    """Episodes after the first dx (rel_day > 0): covered by Fitbit / HealthKit / watch
    days alone / ADDED by HealthKit (either source but not Fitbit alone), with persons,
    plus the hidden complements nested_cells needs. ALL by class, or (by_disease) each
    disease for ed_or_inpatient."""
    keys = ([(m, "ed_or_inpatient") for m in ev["mondo_id"].unique()] if by_disease
            else [(ALL, c) for c in CLASSES])
    rows = []
    for m, cls in keys:
        e = ev[(ev["mondo_id"] == m) & (ev["rel_day"] > 0)]
        e = e[event_class_mask(e, cls)]
        sel = {"fb": e["cov_fb"] >= min_cov, "hk": e["cov_hk"] >= min_cov,
               "watch": e["cov_watch"] >= min_cov}
        sel["added"] = (e["cov_any"] >= min_cov) & ~sel["fb"]
        pids = lambda s: set(e.loc[s, "pid"])  # noqa: E731
        allp = set(e["pid"])
        row = {"mondo_id": m, "event_class": cls, "n_ev": len(e), "n_ev_p": len(allp)}
        for k, s in sel.items():
            row[f"cov_{k}"] = int(s.sum())
            row[f"cov_{k}_p"] = len(pids(s))
        row["cov_any"] = row["cov_fb"] + row["cov_added"]
        row["x_unc"] = len(e) - row["cov_fb"]
        row["x_unc_p"] = len(allp - pids(sel["fb"]))
        row["x_hk_nw"] = int((sel["hk"] & ~sel["watch"]).sum())
        row["x_hk_nw_p"] = len(pids(sel["hk"]) - pids(sel["watch"]))
        rows.append(row)
    out = pd.DataFrame(rows)
    if by_disease and len(out):
        out = out.sort_values(["cov_any", "mondo_id"], ascending=[False, True])
    return out.reset_index(drop=True)


EVENT_GROUPS = (("n_ev", ("cov_fb", "x_unc")), ("n_ev_p", ("cov_fb_p", "x_unc_p")),
                ("cov_hk", ("cov_watch", "x_hk_nw")), ("cov_hk_p", ("cov_watch_p", "x_hk_nw_p")))
EVENT_KEYS = ("n_ev", "n_ev_p", "cov_fb", "cov_fb_p", "cov_hk", "cov_hk_p", "cov_watch",
              "cov_watch_p", "cov_added", "cov_added_p", "x_unc", "x_unc_p", "x_hk_nw",
              "x_hk_nw_p")


def top_values(vals: pd.DataFrame, floor: int = EGRESS_FLOOR) -> pd.DataFrame:
    """Values held by >= floor persons; the rest pooled as one '(other)' row whose
    person count is a sum (can double count) and whose value count is masked too."""
    big = vals[vals["n_persons"] >= floor].copy()
    rest = vals[vals["n_persons"] < floor]
    if len(rest):
        extra = {c: [rest[c].sum()] for c in vals.columns if c.startswith("n_")}
        label = f"(other: {cell(len(rest), floor)} values)"
        extra.update({c: [label if i == 0 else ""] for i, c in
                      enumerate(c for c in vals.columns if not c.startswith("n_"))})
        big = pd.concat([big, pd.DataFrame(extra)], ignore_index=True)
    return big.fillna("(null)")


# ---------------------------------------------------------------- report

def _t(header, rows) -> list[str]:
    return (["| " + " | ".join(header) + " |", "|" + "---|" * len(header)]
            + ["| " + " | ".join(str(c) for c in r) + " |" for r in rows])


def _s(v) -> str:
    return "" if v is None or (isinstance(v, float) and pd.isna(v)) else str(v)


def _kind(src: str) -> str:
    return src.removeprefix(HK).replace(":", " · ")


def format_report(meta, tables, schema, kinds, overlap, years, types, models, coh, evs,
                  evd, names, floor: int = EGRESS_FLOOR) -> str:
    c = lambda n: cell(n, floor)  # noqa: E731
    L = [f"# Apple HealthKit next to Fitbit — {meta['run']}", "",
         f"CDR `{meta['cdr']}` · HealthKit `{meta['hk']}` (found by: {meta['hk_how']}) · "
         f"Fitbit daily summaries: {', '.join(meta['fitbit_tables'])} · HealthKit coverage "
         f"tables: {', '.join(meta['hk_tables'])}, user-entered rows dropped · watch = "
         f"device model / product type says Watch · BigQuery estimate "
         f"{meta['est_tb']:.2f} TB", "",
         "Counts are participants unless they say rows; 1-19 show as <20, and — hides a "
         "cell whose nested partner is <20. Don't subtract published cells.", "",
         "## 1. Tables", ""]
    L += _t(["table", "rows", "GB", "person col", "date col", "type col", "coverage"],
            [(r.table_name, f"{int(r.row_count):,}" if pd.notna(r.row_count) else "",
              f"{r.gb:.1f}" if pd.notna(r.gb) else "", _s(r.person_col),
              _s(r.date_col), _s(r.type_col), "yes" if r.why == "" else f"no: {r.why}")
             for r in tables.itertuples()])
    L += ["", "<details><summary>Columns</summary>", ""]
    L += _t(["table", "column", "type"],
            [(r.table_name, r.column_name, r.data_type) for r in schema.itertuples()])
    L += ["", "</details>", "", "## 2. All participants", ""]
    krows = []
    for r in kinds.itertuples():
        v = {"n": int(r.n_persons), "in": int(r.n_in_cdr),
             "_out": int(r.n_persons) - int(r.n_in_cdr)}
        k = nested_cells(v, [("n", ("in", "_out"))], floor)
        krows.append((_kind(r.src), k["n"], k["in"]))
    L += _t(["HealthKit kind", "persons", "of those in the CDR person table"], krows)
    o = overlap.iloc[0]
    ov = {k: int(o[k]) for k in ("n_fitbit", "n_hk", "n_watch", "n_both", "n_hk_only")}
    ov["x_fb_only"], ov["x_hk_no_watch"] = (ov["n_fitbit"] - ov["n_both"],
                                          ov["n_hk"] - ov["n_watch"])
    oc = nested_cells(ov, COHORT_GROUPS[:3], floor)
    L += ["", f"Persons with Fitbit daily data: {oc['n_fitbit']} · HealthKit: {oc['n_hk']} "
          f"· HealthKit from a watch: {oc['n_watch']} · both Fitbit and HealthKit: "
          f"{oc['n_both']} · HealthKit only: {oc['n_hk_only']}", "",
          "Persons with data by year:", ""]
    yrows = []
    for r in years.dropna(subset=["year"]).itertuples():
        v = {"fb": int(r.n_fitbit), "hk": int(r.n_hk), "w": int(r.n_watch),
             "_nw": int(r.n_hk) - int(r.n_watch)}
        y = nested_cells(v, [("hk", ("w", "_nw"))], floor)
        yrows.append((int(r.year), y["fb"], y["hk"], y["w"]))
    L += _t(["year", "Fitbit", "HealthKit", "HealthKit watch"], yrows)
    L += ["", "## 3. Data types and devices", ""]
    for t, d in types.items():
        L += [f"`{t}` by type (values with >= {floor} persons; the rest pooled):", ""]
        L += _t(["type", "persons", "rows"],
                [(r.value, c(r.n_persons), f"{int(r.n_rows):,}") for r in d.itertuples()])
        L += [""]
    if models is not None:
        L += [f"Device models over the coverage tables (>= {floor} persons; the rest "
              "pooled):", ""]
        L += _t(["manufacturer", "model", "persons"],
                [(r.manufacturer, r.model, c(r.n_persons)) for r in models.itertuples()])
    a = coh.iloc[0]
    ac = nested_cells({k: int(a[k]) for k in COHORT_KEYS}, COHORT_GROUPS, floor)
    L += ["", f"## 4. Cohort ({meta['scope']})", "",
          f"Persons with a selected diagnosis: {ac['n_dx']} · with Fitbit: {ac['n_fitbit']} "
          f"· with HealthKit: {ac['n_hk']} · HealthKit from a watch: {ac['n_watch']} · "
          f"both: {ac['n_both']} · HealthKit only: {ac['n_hk_only']} · with HealthKit days "
          f"after dx: {ac['n_hk_after']}", "",
          f"Days after dx: Fitbit {int(a.fb_days_after):,} · HealthKit "
          f"{int(a.hk_days_after):,} · HealthKit watch {int(a.watch_days_after):,} · either "
          f"{int(a.any_days_after):,}", "",
          f"By disease (persons with HealthKit >= {floor}):", ""]
    sub = coh[(coh["mondo_id"] != ALL) & (coh["n_hk"] >= floor)].sort_values(
        "n_hk", ascending=False)
    drows = []
    for r in sub.itertuples():
        x = nested_cells({k: int(getattr(r, k)) for k in COHORT_KEYS}, COHORT_GROUPS, floor)
        drows.append((r.mondo_id, names.get(r.mondo_id, ""), x["n_dx"], x["n_fitbit"],
                      x["n_hk"], x["n_watch"], x["n_both"], x["n_hk_only"]))
    L += _t(["Mondo", "disease", "dx", "Fitbit", "HealthKit", "watch", "both",
             "HealthKit only"], drows)
    L += ["", "## 5. Covered episodes after dx", "",
          f"Episode = ED / inpatient visit starts within {meta['washout']} days merged"
          + (", inpatient only with a stay (a row past its start day or consecutive "
             "inpatient days)" if meta["ip_overnight"] else "")
          + f"; covered = >= {meta['min_cov']} days of that source in the {meta['lookback']} "
          "days before; added by HealthKit = covered with Fitbit and HealthKit days "
          "together, not with Fitbit alone. Episodes among persons with any Fitbit or "
          "HealthKit day. Cells: episodes (persons).", ""]
    hdr = ["episodes", "Fitbit", "HealthKit", "watch alone", "added by HealthKit"]

    L += _t(["class"] + hdr,
            [[r.event_class] + _ev_cells(r, floor)
             for r in evs.itertuples()])
    L += ["", f"ED or inpatient by disease (Fitbit + added >= {floor}, i.e. a disease "
          "the challenge could score):", ""]
    sub = evd[(evd["mondo_id"] != ALL) & (evd["cov_any"] >= floor)]
    L += _t(["Mondo", "disease"] + hdr,
            [[r.mondo_id, names.get(r.mondo_id, "")] + _ev_cells(r, floor)
             for r in sub.itertuples()])
    return "\n".join(L) + "\n"


def _ev_cells(r, floor: int = EGRESS_FLOOR) -> list[str]:
    x = nested_cells({k: int(getattr(r, k)) for k in EVENT_KEYS}, EVENT_GROUPS, floor)
    return [f"{x[k]} ({x[k + '_p']})" for k in ("n_ev", "cov_fb", "cov_hk", "cov_watch",
                                                "cov_added")]


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
        + "; rerun with HK=<project>.<dataset>")


# ---------------------------------------------------------------- main

def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    p.add_argument("--out-dir", required=True)
    p.add_argument("--hk-dataset", default="", help="<project>.<dataset> of HealthKit")
    p.add_argument("--hk-skip", default="physical_measurements",
                   help="comma list: tables described but not counted as coverage")
    p.add_argument("--hk-date-cols", default="", help="comma list of table=column overrides")
    p.add_argument("--max-tb", type=float, default=3.0,
                   help="stop if the dry-run estimate of all queries is over this many TB")
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
    if only is not None:
        schema = schema[schema["table_name"].isin(only)]
    try:
        sizes = query(client, f"SELECT table_id AS table_name, row_count, size_bytes "
                              f"FROM `{hk}.__TABLES__`", {})
    except Exception as e:  # noqa: BLE001 (metadata view not readable: sizes unknown)
        print(f"[healthkit] table sizes: {e}", flush=True)
        sizes = pd.DataFrame(columns=["table_name", "row_count", "size_bytes"])
    overrides = dict(kv.split("=", 1) for kv in args.hk_date_cols.split(",") if "=" in kv)
    skip = {t.strip() for t in args.hk_skip.split(",") if t.strip()}
    picks = pick_columns(schema, overrides, skip)
    tables = picks.merge(sizes, on="table_name", how="left")
    tables["gb"] = pd.to_numeric(tables["size_bytes"], errors="coerce") / 1e9
    print(tables.drop(columns=["size_bytes"]).to_string(index=False), flush=True)
    dev = device_table(schema)
    dev_sql = (_dev_subquery(hk, dev, set(schema.loc[schema["table_name"] == dev,
                                                     "column_name"])) if dev else None)
    used = picks[picks["why"] == ""]

    fcols = query(client, f"""
SELECT table_name, column_name FROM `{cdr}.INFORMATION_SCHEMA.COLUMNS`
WHERE table_name IN UNNEST(@tables)""", {"tables": ("STRING", [t for t, _, _ in _TIMING_TABLES])})
    fb_sql, fb_found = typed_wear_sql(
        cdr, fcols.groupby("table_name")["column_name"].apply(set).to_dict(), intraday=False)

    roots = [x.strip() for x in args.under.split(",") if x.strip()]
    rm = build_rare_map(client, cdr, flags=flags, roots=roots, exact=args.exact,
                        mondo_version=args.mondo_version,
                        cache_dir=Path(args.mondo_cache_dir))
    rmap, names = rm.rmap, rm.names
    all_days = all_days_sql(fb_sql, hk_wear_sql(hk, used, dev_sql, cohort=False))
    ctes = (timing_ctes(cdr, fb_sql + "\n    UNION ALL\n    "
                        + hk_wear_sql(hk, used, dev_sql, cohort=True),
                        descendants=not args.no_descendants)
            + events_ctes(None).replace("{cdr}", cdr))
    params = {"mondo": ("STRING", rmap["mondo_id"].tolist()),
              "cid": ("INT64", [int(x) for x in rmap["standard_concept_id"]]),
              "min_dx_dates": ("INT64", int(args.min_dx_dates)),
              "washout": ("INT64", int(args.washout)),
              "ip_overnight": ("BOOL", bool(args.ip_overnight))}
    evp = {**params, "lookback": ("INT64", int(args.lookback))}

    plan = {"kinds": (all_days + ALL_KINDS_SELECT.format(cdr=cdr), {}),
            "overlap": (all_days + ALL_OVERLAP_SELECT, {}),
            "years": (all_days + ALL_YEARS_SELECT, {}),
            "n_dx": (ctes + N_DX_SELECT, params),
            "cohort": (ctes + COHORT_SELECT, params),
            "events": (ctes + HK_EVENTS_SELECT, evp)}
    for r in picks[picks["type_col"].notna() & picks["person_col"].notna()].itertuples():
        rows = hk_rows_sql(hk, r, None, False, f"{{pid}} AS person_id, t.{r.type_col} AS value")
        plan[f"types:{r.table_name}"] = (TYPES_SELECT.format(rows=rows), {})
    if dev:
        rows = "\n  UNION ALL\n  ".join(
            hk_rows_sql(hk, r, None, False, "{pid} AS person_id, t.device_source_id")
            for r in used.itertuples() if r.has_device)
        if rows:
            plan["models"] = (MODELS_SELECT.format(rows=rows, hk=hk, dev=dev), {})

    est = {k: dry_run_bytes(client, s, prm) for k, (s, prm) in plan.items()}
    tb = sum(est.values()) / 1e12
    for k, b in est.items():
        print(f"[healthkit] dry run {k}: {b / 1e9:,.1f} GB", flush=True)
    print(f"[healthkit] total {tb:.2f} TB (~${tb * USD_PER_TB:.0f} on demand)", flush=True)
    if tb > args.max_tb:
        raise SystemExit(f"[healthkit] estimate {tb:.2f} TB is over --max-tb {args.max_tb:g}; "
                         "rerun with ARGS='--max-tb N' to go ahead")

    res = {}
    for k, (s, prm) in plan.items():
        print(f"[healthkit] {k} query…", flush=True)
        res[k] = query(client, s, prm)
    coh = cohort_summary(res["cohort"], res["n_dx"])
    evs = events_summary(res["events"], min_cov=args.min_cov)
    evd = events_summary(res["events"], min_cov=args.min_cov, by_disease=True)
    types = {k.split(":", 1)[1]: top_values(v) for k, v in res.items()
             if k.startswith("types:")}
    models = top_values(res["models"]) if "models" in res else None

    tag = args.tag or run_name(roots, names, flags, exact=args.exact,
                               descendants=not args.no_descendants,
                               min_dx_dates=args.min_dx_dates)
    meta = {"run": tag, "cdr": cdr, "hk": hk, "hk_how": how, "fitbit_tables": fb_found,
            "hk_tables": list(used["table_name"]), "hk_skip": sorted(skip),
            "device_table": dev, "est_tb": tb, "flags": flags, "under": roots,
            "exact": args.exact,
            "scope": ", ".join(names.get(r, r) for r in roots) or "all rare",
            "lookback": args.lookback, "min_cov": args.min_cov, "washout": args.washout,
            "ip_overnight": bool(args.ip_overnight), "min_dx_dates": args.min_dx_dates}
    text = format_report(meta, tables, schema, res["kinds"], res["overlap"], res["years"],
                         types, models, coh, evs, evd, names)
    (out / f"{tag}_hk-report.md").write_text(text)
    schema.to_csv(out / f"{tag}_hk-schema.tsv", sep="\t", index=False)
    (out / f"{tag}_hk-run.json").write_text(json.dumps(meta, indent=1, default=str))
    print(text, flush=True)
    print(f"[healthkit] wrote {out}/{tag}_hk-report.md (cells 1-19 as <20, nested "
          "partners as —)", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
