"""WEARABLES x ACUTE CARE EVENTS: is there enough data for "predict an ED / inpatient
visit in the next N days from the preceding Fitbit data"?

Diseases are chosen and mapped as in `wearables_timing` (`build_rare_map`, `--under`,
`--exact`, `--min-dx-dates`; `ALL` pools them, first dx = earliest among them). The
cohort is persons with a selected diagnosis AND at least one Fitbit daily-summary day.

EVENTS = acute-care EPISODES: ED or inpatient visit starts in visit_occurrence (visit
concepts under 9203 Emergency Room Visit, 9201 Inpatient Visit or 262 Emergency Room and
Inpatient Visit in OMOP `concept_ancestor`, plus 8870 / 8717, the CMS place-of-service ED
and inpatient-hospital concepts), grouped per person so that a visit starting within
--washout days (default 7) of the previous one belongs to the same episode (multi-day
stays often have a visit row per day). An episode's date is its first day. Classes:
  ed_or_inpatient   any of them
  ed / inpatient    ED (9203 or 262) / inpatient (9201 or 262)
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

SPLIT (--after DATE, e.g. the previous CDR's data cutoff): how much a later release
would add as a prospective test set. Persons are KNOWN when diagnosed and wearing a
Fitbit before DATE (they and their history would be in the earlier release), NEW
otherwise. Test episodes start on or after DATE (and after dx); training episodes start
after dx and before DATE. Per disease (ed_or_inpatient) and pooled (each class):
  n_known / n_known_post     known persons / those with Fitbit days on or after DATE
  wd_post                    known persons' Fitbit days on or after DATE
  n_train / n_train_p        covered training episodes of known persons / persons
  n_test / n_test_p          covered test episodes of known persons / persons
  n_new / n_new_test(_p)     new persons with Fitbit days after dx on or after DATE /
                             their covered test episodes / persons with one
"Known" is a date-based stand-in for "in the earlier release": late-arriving EHR records
and Fitbit history synced after DATE make it overcount a little; test episodes (dated
on or after DATE) are unaffected.

EGRESS: every count through `cell`; the rate only where the count behind it is >= 20.
Columns are nested (n_ev >= n_cov, ed_or_inpatient >= each class): check differences
before sharing beyond the Workbench team. Person ids stay in BigQuery: rows come back
keyed by a per-run rank, and nothing person-level is written.

OUTPUT: `<out-dir>/<CDR dataset>/<run>_events-report.md`, `_events-table.tsv`,
`_visit-types.tsv`, `_events-run.json`, `_events-plot-*.png` (from the masked report),
and with --after, `_split-table.tsv`.
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
# CMS place-of-service visit concepts that may sit outside the 9201 / 9203 hierarchy.
ED_EXTRA, INPATIENT_EXTRA = (8870,), (8717,)   # Emergency Room - Hospital; Inpatient Hospital
ED_ROOTS = (ED, ED_AND_INPATIENT, *ED_EXTRA)
IP_ROOTS = (INPATIENT, ED_AND_INPATIENT, *INPATIENT_EXTRA)
CLASSES = ("ed_or_inpatient", "ed", "inpatient")
COV_BINS = (0, 1, 7, 14, 21)   # lower edges of covered-days bins in the lookback


def _ids(ids) -> str:
    return ", ".join(str(i) for i in ids)


def events_ctes(site_table: str | None = None) -> str:
    """Appended to `timing_ctes(...)` (daily summaries only). Extra param: @washout
    INT64 (days between visit starts that still belong to one episode).
    `wdays` = (person, Fitbit day); `wp` = cohort persons with Fitbit data; `pids` = a
    per-run rank standing in for person_id; `ev` = (person, disease, first_dx, episode
    start date) with ED / inpatient flags and `site`, the EHR source (`src_id` of
    `site_table`, e.g. visit_occurrence_ext) of the episode's first day, or NULL when no
    site table is given."""
    site_join = (f"\n  LEFT JOIN `{{cdr}}.{site_table}` vx "
                 "ON vx.visit_occurrence_id = v.visit_occurrence_id" if site_table else "")
    site_col = "vx.src_id" if site_table else "CAST(NULL AS STRING)"
    return f""",
