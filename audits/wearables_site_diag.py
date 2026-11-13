"""EHR-source diagnostics for the wearables x ED / inpatient events audit: is one site's
coding inflating the event counts, and has it done so all along?

Run through `wearables_events.py --site-diagnostics` (it reuses that run's CTEs, its
covered-episode definition and its site ranks, so "site 6" means the same source in both
reports). Episodes here are the pooled (ALL) cohort's covered ED / inpatient episodes
after the first dx; each belongs to the source of its first day.

Report (`<run>_site-diag-report.md`):
  1. per source (>= floor persons with an episode): episodes per person (median, 90th
     percentile), days between a person's consecutive episodes (median), visit days and
     visit rows per episode (median), episodes with an inpatient row and those whose
     longest inpatient row ends the day it starts (no overnight stay)
  2. the FOCUS source (default: most episodes per person among those sources; or
     --focus-site 'site N') against all other sources: episodes by start year (was it
     there before the V8 cutoff?), days between consecutive episodes in bins (periodic
     care such as infusions or dialysis shows up as a 7-30 day spike), visit concepts on
     the episodes' visit rows, and the conditions and procedures most often recorded on
     those visits.
  3. pooled covered episodes and persons with and without the focus source.

EGRESS: counts through `cell`; medians and percentiles of person-level values are shown
only where >= floor persons stand behind them. No ratios are published. Person ids stay
in BigQuery (rows keyed by the run's rank), and src_id never leaves memory.
"""
from __future__ import annotations

import pandas as pd

from audits.wearables_timing import ALL
from rapidaudit.egress import EGRESS_FLOOR, cell

GAP_BINS = (8, 14, 21, 31, 61, 181)   # lower edges, days between consecutive episodes


def diag_ctes() -> str:
    """Appended after `events_ctes(site_table)`. Params: @lookback, @min_cov INT64 and
    @ip_overnight BOOL (as in the events audit: keep ED episodes and inpatient ones
    spanning a night).
    `ep_rows` = acute visit rows with their episode number; `dep` = the pooled cohort's
    covered episodes after the first dx, one row each."""
    return f""",
ep_rows AS (
  SELECT v.person_id, a.ep, v.visit_occurrence_id, v.visit_concept_id, v.vd, v.ved,
         v.is_ed, v.is_ip, v.site, IFNULL(s.stay, FALSE) AS ip_stay
  FROM vis v
  JOIN acute_ep a ON a.person_id = v.person_id AND a.vd = v.vd
  LEFT JOIN ip_stay s ON s.person_id = v.person_id AND s.vd = v.vd),
ep AS (
  SELECT person_id, ep, MIN(vd) AS start, COUNT(DISTINCT vd) AS n_days,
         COUNT(*) AS n_rows, COUNTIF(is_ip) AS n_ip_rows,
         MAX(IF(is_ip, DATE_DIFF(ved, vd, DAY), NULL)) AS max_ip_los,
         LOGICAL_OR(is_ed) AS has_ed,
         LOGICAL_OR(ip_stay) AS ip_night,
         ARRAY_AGG(site IGNORE NULLS ORDER BY vd, site LIMIT 1)[SAFE_OFFSET(0)] AS site
  FROM ep_rows
  GROUP BY person_id, ep),
dep AS (
  SELECT e.person_id, e.ep, e.start, e.n_days, e.n_rows, e.n_ip_rows, e.max_ip_los,
         e.site, COUNT(w.d) AS cov_days
  FROM ep e
  JOIN dx_all x ON x.person_id = e.person_id AND x.mondo_id = '{ALL}'
                AND e.start > x.first_dx
  LEFT JOIN wdays w ON w.person_id = e.person_id
    AND w.d >= DATE_SUB(e.start, INTERVAL @lookback DAY) AND w.d < e.start
  WHERE NOT @ip_overnight OR e.has_ed OR e.ip_night
  GROUP BY e.person_id, e.ep, e.start, e.n_days, e.n_rows, e.n_ip_rows, e.max_ip_los,
           e.site
  HAVING COUNT(w.d) >= @min_cov)
"""


# One row per covered episode (pooled cohort, after dx).
DIAG_EPISODES_SELECT = """
SELECT p.pid, d.site, d.start, d.n_days, d.n_rows, d.n_ip_rows, d.max_ip_los
FROM dep d
JOIN pids p ON p.person_id = d.person_id
"""

# Visit concepts on the covered episodes' visit rows, focus source (@focus) vs others.
DIAG_VISIT_TYPES_SELECT = """
SELECT IF(d.site = @focus, 'focus', 'other') AS grp, r.visit_concept_id, c.concept_name,
       COUNT(*) AS n_rows, COUNT(DISTINCT d.person_id) AS n_persons
FROM dep d
JOIN ep_rows r ON r.person_id = d.person_id AND r.ep = d.ep
LEFT JOIN `{cdr}.concept` c ON c.concept_id = r.visit_concept_id
GROUP BY grp, r.visit_concept_id, c.concept_name
"""

