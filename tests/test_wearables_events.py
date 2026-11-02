"""Wearables x ED / inpatient events helpers (audits/wearables_events.py)."""
import pandas as pd

from audits import wearables_events as we
from audits import wearables_rare as dw
from audits import wearables_timing as wt


def _ev():
    """Disease M:1 (ALL mirrors it): 25 persons each with one ED visit 10 days after dx,
    fully covered (30 Fitbit days in the lookback); persons 0-4 have a second, related
    inpatient visit at day 40 with 3 covered days; persons 0-21 an ED visit before dx."""
    rows = []
    for m in ("M:1", wt.ALL):
        for pid in range(25):
            rows.append((pid, m, 10, True, False, False, 30))
            if pid < 5:
                rows.append((pid, m, 40, False, True, True, 3))
            if pid < 22:
                rows.append((pid, m, -100, True, False, False, 20))
            rows.append((pid, m, 0, True, True, True, 30))           # dx day: excluded
    return pd.DataFrame(rows, columns=["pid", "mondo_id", "rel_day", "is_ed", "is_ip",
                                       "related", "cov_days"])


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
    r = s.loc[("M:1", "related")]
    assert (r["n_ev"], r["n_cov"]) == (5, 0) and pd.isna(r["cov_per_1k"])
    assert s.loc[("M:1", "inpatient"), "n_ev"] == 5
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
    assert t.loc[("M:1", "related"), "n_ev"] == "<20"
    assert t.loc[("M:1", "related"), "cov_per_1k"] == ""


def test_events_sql_parses():
    sqlglot = __import__("pytest").importorskip("sqlglot")
    sql, _ = wt.typed_wear_sql("p.ds", {"activity_summary": {"date"}}, intraday=False)
    ctes = wt.timing_ctes("p.ds", sql) + we.events_ctes().replace("{cdr}", "p.ds")
    for body in (we.EVENTS_SELECT, we.EXPOSURE_SELECT,
                 we.VISIT_TYPES_SELECT.format(cdr="p.ds"), wt.N_DX_SELECT):
        sqlglot.parse_one(ctes + body, read="bigquery")
    assert "{cdr}" not in ctes and " IN (SELECT" not in ctes
    assert "IN (9203, 262, 8870)" in ctes and "IN (9201, 262, 8717)" in ctes
    assert "COUNTIF(new_ep) OVER (PARTITION BY person_id ORDER BY vd)" in ctes


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
        if "SELECT * FROM mt" in sql:
            return pd.DataFrame({"concept_id_1": [123], "concept_id_2": [123],
                                 "relationship_id": ["Maps to"]})
        if "UNION DISTINCT" in sql:
            return concept
        if "INFORMATION_SCHEMA" in sql:
            return pd.DataFrame({"table_name": ["activity_summary"], "column_name": ["date"]})
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
                    "MONDO:AI", "--exact", "--tag", "ai"]) == 0
    out = out / "ds"
    assert seen["ev"]["lookback"] == ("INT64", 30)
    assert seen["ev"]["washout"] == ("INT64", 7)
    md = (out / "ai_events-report.md").read_text()
    assert "| MONDO:A | disease A | 30 |" in md
    assert (out / "ai_events-table.tsv").exists() and (out / "ai_visit-types.tsv").exists()