wdays AS (SELECT DISTINCT person_id, d FROM wear_days),
wp AS (SELECT DISTINCT person_id FROM wdays),
pids AS (SELECT person_id, DENSE_RANK() OVER (ORDER BY person_id) AS pid FROM wp),
vt AS (
  SELECT descendant_concept_id AS cid,
         LOGICAL_OR(ancestor_concept_id IN ({_ids(ED_ROOTS)})) AS is_ed,
         LOGICAL_OR(ancestor_concept_id IN ({_ids(IP_ROOTS)})) AS is_ip
  FROM `{{cdr}}.concept_ancestor`
  WHERE ancestor_concept_id IN ({_ids(ED_ROOTS + IP_ROOTS)})
  GROUP BY descendant_concept_id),
vis AS (
  SELECT v.person_id, v.visit_occurrence_id, CAST(v.visit_start_date AS DATE) AS vd,
         CAST(v.visit_end_date AS DATE) AS ved, v.visit_concept_id,
         vt.is_ed, vt.is_ip, {site_col} AS site
  FROM `{{cdr}}.visit_occurrence` v
  JOIN vt ON v.visit_concept_id = vt.cid
  JOIN wp ON v.person_id = wp.person_id{site_join}),
acute AS (SELECT DISTINCT person_id, vd FROM vis),
acute_new AS (
  SELECT person_id, vd,
         IFNULL(DATE_DIFF(vd, LAG(vd) OVER (PARTITION BY person_id ORDER BY vd), DAY)
                > @washout, TRUE) AS new_ep
  FROM acute),
acute_ep AS (
  SELECT person_id, vd,
         COUNTIF(new_ep) OVER (PARTITION BY person_id ORDER BY vd) AS ep
  FROM acute_new),
ev_day AS (
  SELECT x.person_id, x.mondo_id, x.first_dx, v.vd,
         LOGICAL_OR(v.is_ed) AS is_ed, LOGICAL_OR(v.is_ip) AS is_ip,
         ARRAY_AGG(v.site IGNORE NULLS ORDER BY v.site LIMIT 1)[SAFE_OFFSET(0)] AS site
  FROM dx_all x
  JOIN vis v ON v.person_id = x.person_id
  GROUP BY x.person_id, x.mondo_id, x.first_dx, v.vd),
ev AS (
  SELECT e.person_id, e.mondo_id, e.first_dx, MIN(e.vd) AS vd,
         LOGICAL_OR(e.is_ed) AS is_ed, LOGICAL_OR(e.is_ip) AS is_ip,
         ARRAY_AGG(e.site IGNORE NULLS ORDER BY e.vd LIMIT 1)[SAFE_OFFSET(0)] AS site
  FROM ev_day e
  JOIN acute_ep a ON a.person_id = e.person_id AND a.vd = e.vd
  GROUP BY e.person_id, e.mondo_id, e.first_dx, a.ep)
"""


# One row per (person, disease, event date). Extra param: @lookback INT64.
EVENTS_SELECT = """
SELECT p.pid, e.mondo_id, DATE_DIFF(e.vd, e.first_dx, DAY) AS rel_day,
       e.is_ed, e.is_ip, e.site, COUNT(w.d) AS cov_days
FROM ev e
JOIN pids p ON p.person_id = e.person_id
LEFT JOIN wdays w ON w.person_id = e.person_id
  AND w.d >= DATE_SUB(e.vd, INTERVAL @lookback DAY) AND w.d < e.vd