# Conditions and procedures recorded on those visits, focus vs others: episodes and
# persons with the concept.
DIAG_CONCEPTS_SELECT = """
SELECT IF(h.site = @focus, 'focus', 'other') AS grp, h.domain, h.concept_id,
       c.concept_name,
       COUNT(DISTINCT FORMAT('%d-%d', h.person_id, h.ep)) AS n_eps,
       COUNT(DISTINCT h.person_id) AS n_persons
FROM (
  SELECT d.person_id, d.ep, d.site, 'condition' AS domain,
         co.condition_concept_id AS concept_id
  FROM dep d
  JOIN ep_rows r ON r.person_id = d.person_id AND r.ep = d.ep
  JOIN `{cdr}.condition_occurrence` co ON co.visit_occurrence_id = r.visit_occurrence_id
  UNION ALL
  SELECT d.person_id, d.ep, d.site, 'procedure' AS domain,
         po.procedure_concept_id AS concept_id
  FROM dep d
  JOIN ep_rows r ON r.person_id = d.person_id AND r.ep = d.ep
  JOIN `{cdr}.procedure_occurrence` po ON po.visit_occurrence_id = r.visit_occurrence_id
) h
LEFT JOIN `{cdr}.concept` c ON c.concept_id = h.concept_id
WHERE h.concept_id != 0
GROUP BY grp, h.domain, h.concept_id, c.concept_name
"""


def _gaps(eps: pd.DataFrame) -> pd.Series:
    """Days between a person's consecutive covered episodes (any source)."""
    e = eps.sort_values(["pid", "start"])
    d = pd.to_datetime(e["start"]).groupby(e["pid"]).diff().dt.days
    return d.dropna()


def label_episodes(eps: pd.DataFrame, ranks: pd.DataFrame) -> pd.DataFrame:
    """Adds `label` (the events report's 'site N') from `site_ranks` output."""
    lab = dict(zip(ranks["src_id"], ranks["site"]))
    out = eps.copy()
    out["label"] = out["site"].map(lambda s: lab.get(s, "no source") if pd.notna(s)
                                   else "no source")
    return out


def per_site(eps: pd.DataFrame, floor: int = EGRESS_FLOOR) -> pd.DataFrame:
    """Raw per-source rows for sources with >= floor persons with an episode. Gaps are
    within a person, between consecutive episodes both recorded at that source."""
    rows = []
    for lab, e in eps.groupby("label", sort=False):
        n_p = e["pid"].nunique()
        if n_p < floor:
            continue
        per_p = e.groupby("pid").size()
        ip = e[e["n_ip_rows"] > 0]
        g = _gaps(e)
        rows.append({
            "site": lab, "n_p": n_p, "n_eps": len(e),
            "eps_per_p_med": float(per_p.median()), "eps_per_p_p90": float(per_p.quantile(0.9)),
            "gap_med": float(g.median()) if len(g) >= floor else None,
            "days_med": float(e["n_days"].median()), "rows_med": float(e["n_rows"].median()),
            "n_ip_eps": len(ip), "n_ip_sameday": int((ip["max_ip_los"] <= 0).sum()),
            "_rate": len(e) / n_p})
    return pd.DataFrame(rows)


def pick_focus(ps: pd.DataFrame, focus: str | None = None) -> str | None:
    if focus:
        return focus
    return None if ps.empty else ps.sort_values("_rate", ascending=False)["site"].iloc[0]


def by_year(eps: pd.DataFrame, focus: str) -> pd.DataFrame:
    """Covered episodes and persons by start year: focus source vs all others."""
    e = eps.assign(year=pd.to_datetime(eps["start"]).dt.year,
                   grp=lambda x: x["label"].eq(focus).map({True: "focus", False: "other"}))
    g = e.groupby(["year", "grp"]).agg(n_eps=("pid", "size"), n_p=("pid", "nunique"))
    g = g.unstack("grp").fillna(0).astype(int)
    g.columns = [f"{a}_{b}" for a, b in g.columns]
    for c in ("n_eps_focus", "n_p_focus", "n_eps_other", "n_p_other"):
        if c not in g:
            g[c] = 0
    return g.sort_index()


def gap_bins(eps: pd.DataFrame, focus: str, edges=GAP_BINS) -> pd.DataFrame:
    hi = list(edges[1:]) + [None]
    labs = [f"{lo}-{h - 1}" if h else f"{lo}+" for lo, h in zip(edges, hi)]
    out = {}
    for grp, e in (("focus", eps[eps["label"] == focus]), ("other", eps[eps["label"] != focus])):
        g = _gaps(e)
        out[grp] = [int(((g >= lo) & ((g < h) if h else True)).sum())
                    for lo, h in zip(edges, hi)]
    return pd.DataFrame(out, index=labs)


