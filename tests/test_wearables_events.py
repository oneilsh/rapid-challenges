"""Wearables x ED / inpatient events helpers (audits/wearables_events.py)."""
import pandas as pd

from audits import wearables_events as we
from audits import wearables_rare as dw
from audits import wearables_timing as wt


def _ev():
    """Disease M:1 (ALL mirrors it): 25 persons each with one ED visit 10 days after dx,
    fully covered (30 Fitbit days in the lookback); persons 0-4 have a second, inpatient
    visit at day 40 with 3 covered days; persons 0-21 an ED visit before dx. Episodes of
    persons 0-19 are recorded at EHR source 'EHR site 7', the rest at 'EHR site 3'."""
    rows = []
    for m in ("M:1", wt.ALL):
        for pid in range(25):
            site = "EHR site 7" if pid < 20 else "EHR site 3"
            rows.append((pid, m, 10, True, False, site, 30))
            if pid < 5:
                rows.append((pid, m, 40, False, True, site, 3))
            if pid < 22:
                rows.append((pid, m, -100, True, False, site, 20))
            rows.append((pid, m, 0, True, True, site, 30))     # dx day: excluded
    return pd.DataFrame(rows, columns=["pid", "mondo_id", "rel_day", "is_ed", "is_ip",
                                       "site", "cov_days"])


def _psite():
    """Primary EHR source per person: 0-19 site 7, 20-27 site 3, 28-29 a portal."""
    return pd.DataFrame({"pid": range(30), "primary_site": ["EHR site 7"] * 20
                         + ["EHR site 3"] * 8 + ["Participant Portal: PTSC"] * 2})


def _expo():
    return pd.DataFrame([(pid, m, 100, 400) for m in ("M:1", wt.ALL) for pid in range(30)],
                        columns=["pid", "mondo_id", "wd_before", "wd_after"])


def _n_dx():
    return pd.DataFrame({"mondo_id": ["M:1", wt.ALL], "n_dx": [300, 300]})


def test_summarize_counts_covered_and_repeat_events():
    s = we.summarize(_ev(), _expo(), _n_dx(), min_cov=14).set_index(["mondo_id", "event_class"])
    a = s.loc[(wt.ALL, "ed_or_inpatient")]
    assert (a["n_wear"], a["wear_days_after"]) == (30, 12_000)
    assert (a["n_ev"], a["n_ev_p"], a["n_cov"], a["n_cov_p"], a["n_cov_p2"]) == (30, 25, 25, 25, 0)
    assert a["cov_per_1k"] == round(1000 * 25 / 12_000, 2)
    assert (a["n_cov_pre"], a["n_cov_pre_p"]) == (22, 22)
    r = s.loc[("M:1", "inpatient")]
    assert (r["n_ev"], r["n_cov"]) == (5, 0) and pd.isna(r["cov_per_1k"])
    assert set(s.index.get_level_values(1)) == {"ed_or_inpatient", "ed", "inpatient"}
    assert list(s.index.get_level_values(0))[0] == wt.ALL


def test_coverage_bins_and_report():
    ev = _ev()
    bins = we.coverage_bins(ev, "ed_or_inpatient")
    assert bins == {"0": 0, "1-6": 5, "7-13": 0, "14-20": 0, "21+": 25}
    s = we.summarize(ev, _expo(), _n_dx(), min_cov=14)
    vt = pd.DataFrame({"visit_concept_id": [9202, 9203], "concept_name": ["Outpatient", "ER"],
                       "n_visits": [5000, 12], "n_persons": [30, 12]})
    meta = {"cdr": "p.ds", "wear_tables": ["activity_summary"], "flags": ["x"],
            "n_rare_nodes": 1, "lookback": 30, "min_cov": 14, "washout": 7}
    md = we.format_report(s, vt, {"ed_or_inpatient": bins}, {"M:1": "foo"}, meta)
    assert "| ed_or_inpatient | 30 | 25 | 25 | 25 | 0 | 2.08 | 22 | 22 |" in md
    assert "| M:1 | foo | 30 |" in md and "| 9203 | ER | <20 | <20 |" in md
    assert "| ed_or_inpatient | 0 | <20 | 0 | 0 | 25 |" in md
    t = we.masked_table(s, {"M:1": "foo"}).set_index(["mondo_id", "event_class"])
    assert t.loc[("M:1", "inpatient"), "n_ev"] == "<20"
    assert t.loc[("M:1", "inpatient"), "cov_per_1k"] == ""