GROUP BY p.pid, e.mondo_id, e.vd, e.first_dx, e.is_ed, e.is_ip, e.site
"""

# EVENTS_SELECT plus each episode's and first dx's day offset from @split DATE.
SPLIT_EVENTS_SELECT = EVENTS_SELECT.replace(
    "e.site, COUNT(w.d) AS cov_days",
    "e.site, COUNT(w.d) AS cov_days,\n"
    "       DATE_DIFF(e.vd, @split, DAY) AS split_day,\n"
    "       DATE_DIFF(e.first_dx, @split, DAY) AS dx_split_day", 1)

# One row per (person, disease): Fitbit days before @split, and after both dx and @split.
SPLIT_EXPOSURE_SELECT = """
SELECT p.pid, x.mondo_id, DATE_DIFF(x.first_dx, @split, DAY) AS dx_split_day,
       COUNTIF(w.d < @split) AS wd_pre,
       COUNTIF(w.d >= @split AND w.d > x.first_dx) AS wd_post
FROM dx_all x
JOIN wdays w ON w.person_id = x.person_id
JOIN pids p ON p.person_id = x.person_id
GROUP BY p.pid, x.mondo_id, x.first_dx
"""

# Days from @split to the cohort's last Fitbit day and last ED / inpatient visit start.
SPLIT_SPAN_SELECT = """
SELECT DATE_DIFF((SELECT MAX(d) FROM wdays), @split, DAY) AS wear_days_span,
       DATE_DIFF((SELECT MAX(vd) FROM vis), @split, DAY) AS visit_days_span
"""

# Tables carrying an EHR source column (All of Us `*_ext` tables, `src_id`).
SITE_TABLES_SELECT = """
SELECT table_name FROM `{cdr}.INFORMATION_SCHEMA.COLUMNS`
WHERE column_name = 'src_id' AND ENDS_WITH(table_name, '_ext')
ORDER BY table_name
"""

# One row per cohort person: the EHR source with most of their visits (any visit type).
PERSON_SITE_SELECT = """
SELECT p.pid,
       ARRAY_AGG(s.src_id ORDER BY s.n DESC, s.src_id LIMIT 1)[OFFSET(0)] AS primary_site
FROM (
  SELECT v.person_id, vx.src_id, COUNT(*) AS n
  FROM `{cdr}.visit_occurrence` v
  JOIN `{cdr}.{site_table}` vx ON vx.visit_occurrence_id = v.visit_occurrence_id
  JOIN wp ON v.person_id = wp.person_id
  WHERE vx.src_id IS NOT NULL
  GROUP BY v.person_id, vx.src_id) s
JOIN pids p ON p.person_id = s.person_id
GROUP BY p.pid
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
    return ev["is_ed"].astype(bool) | ev["is_ip"].astype(bool)


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


def site_label(src_id: str, rank: int) -> str:
    """Published label for an EHR source: participant-portal sources keep their (non-site)
    name, EHR sites become 'site <rank>' so no source code leaves the Workbench."""
    s = str(src_id)
    return s if s.lower().startswith("participant portal") else f"site {rank}"


def site_summary(ev: pd.DataFrame, psite: pd.DataFrame, expo: pd.DataFrame, *,
                 min_cov: int) -> pd.DataFrame:
    """Published per-source table (labels only); see `site_ranks`."""
    return site_ranks(ev, psite, expo, min_cov=min_cov).drop(columns="src_id")


def site_ranks(ev: pd.DataFrame, psite: pd.DataFrame, expo: pd.DataFrame, *,
               min_cov: int) -> pd.DataFrame:
    """Per EHR source, for the pooled (ALL) cohort: persons whose primary source it is,
    covered ED / inpatient episodes after dx whose first day was recorded there, and
    persons with such an episode. Rows sorted by persons; labels from `site_label`."""
    persons = psite[psite["pid"].isin(expo.loc[expo["mondo_id"] == ALL, "pid"])]
    e = ev[(ev["mondo_id"] == ALL) & (ev["rel_day"] > 0) & (ev["cov_days"] >= min_cov)]
    e = e[event_class_mask(e, "ed_or_inpatient")]
    out = pd.DataFrame({"n_persons": persons.groupby("primary_site").size()})
    out["n_cov"] = e.groupby("site").size()
    out["n_cov_p"] = e.groupby("site")["pid"].nunique()
    out = out.fillna(0).astype(int).sort_values(["n_persons", "n_cov"], ascending=False)
    out = out.reset_index().rename(columns={"index": "src_id", "primary_site": "src_id"})
    out.insert(0, "site", [site_label(s, i + 1) for i, s in enumerate(out["src_id"])])
    return out   # src_id stays in memory only: never write this frame