def format_diag(eps: pd.DataFrame, ps: pd.DataFrame, focus: str, vt: pd.DataFrame,
                concepts: pd.DataFrame, meta: dict, *, floor: int = EGRESS_FLOOR,
                top: int = 15) -> str:
    f = lambda v: "—" if v is None or pd.isna(v) else f"{v:g}"
    L = ["# EHR source diagnostics: ED / inpatient episodes (All of Us)", "",
         f"CDR: `{meta['cdr']}` · run `{meta['run']}` · source = `src_id` in "
         f"`{meta['site_table']}`, labels as in that run's events report", "",
         f"Episodes = the pooled cohort's covered ED / inpatient episodes after the first "
         f"dx (>= {meta['min_cov']} Fitbit days in the {meta['lookback']} days before; "
         f"visits less than {meta['washout'] + 1} days apart merged"
         + ("; inpatient only with a stay: a row ending after its start day or rows on "
            "consecutive days" if meta.get("ip_overnight") else "")
         + "), each at the source of "
         "its first day. Medians and percentiles are over persons or episodes at that "
         f"source and only shown where >= {floor} persons stand behind them. Columns are "
         "nested: check differences before sharing.", ""]

    L += [f"## Per source (>= {floor} persons with an episode)", "",
          "| source | persons | episodes | episodes / person, median | 90th pct | "
          "days between episodes, median | visit days / episode, median | "
          "visit rows / episode, median | episodes with inpatient row | "
          "of those, no single row spanning a night |", "|---|" + "--:|" * 9]
    for _, r in ps.sort_values("n_eps", ascending=False).iterrows():
        L.append(f"| {r['site']} | {cell(r['n_p'], floor)} | {cell(r['n_eps'], floor)} | "
                 f"{f(r['eps_per_p_med'])} | {f(r['eps_per_p_p90'])} | {f(r['gap_med'])} | "
                 f"{f(r['days_med'])} | {f(r['rows_med'])} | {cell(r['n_ip_eps'], floor)} | "
                 f"{cell(r['n_ip_sameday'], floor)} |")

    L += ["", f"## Focus: {focus} against all other sources", "",
          ("Chosen with --focus-site." if meta.get("focus_given") else
           "Chosen as the source with the most episodes per person among those above."), "",
          "### Episodes by start year", "",
          "| year | focus episodes | persons | other episodes | persons |", "|--:|--:|--:|--:|--:|"]
    for y, r in by_year(eps, focus).iterrows():
        L.append(f"| {y} | {cell(r['n_eps_focus'], floor)} | {cell(r['n_p_focus'], floor)} | "
                 f"{cell(r['n_eps_other'], floor)} | {cell(r['n_p_other'], floor)} |")

    L += ["", "### Days between a person's consecutive episodes (same group)", "",
          "| days | focus | other |", "|---|--:|--:|"]
    for lab, r in gap_bins(eps, focus).iterrows():
        L.append(f"| {lab} | {cell(r['focus'], floor)} | {cell(r['other'], floor)} |")

    L += ["", "### Visit concepts on the episodes' visit rows", "",
          "| visit concept | name | focus rows | persons | other rows | persons |",
          "|--:|---|--:|--:|--:|--:|"]
    L += _paired(vt, ["visit_concept_id", "concept_name"], "n_rows", floor, top)

    for dom in ("condition", "procedure"):
        c = concepts[concepts["domain"] == dom]
        L += ["", f"### Top {dom}s on the focus source's episode visits (by episodes)", "",
              f"| concept | name | focus episodes | persons | other episodes | persons |",
              "|--:|---|--:|--:|--:|--:|"]
        L += _paired(c, ["concept_id", "concept_name"], "n_eps", floor, top)

    oth = eps[eps["label"] != focus]
    L += ["", "## Pooled episodes with and without the focus source", "",
          "| | episodes | persons with one |", "|---|--:|--:|",
          f"| all sources | {cell(len(eps), floor)} | {cell(eps['pid'].nunique(), floor)} |",
          f"| without {focus} | {cell(len(oth), floor)} | {cell(oth['pid'].nunique(), floor)} |",
          "", "Persons can have episodes at more than one source, so the rows overlap."]
    return "\n".join(L) + "\n"


def _paired(df: pd.DataFrame, keys: list, count: str, floor: int, top: int) -> list:
    """Rows ranked by the focus group's `count`, with the other group alongside."""
    if df.empty:
        return []
    w = df.pivot_table(index=keys, columns="grp", values=[count, "n_persons"],
                       aggfunc="sum", fill_value=0)
    w.columns = [f"{a}_{b}" for a, b in w.columns]
    for c in (f"{count}_focus", "n_persons_focus", f"{count}_other", "n_persons_other"):
        if c not in w:
            w[c] = 0
    w = w.sort_values(f"{count}_focus", ascending=False).head(top)
    return [f"| {k[0]} | {str(k[1])[:50]} | {cell(r[f'{count}_focus'], floor)} | "
            f"{cell(r['n_persons_focus'], floor)} | {cell(r[f'{count}_other'], floor)} | "
            f"{cell(r['n_persons_other'], floor)} |" for k, r in w.iterrows()]