def test_site_summary_ranks_sources_and_hides_codes():
    sites = we.site_summary(_ev(), _psite(), _expo(), min_cov=14)
    assert list(sites["site"]) == ["site 1", "site 2", "Participant Portal: PTSC"]
    assert list(sites["n_persons"]) == [20, 8, 2]
    assert list(sites["n_cov"]) == [20, 5, 0] and list(sites["n_cov_p"]) == [20, 5, 0]
    meta = {"cdr": "p.ds", "wear_tables": ["activity_summary"], "flags": ["x"],
            "n_rare_nodes": 1, "lookback": 30, "min_cov": 14, "washout": 7,
            "site_table": "visit_occurrence_ext", "site_tables": ["visit_occurrence_ext"]}
    s = we.summarize(_ev(), _expo(), _n_dx(), min_cov=14)
    vt = pd.DataFrame({"visit_concept_id": [9203], "concept_name": ["ER"],
                       "n_visits": [40], "n_persons": [25]})
    md = we.format_report(s, vt, {}, {"M:1": "foo"}, meta, sites=sites)
    assert "| site 1 | 20 | 20 | 20 |" in md and "| site 2 | <20 | <20 | <20 |" in md
    assert "Sources: 3 · with >= 20 cohort persons: 1" in md
    assert "EHR site 7" not in md and "EHR site 3" not in md


def test_events_sql_parses():
    sqlglot = __import__("pytest").importorskip("sqlglot")
    sql, _ = wt.typed_wear_sql("p.ds", {"activity_summary": {"date"}}, intraday=False)
    ctes = wt.timing_ctes("p.ds", sql) + we.events_ctes().replace("{cdr}", "p.ds")
    for body in (we.EVENTS_SELECT, we.EXPOSURE_SELECT,
                 we.VISIT_TYPES_SELECT.format(cdr="p.ds"), wt.N_DX_SELECT):
        sqlglot.parse_one(ctes + body, read="bigquery")
    site_ctes = (wt.timing_ctes("p.ds", sql)
                 + we.events_ctes("visit_occurrence_ext").replace("{cdr}", "p.ds"))
    assert "LEFT JOIN `p.ds.visit_occurrence_ext` vx" in site_ctes
    for body in (we.EVENTS_SELECT,
                 we.PERSON_SITE_SELECT.format(cdr="p.ds", site_table="visit_occurrence_ext")):
        sqlglot.parse_one(site_ctes + body, read="bigquery")
    sqlglot.parse_one(we.SITE_TABLES_SELECT.format(cdr="p.ds"), read="bigquery")
    assert "{cdr}" not in ctes and " IN (SELECT" not in ctes
    assert "IN (9203, 262, 8870)" in ctes and "IN (9201, 262, 8717)" in ctes
    assert "COUNTIF(new_ep) OVER (PARTITION BY person_id ORDER BY vd)" in ctes
    assert "NOT @ip_overnight" in ctes and "MAX(e.ip_end) > MIN(e.ip_start)" in ctes