def split_summary(sev: pd.DataFrame, sexpo: pd.DataFrame, n_dx: pd.DataFrame, *,
                  min_cov: int, floor: int = EGRESS_FLOOR) -> pd.DataFrame:
    """Raw per-(disease, class) split counts (see SPLIT in the module docstring) from
    SPLIT_EVENTS_SELECT / SPLIT_EXPOSURE_SELECT rows. ALL first, then `n_dx` order."""
    order = [ALL] + [m for m in n_dx["mondo_id"] if m != ALL]
    rows = []
    for m in order:
        x = sexpo[sexpo["mondo_id"] == m]
        known = x[(x["dx_split_day"] < 0) & (x["wd_pre"] > 0)]
        new = x[~x["pid"].isin(known["pid"]) & (x["wd_post"] > 0)]
        e_m = sev[(sev["mondo_id"] == m) & (sev["rel_day"] > 0) & (sev["cov_days"] >= min_cov)]
        for cls in CLASSES:
            e = e_m[event_class_mask(e_m, cls)]
            ek = e[e["pid"].isin(known["pid"])]
            train, test = ek[ek["split_day"] < 0], ek[ek["split_day"] >= 0]
            en = e[e["pid"].isin(new["pid"]) & (e["split_day"] >= 0)]
            wdp = int(known["wd_post"].sum())
            rows.append({
                "mondo_id": m, "event_class": cls, "n_known": len(known),
                "n_known_post": int((known["wd_post"] > 0).sum()), "wd_post": wdp,
                "n_train": len(train), "n_train_p": int(train["pid"].nunique()),
                "n_test": len(test), "n_test_p": int(test["pid"].nunique()),
                "test_per_1k": (round(1000 * len(test) / wdp, 2)
                                if len(test) >= floor and wdp else None),
                "n_new": len(new), "n_new_test": len(en),
                "n_new_test_p": int(en["pid"].nunique())})
    return pd.DataFrame(rows)


SPLIT_COUNT_COLS = ["n_known", "n_known_post", "n_train", "n_train_p", "n_test", "n_test_p",
                    "n_new", "n_new_test", "n_new_test_p"]


def masked_split_table(split: pd.DataFrame, names: dict,
                       floor: int = EGRESS_FLOOR) -> pd.DataFrame:
    out = mask_counts(split, SPLIT_COUNT_COLS, floor)
    out["test_per_1k"] = split["test_per_1k"].map(
        lambda v: "" if v is None or pd.isna(v) else f"{v:.2f}")
    out.insert(1, "name", out["mondo_id"].map(
        lambda m: "all selected diseases" if m == ALL else names.get(m, m)))
    return out


SPLIT_HEAD = ("known persons | still wearing after split | covered train episodes | persons | "
              "covered test episodes | persons | test per 1k wear-days | new persons | "
              "their covered test episodes | persons |")


def _split_row(r, floor) -> str:
    rate = "—" if r["test_per_1k"] is None or pd.isna(r["test_per_1k"]) else f"{r['test_per_1k']:.2f}"
    return " | ".join([cell(r["n_known"], floor), cell(r["n_known_post"], floor),
                       cell(r["n_train"], floor), cell(r["n_train_p"], floor),
                       cell(r["n_test"], floor), cell(r["n_test_p"], floor), rate,
                       cell(r["n_new"], floor), cell(r["n_new_test"], floor),
                       cell(r["n_new_test_p"], floor)]) + " |"


