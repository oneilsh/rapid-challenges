"""EHR source diagnostics (audits/wearables_site_diag.py)."""
import datetime as dt

import pandas as pd

from audits import wearables_events as we
from audits import wearables_site_diag as sd
from audits import wearables_timing as wt


def _eps():
    """Source 'A' (site 1): 25 persons, one episode each in 2021, 2 visit days, an
    inpatient row with a 3-day stay. Source 'B' (site 2): 20 persons with 10 episodes
    each every 14 days from 2019-01-01, one same-day inpatient row each."""
    rows = []
    for pid in range(25):
        rows.append((pid, "A", dt.date(2021, 3, 1), 2, 3, 1, 3))
    for pid in range(100, 120):
        for k in range(10):
            rows.append((pid, "B", dt.date(2019, 1, 1) + dt.timedelta(days=14 * k),
                         1, 1, 1, 0))
    return pd.DataFrame(rows, columns=["pid", "site", "start", "n_days", "n_rows",
                                       "n_ip_rows", "max_ip_los"])


def _ranks():
    return pd.DataFrame({"site": ["site 1", "site 2"], "src_id": ["A", "B"],
                         "n_persons": [25, 20], "n_cov": [25, 200], "n_cov_p": [25, 20]})


def test_per_site_focus_year_and_gaps():
    eps = sd.label_episodes(_eps(), _ranks())
    ps = sd.per_site(eps).set_index("site")
    assert ps.loc["site 2", "eps_per_p_med"] == 10 and ps.loc["site 2", "gap_med"] == 14
    assert pd.isna(ps.loc["site 1", "gap_med"]) and ps.loc["site 1", "days_med"] == 2
    assert (ps.loc["site 2", "n_ip_eps"], ps.loc["site 2", "n_ip_sameday"]) == (200, 200)
    assert ps.loc["site 1", "n_ip_sameday"] == 0
    assert sd.pick_focus(sd.per_site(eps)) == "site 2"
    assert sd.pick_focus(sd.per_site(eps), "site 1") == "site 1"
    y = sd.by_year(eps, "site 2")
    assert y.loc[2019, "n_eps_focus"] == 200 and y.loc[2021, "n_eps_other"] == 25
    g = sd.gap_bins(eps, "site 2")
    assert g.loc["14-20", "focus"] == 180 and g["other"].sum() == 0


def test_format_diag_masks_and_hides_source_codes():
    eps = sd.label_episodes(_eps(), _ranks())
    ps = sd.per_site(eps)
    vt = pd.DataFrame({"grp": ["focus", "other", "focus"],
                       "visit_concept_id": [9201, 9201, 9203],
                       "concept_name": ["Inpatient Visit", "Inpatient Visit", "ER"],
                       "n_rows": [200, 25, 5], "n_persons": [20, 25, 3]})
    concepts = pd.DataFrame({"grp": ["focus", "other"], "domain": ["procedure"] * 2,
                             "concept_id": [1, 1], "concept_name": ["Infusion"] * 2,
                             "n_eps": [190, 4], "n_persons": [20, 4]})
    meta = {"cdr": "p.ds", "run": "ai", "site_table": "visit_occurrence_ext",
            "min_cov": 14, "lookback": 30, "washout": 7}
    md = sd.format_diag(eps, ps, "site 2", vt, concepts, meta)
    assert "| site 2 | 20 | 200 | 10 | 10 | 14 | 1 | 1 | 200 | 200 |" in md
    assert "| 2019 | 200 | 20 | 0 | 0 |" in md
    assert "| 9201 | Inpatient Visit | 200 | 20 | 25 | 25 |" in md
    assert "| 9203 | ER | <20 | <20 | 0 | 0 |" in md
    assert "| 1 | Infusion | 190 | 20 | <20 | <20 |" in md
    assert "| without site 2 | 25 | 25 |" in md
    assert "| A |" not in md and "| B |" not in md


def test_diag_sql_parses():
    sqlglot = __import__("pytest").importorskip("sqlglot")
    sql, _ = wt.typed_wear_sql("p.ds", {"activity_summary": {"date"}}, intraday=False)
    ctes = (wt.timing_ctes("p.ds", sql)
            + we.events_ctes("visit_occurrence_ext").replace("{cdr}", "p.ds")
            + sd.diag_ctes())
    for body in (sd.DIAG_EPISODES_SELECT, sd.DIAG_VISIT_TYPES_SELECT.format(cdr="p.ds"),
                 sd.DIAG_CONCEPTS_SELECT.format(cdr="p.ds")):
        sqlglot.parse_one(ctes + body, read="bigquery")
        assert "WITH" not in body
    assert "WHERE NOT @ip_overnight OR e.has_ed OR e.ip_night" in ctes
    assert "mondo_id = 'ALL'" in ctes and "HAVING COUNT(w.d) >= @min_cov" in ctes