def test_main_end_to_end_with_fake_bigquery(tmp_path, monkeypatch):
    sc = "biolink:subclass_of"
    nodes = pd.DataFrame(
        [("MONDO:0700096", "biolink:Disease", "human disease", None, None),
         ("MONDO:AI", "biolink:Disease", "autoimmune thing", None, None),
         ("MONDO:A", "biolink:Disease", "disease A",
          "http://identifiers.org/snomedct/123", "rare|orphanet_rare")],
        columns=["id", "category", "name", "same_as", "subsets"])
    edges = pd.DataFrame([("MONDO:AI", "MONDO:0700096", sc), ("MONDO:A", "MONDO:AI", sc)],
                         columns=["subject", "object", "predicate"])
    files = {"mondo_nodes.tsv": tmp_path / "n.tsv", "mondo_edges.tsv": tmp_path / "e.tsv"}
    nodes.to_csv(files["mondo_nodes.tsv"], sep="\t", index=False)
    edges.to_csv(files["mondo_edges.tsv"], sep="\t", index=False)
    concept = pd.DataFrame([(123, "Std A", "SNOMED", "Condition", "123", "S")],
                           columns=["concept_id", "concept_name", "vocabulary_id",
                                    "domain_id", "concept_code", "standard_concept"])
    seen = {}

    def fake_query(client, sql, params=None):
        if "d.max_ip_los" in sql and "AS grp" not in sql:
            eps = []
            for pid in range(20):
                for k in range(3):
                    eps.append((pid, "EHR site 7", f"2022-0{k + 1}-01", 1, 1, 1, 0))
            for pid in range(20, 45):
                eps.append((pid, "EHR site 3", "2021-05-01", 2, 3, 1, 2))
            return pd.DataFrame(eps, columns=["pid", "site", "start", "n_days", "n_rows",
                                              "n_ip_rows", "max_ip_los"])
        if "AS grp, r.visit_concept_id" in sql:
            seen["focus"] = params["focus"]
            return pd.DataFrame({"grp": ["focus"], "visit_concept_id": [9201],
                                 "concept_name": ["Inpatient Visit"], "n_rows": [60],
                                 "n_persons": [20]})
        if "AS grp, h.domain" in sql:
            return pd.DataFrame({"grp": ["focus"], "domain": ["procedure"],
                                 "concept_id": [5], "concept_name": ["Infusion"],
                                 "n_eps": [60], "n_persons": [20]})
        if "ENDS_WITH(table_name" in sql:
            return pd.DataFrame({"table_name": ["condition_occurrence_ext",
                                                "visit_occurrence_ext"]})
        if "primary_site" in sql:
            seen["site"] = sql
            return _psite()
        if "SELECT * FROM mt" in sql:
            return pd.DataFrame({"concept_id_1": [123], "concept_id_2": [123],
                                 "relationship_id": ["Maps to"]})
        if "UNION DISTINCT" in sql:
            return concept
        if "INFORMATION_SCHEMA" in sql:
            return pd.DataFrame({"table_name": ["activity_summary"], "column_name": ["date"]})
        if "wear_days_span" in sql:
            return pd.DataFrame({"wear_days_span": [457], "visit_days_span": [450]})
        if "split_day" in sql and "cov_days" in sql:
            seen["split"] = params
            return _split_rows()[0].replace({"M:1": "MONDO:A"})
        if "wd_pre" in sql:
            return _split_rows()[1].replace({"M:1": "MONDO:A"})
        if "cov_days" in sql:
            seen["ev"] = params
            return _ev().replace({"M:1": "MONDO:A"})
        if "wd_after" in sql:
            return _expo().replace({"M:1": "MONDO:A"})
        if "n_visits" in sql:
            return pd.DataFrame({"visit_concept_id": [9203], "concept_name": ["ER"],
                                 "n_visits": [40], "n_persons": [25]})
        return pd.DataFrame({"mondo_id": ["MONDO:A", wt.ALL], "n_dx": [300, 300]})

    monkeypatch.setenv("WORKSPACE_CDR", "p.ds")
    monkeypatch.setenv("GOOGLE_CLOUD_PROJECT", "bill")
    monkeypatch.setattr(we, "bq_client", lambda billing: object())
    monkeypatch.setattr(we, "query", fake_query)
    monkeypatch.setattr(dw, "query", fake_query)
    monkeypatch.setattr(dw, "download_cached", lambda v, f, c: files[f])
    out = tmp_path / "out"
    assert we.main(["--out-dir", str(out), "--flags", "orphanet_rare", "--under",
                    "MONDO:AI", "--exact", "--tag", "ai", "--after", "2023-10-01", "--site-diagnostics"]) == 0
    out = out / "ds"
    assert seen["ev"]["lookback"] == ("INT64", 30)
    assert seen["ev"]["washout"] == ("INT64", 7)
    assert seen["ev"]["ip_overnight"] == ("BOOL", False)
    md = (out / "ai_events-report.md").read_text()
    assert "| MONDO:A | disease A | 30 |" in md
    assert (out / "ai_events-table.tsv").exists() and (out / "ai_visit-types.tsv").exists()
    assert "`p.ds.visit_occurrence_ext`" in seen["site"]
    assert "| site 1 | 20 | 20 | 20 |" in md and (out / "ai_sites.tsv").exists()
    assert "EHR site 7" not in (out / "ai_sites.tsv").read_text()
    assert seen["split"]["split"] == ("DATE", "2023-10-01")
    assert "## Prospective split at 2023-10-01" in md and (out / "ai_split-table.tsv").exists()
    assert "| MONDO:A | disease A | 25 |" in md
    diag = (out / "ai_site-diag-report.md").read_text()
    assert seen["focus"] == ("STRING", "EHR site 7")
    assert "## Focus: site 1 against all other sources" in diag
    assert "EHR site" not in diag