def format_split(split: pd.DataFrame, names: dict, meta: dict, *,
                 floor: int = EGRESS_FLOOR) -> list[str]:
    """Report lines for the --after section. Tables start with 'split class' / 'split
    Mondo' so the events plots ignore them."""
    d = meta["after"]
    span = meta.get("split_span") or {}
    months = lambda v: "?" if v is None else f"{v / 30.44:.1f}"
    L = [f"## Prospective split at {d}", "",
         f"Known = diagnosed and with a Fitbit day before {d} (would be in a release cut "
         f"then); new = everyone else in the cohort with Fitbit days after dx on or after "
         f"{d}. Train = covered episodes after dx and before {d}; test = covered episodes "
         f"on or after {d}. Follow-up after the split: about "
         f"{months(span.get('wear_days_span'))} months of Fitbit data and "
         f"{months(span.get('visit_days_span'))} months of visits. \"Known\" is by date "
         "only, so it slightly overcounts persons in the earlier release (late EHR records, "
         "Fitbit history synced later); test counts are exact. Columns are nested.", "",
         f"| split class | {SPLIT_HEAD}", "|---|" + "--:|" * 10]
    for _, r in split[split["mondo_id"] == ALL].iterrows():
        L.append(f"| {r['event_class']} | {_split_row(r, floor)}")
    a = split[(split["mondo_id"] == ALL) & (split["event_class"] == "ed_or_inpatient")]
    if len(a):
        L += ["", f"Known persons' Fitbit days on or after {d}: {int(a.iloc[0]['wd_post']):,}"]
    dd = split[(split["mondo_id"] != ALL) & (split["event_class"] == "ed_or_inpatient")
               & (split["n_known"] + split["n_new"] >= floor)]
    L += ["", f"By disease, ed_or_inpatient (known + new persons >= {floor}):", "",
          f"| split Mondo | disease | {SPLIT_HEAD}", "|---|---|" + "--:|" * 10]
    for _, r in dd.sort_values("n_known", ascending=False).iterrows():
        L.append(f"| {r['mondo_id']} | {str(names.get(r['mondo_id'], r['mondo_id']))[:44]} | "
                 f"{_split_row(r, floor)}")
    return L + [""]


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
                  meta: dict, *, sites: pd.DataFrame | None = None,
                  split: pd.DataFrame | None = None, floor: int = EGRESS_FLOOR, top_visit_types: int = 15) -> str:
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
    L += [f"Event = an acute-care episode: ED / inpatient visit starts, with visits less "
          f"than {meta['washout'] + 1} days apart merged, dated by its first day. After / "
          "before = strictly after / before the first diagnosis (the dx day itself is "
          f"excluded). Covered = >= {mc} Fitbit days in the {lb} days before the event. "
          "Cohort = persons with the disease and any Fitbit day. Columns are nested: check differences before "
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
    for cls in ("ed_or_inpatient",):
        L += [f"### {cls}", "", f"| Mondo | disease | with data | {EVENT_HEAD}",
              "|---|---|--:|" + "--:|" * 8]
        for m in show["mondo_id"]:
            r = d[(d["mondo_id"] == m) & (d["event_class"] == cls)].iloc[0]
            L.append(f"| {m} | {str(names.get(m, m))[:44]} | {cell(r['n_wear'], floor)} | "
                     f"{_row(r, floor)}")
        L.append("")

    if split is not None:
        L += format_split(split, names, meta, floor=floor)

    L += ["## By EHR source (all selected diseases)", ""]
    if sites is None:
        L += ["No EHR source column found (no `*_ext` table with `src_id` for visits).", ""]
    else:
        big = sites[sites["n_persons"] >= floor]
        L += [f"Source = `src_id` in `{meta.get('site_table')}` (All of Us obfuscated EHR "
              "source, shown here only by rank). Persons are counted at the source holding "
              "most of their visits; covered ED / inpatient episodes after dx at the source "
              "of the episode's first day. Other `*_ext` tables with `src_id`: "
              f"{', '.join(meta.get('site_tables', [])) or 'none'}.", "",
              f"Sources: {len(sites):,} · with >= {floor} cohort persons: {len(big):,} · "
              f"with >= {floor} persons with a covered episode: "
              f"{int((sites['n_cov_p'] >= floor).sum()):,}", "",
              "| source | cohort persons | covered episodes | persons with one |",
              "|---|--:|--:|--:|"]
        for _, r in sites.iterrows():
            L.append(f"| {r['site']} | {cell(r['n_persons'], floor)} | "
                     f"{cell(r['n_cov'], floor)} | {cell(r['n_cov_p'], floor)} |")
        L.append("")

    L += [f"## Visit types for the cohort (top {top_visit_types} by visits)", "",
          "| visit concept | name | visits | persons |", "|--:|---|--:|--:|"]
    for _, r in vtypes.head(top_visit_types).iterrows():
        L.append(f"| {r['visit_concept_id']} | {r['concept_name']} | "
                 f"{cell(r['n_visits'], floor)} | {cell(r['n_persons'], floor)} |")
    return "\n".join(L) + "\n"


def _site_diagnostics(client, cdr, ctes, params, ranks, meta, args, out, tag) -> None:
    from audits import wearables_site_diag as sd
    dctes = ctes + sd.diag_ctes()
    dp = {**params, "lookback": ("INT64", int(args.lookback)),
          "min_cov": ("INT64", int(args.min_cov))}
    print("[events] site diagnostics: episodes query…", flush=True)
    eps = sd.label_episodes(query(client, dctes + sd.DIAG_EPISODES_SELECT, dp), ranks)
    ps = sd.per_site(eps)
    focus = sd.pick_focus(ps, args.focus_site or None)
    src = ranks.loc[ranks["site"] == focus, "src_id"]
    if focus is None or src.empty:
        print(f"[events] site diagnostics: no focus source ({focus!r})", flush=True)
        return
    fp = {**dp, "focus": ("STRING", str(src.iloc[0]))}
    print(f"[events] site diagnostics: {focus} visit types / concepts…", flush=True)
    vt = query(client, dctes + sd.DIAG_VISIT_TYPES_SELECT.format(cdr=cdr), fp)
    concepts = query(client, dctes + sd.DIAG_CONCEPTS_SELECT.format(cdr=cdr), fp)
    text = sd.format_diag(eps, ps, focus, vt, concepts,
                          {**meta, "focus_given": bool(args.focus_site)})
    (out / f"{tag}_site-diag-report.md").write_text(text)
    print(text, flush=True)
    print(f"[events] wrote {out}/{tag}_site-diag-report.md", flush=True)


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
    p.add_argument("--washout", type=int, default=7,
                   help="visit starts within this many days of the previous one join its "
                        "episode")
    p.add_argument("--after", default="",
                   help="YYYY-MM-DD: also report a prospective split at this date (e.g. "
                        "the previous CDR's data cutoff)")
    p.add_argument("--site-diagnostics", action="store_true",
                   help="also write <run>_site-diag-report.md (see wearables_site_diag)")
    p.add_argument("--focus-site", default="",
                   help="'site N' label (from the events report) for the diagnostics; "
                        "default: most episodes per person")
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
    site_tables = list(query(client, SITE_TABLES_SELECT.format(cdr=cdr), {})["table_name"])
    site_table = "visit_occurrence_ext" if "visit_occurrence_ext" in site_tables else None
    print(f"[events] EHR source tables: {site_tables or 'none'}", flush=True)
    ctes = (timing_ctes(cdr, wear_sql, descendants=not args.no_descendants)
            + events_ctes(site_table).replace("{cdr}", cdr))
    params = {"mondo": ("STRING", rmap["mondo_id"].tolist()),
              "cid": ("INT64", [int(c) for c in rmap["standard_concept_id"]]),
              "min_dx_dates": ("INT64", int(args.min_dx_dates)),
              "washout": ("INT64", int(args.washout))}
    print("[events] diagnosis counts query…", flush=True)
    n_dx = query(client, ctes + N_DX_SELECT, params)
    print("[events] exposure query…", flush=True)
    expo = query(client, ctes + EXPOSURE_SELECT, params)
    print("[events] events query…", flush=True)
    ev = query(client, ctes + EVENTS_SELECT,
               {**params, "lookback": ("INT64", int(args.lookback))})
    print("[events] visit types query…", flush=True)
    vtypes = query(client, ctes + VISIT_TYPES_SELECT.format(cdr=cdr), params)

    sites = None
    if site_table:
        print("[events] EHR source query…", flush=True)
        psite = query(client, ctes + PERSON_SITE_SELECT.format(cdr=cdr, site_table=site_table),
                      params)
        ranks = site_ranks(ev, psite, expo, min_cov=args.min_cov)
        sites = ranks.drop(columns="src_id")
    split = None
    if args.after:
        sp = {**params, "split": ("DATE", args.after)}
        print(f"[events] split queries at {args.after}…", flush=True)
        sev = query(client, ctes + SPLIT_EVENTS_SELECT,
                    {**sp, "lookback": ("INT64", int(args.lookback))})
        sexpo = query(client, ctes + SPLIT_EXPOSURE_SELECT, sp)
        span = query(client, ctes + SPLIT_SPAN_SELECT, sp)
        split = split_summary(sev, sexpo, n_dx, min_cov=args.min_cov)
    summ = summarize(ev, expo, n_dx, min_cov=args.min_cov)
    cov = {"ed_or_inpatient": coverage_bins(ev, "ed_or_inpatient")}
    meta = {"cdr": cdr, "wear_tables": found, "flags": flags, "under": roots,
            "exact": args.exact, "descendants": not args.no_descendants,
            "min_dx_dates": args.min_dx_dates, "lookback": args.lookback,
            "min_cov": args.min_cov, "washout": args.washout,
            "site_table": site_table, "site_tables": site_tables,
            "after": args.after or None,
            "split_span": ({k: (None if pd.isna(v) else int(v))
                            for k, v in span.iloc[0].items()} if split is not None else None),
            "n_rare_nodes": int(rmap["mondo_id"].nunique())}
    tag = args.tag or run_name(roots, names, flags, exact=args.exact,
                               descendants=not args.no_descendants,
                               min_dx_dates=args.min_dx_dates)
    meta["run"] = tag
    text = format_report(summ, vtypes, cov, names, meta, sites=sites, split=split)
    (out / f"{tag}_events-report.md").write_text(text)
    masked_table(summ, names).to_csv(out / f"{tag}_events-table.tsv", sep="\t", index=False)
    mask_counts(vtypes, ["n_visits", "n_persons"]).to_csv(
        out / f"{tag}_visit-types.tsv", sep="\t", index=False)
    if sites is not None:
        mask_counts(sites, ["n_persons", "n_cov", "n_cov_p"]).to_csv(
            out / f"{tag}_sites.tsv", sep="\t", index=False)
    if split is not None:
        masked_split_table(split, names).to_csv(out / f"{tag}_split-table.tsv", sep="\t",
                                                index=False)
    (out / f"{tag}_events-run.json").write_text(json.dumps(meta, indent=1, default=str))
    if args.site_diagnostics:
        if not site_table:
            print("[events] no EHR source table: skipping site diagnostics", flush=True)
        else:
            _site_diagnostics(client, cdr, ctes, params, ranks, meta, args, out, tag)
    try:  # plots are drawn from the masked report text only
        from audits.wearables_events_plots import write_plots
        for path in write_plots(text, out, prefix=f"{tag}_events-plot-"):
            print(f"[events] plot {path}", flush=True)
    except ImportError as e:
        print(f"[events] no plots ({e}); install matplotlib or run "
              "`make plot-wearables-events REPORT=...` locally", flush=True)
    print(text, flush=True)
    print(f"[events] wrote {out}/{tag}_events-report.md, _events-table.tsv, "
          f"_visit-types.tsv (cells 1-19 as <20)", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