def test_plots_read_only_the_masked_report(tmp_path):
    __import__("pytest").importorskip("matplotlib")
    from audits import wearables_events_plots as wp
    ev = _ev()
    s = we.summarize(ev, _expo(), _n_dx(), min_cov=14)
    vt = pd.DataFrame({"visit_concept_id": [9203], "concept_name": ["ER"],
                       "n_visits": [40], "n_persons": [25]})
    cov = {"ed_or_inpatient": we.coverage_bins(ev, "ed_or_inpatient")}
    meta = {"cdr": "p.ds", "wear_tables": ["activity_summary"], "flags": ["x"],
            "n_rare_nodes": 1, "lookback": 30, "min_cov": 14, "washout": 7}
    md = we.format_report(s, vt, cov, {"M:1": "foo"}, meta)
    t = wp.read_report(md)
    assert set(t["disease"]) == {"ed_or_inpatient"} and t["min_cov"] == 14
    assert "related" not in md and "### related" not in md
    assert "persons.1" in t["pooled"].columns and "coverage" in t
    paths = wp.write_plots(md, tmp_path, prefix="run_events-plot-")
    assert [p.name for p in paths] == ["run_events-plot-pooled.png",
                                       "run_events-plot-coverage.png",
                                       "run_events-plot-disease-persons.png",
                                       "run_events-plot-disease-rates.png"]


def _split_rows():
    """Split at day 0 of the calendar. Disease M:1 (ALL mirrors it):
    persons 0-24 known (dx at split day -50, wearing before), 0-19 still wearing after;
    each has a covered train episode (split day -10) and persons 0-9 a covered test
    episode (split day +20) plus an uncovered one (+60). Persons 25-29 are new (dx at
    split day +5) with a covered episode at +30; person 30 has dx before the split but
    no Fitbit until after it, so is new too, with a covered episode at +40."""
    ev, ex = [], []
    for m in ("M:1", wt.ALL):
        for pid in range(25):
            ex.append((pid, m, -50, 100, 300 if pid < 20 else 0))
            ev.append((pid, m, 40, True, False, None, 30, -10, -50))
            if pid < 10:
                ev.append((pid, m, 70, False, True, None, 20, 20, -50))
                ev.append((pid, m, 110, True, False, None, 2, 60, -50))
        for pid in range(25, 30):
            ex.append((pid, m, 5, 0, 200))
            ev.append((pid, m, 25, True, False, None, 25, 30, 5))
        ex.append((30, m, -20, 0, 150))
        ev.append((30, m, 60, True, False, None, 25, 40, -20))
    sev = pd.DataFrame(ev, columns=["pid", "mondo_id", "rel_day", "is_ed", "is_ip", "site",
                                    "cov_days", "split_day", "dx_split_day"])
    sexpo = pd.DataFrame(ex, columns=["pid", "mondo_id", "dx_split_day", "wd_pre", "wd_post"])
    return sev, sexpo


def test_split_summary_known_new_train_test():
    sev, sexpo = _split_rows()
    s = we.split_summary(sev, sexpo, _n_dx(), min_cov=14).set_index(["mondo_id", "event_class"])
    a = s.loc[(wt.ALL, "ed_or_inpatient")]
    assert (a["n_known"], a["n_known_post"], a["wd_post"]) == (25, 20, 6000)
    assert (a["n_train"], a["n_train_p"], a["n_test"], a["n_test_p"]) == (25, 25, 10, 10)
    assert pd.isna(a["test_per_1k"])          # 10 test episodes < floor: no rate
    assert (a["n_new"], a["n_new_test"], a["n_new_test_p"]) == (6, 6, 6)
    ip = s.loc[("M:1", "inpatient")]
    assert (ip["n_train"], ip["n_test"], ip["n_new_test"]) == (0, 10, 0)
    meta = {"after": "2023-10-01", "split_span": {"wear_days_span": 457,
                                                  "visit_days_span": 450}}
    md = "\n".join(we.format_split(we.split_summary(sev, sexpo, _n_dx(), min_cov=14),
                                   {"M:1": "foo"}, meta))
    assert "## Prospective split at 2023-10-01" in md and "about 15.0 months" in md
    assert "| ed_or_inpatient | 25 | 20 | 25 | 25 | <20 | <20 | — | <20 | <20 | <20 |" in md
    assert "| M:1 | foo | 25 |" in md
    t = we.masked_split_table(we.split_summary(sev, sexpo, _n_dx(), min_cov=14), {})
    assert set(t["n_test"]) == {"<20", "0"} and set(t["test_per_1k"]) == {""}


def test_split_sql_parses_and_plots_ignore_split_tables():
    sqlglot = __import__("pytest").importorskip("sqlglot")
    sql, _ = wt.typed_wear_sql("p.ds", {"activity_summary": {"date"}}, intraday=False)
    ctes = wt.timing_ctes("p.ds", sql) + we.events_ctes().replace("{cdr}", "p.ds")
    for body in (we.SPLIT_EVENTS_SELECT, we.SPLIT_EXPOSURE_SELECT, we.SPLIT_SPAN_SELECT):
        sqlglot.parse_one(ctes + body, read="bigquery")
    assert "DATE_DIFF(e.vd, @split, DAY) AS split_day" in we.SPLIT_EVENTS_SELECT
