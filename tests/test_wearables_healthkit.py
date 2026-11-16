"""Apple HealthKit coverage helpers (audits/wearables_healthkit.py)."""
import pandas as pd
import pytest

from audits import wearables_healthkit as hk
from audits import wearables_rare as dw
from audits import wearables_timing as wt


def _schema():
    return pd.DataFrame(
        [("hk_heart_rate", "person_id", "INT64"), ("hk_heart_rate", "start_datetime", "DATETIME"),
         ("hk_heart_rate", "value", "FLOAT64"),
         ("steps_daily", "participant_id", "STRING"), ("steps_daily", "created", "TIMESTAMP"),
         ("steps_daily", "date", "DATE"),
         ("device", "person_id", "INT64"), ("device", "device_name", "STRING"),
         ("readme", "text", "STRING")],
        columns=["table_name", "column_name", "data_type"])


def test_hk_candidates_prefers_named_datasets_then_cdr_tables():
    ds = ["p.C2025Q4R6", "p.C2025Q4R6_healthkit", "q.scratch", "p.C2025Q4R6_healthkit"]
    assert hk.hk_candidates(ds, "p.C2025Q4R6", []) == ["p.C2025Q4R6_healthkit"]
    assert hk.hk_candidates(["p.C2025Q4R6", "q.scratch"], "p.C2025Q4R6",
                            ["person", "apple_heart_rate", "hk_steps", "chk_x"]) == \
        ["CDR:apple_heart_rate", "CDR:hk_steps"]


def test_pick_columns_person_and_date_rules():
    p = hk.pick_columns(_schema()).set_index("table_name")
    assert p.loc["hk_heart_rate", "date_col"] == "start_datetime"
    assert p.loc["steps_daily", "person_col"] == "participant_id"
    assert p.loc["steps_daily", "date_col"] == "date"
    assert p.loc["device", "why"] == "no date column"
    assert p.loc["readme", "why"] == "no person column"
    o = hk.pick_columns(_schema(), {"steps_daily": "created"}).set_index("table_name")
    assert o.loc["steps_daily", "date_col"] == "created"


def test_hk_wear_sql_casts_non_int_person_and_skips_unusable():
    sql = hk.hk_wear_sql("p.hk", hk.pick_columns(_schema()))
    assert "SAFE_CAST(t.participant_id AS INT64) AS person_id, 'hk_steps_daily'" in sql
    assert "t.person_id AS person_id, 'hk_hk_heart_rate'" in sql
    assert "JOIN cohort c" in sql and "device" not in sql
    assert "JOIN cohort" not in hk.hk_wear_sql("p.hk", hk.pick_columns(_schema()), cohort=False)
    with pytest.raises(SystemExit):
        hk.hk_wear_sql("p.hk", hk.pick_columns(_schema()[_schema()["table_name"] == "readme"]))


def _ev():
    """ALL and M:1: 30 persons, an ED episode at day 10. Persons 0-19 covered by Fitbit,
    20-24 by HealthKit only, 25-29 by neither (but 20 days either way combined)."""
    rows = []
    for m in ("M:1", wt.ALL):
        for pid in range(30):
            fb, h = (20, 0) if pid < 20 else (0, 20) if pid < 25 else (10, 10)
            rows.append((pid, m, 10, True, False, fb, h, fb + h))
            rows.append((pid, m, -5, True, False, 30, 30, 30))   # before dx: excluded
    return pd.DataFrame(rows, columns=["pid", "mondo_id", "rel_day", "is_ed", "is_ip",
                                       "cov_fb", "cov_hk", "cov_any"])


def test_events_summary_sources_and_hk_only():
    s = hk.events_summary(_ev(), min_cov=14).set_index("event_class")
    r = s.loc["ed_or_inpatient"]
    assert (r.n_ev, r.cov_fb, r.cov_hk, r.cov_any, r.cov_hk_only) == (30, 20, 5, 30, 10)
    assert s.loc["inpatient", "n_ev"] == 0
    d = hk.events_summary(_ev(), min_cov=14, by_disease=True)
    assert set(d["mondo_id"]) == {"M:1", wt.ALL} and (d["event_class"] == "ed_or_inpatient").all()


def test_cohort_summary_and_device_values():
    per = pd.DataFrame({"mondo_id": [wt.ALL] * 4, "fb_days": [5, 0, 3, 0],
                        "hk_days": [0, 7, 2, 0], "fb_after": [1, 0, 1, 0],
                        "hk_after": [0, 3, 0, 0], "any_after": [1, 3, 1, 0]})
    c = hk.cohort_summary(per, pd.DataFrame({"mondo_id": [wt.ALL], "n_dx": [10]})).iloc[0]
    assert (c.n_fitbit, c.n_hk, c.n_both, c.n_hk_only, c.n_hk_after) == (2, 2, 1, 1, 1)
    v = hk.device_values(pd.DataFrame({"value": ["Watch", None, "Jane's iPhone"],
                                       "n_persons": [50, 25, 1]}))
    assert list(v["value"]) == ["Watch", "(null)", "(other: <20 values)"]
    assert "Jane" not in v.to_string()


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
    seen = {"sql": []}

    def fake_query(client, sql, params=None):
        seen["sql"].append(sql)
        if "__TABLES__" in sql:
            return pd.DataFrame({"table_name": ["hk_heart_rate", "steps_daily", "device"],
                                 "row_count": [10**9, 10**6, 10**4],
                                 "size_bytes": [5e11, 1e9, 1e6]})
        if "ordinal_position" in sql:
            return _schema()
        if "INFORMATION_SCHEMA.TABLES" in sql:
            return pd.DataFrame({"table_name": ["person"]})
        if "INFORMATION_SCHEMA" in sql:
            return pd.DataFrame({"table_name": ["activity_summary"], "column_name": ["date"]})
        if "AS value" in sql:
            return pd.DataFrame({"value": ["Apple Watch", "Jo's phone"], "n_persons": [400, 1]})
        if "n_in_cdr" in sql:
            return pd.DataFrame({"src": ["hk_steps_daily", "any HealthKit"],
                                 "n_persons": [900, 900], "n_in_cdr": [899, 899]})
        if "EXTRACT(YEAR" in sql:
            return pd.DataFrame({"source": ["Fitbit", "HealthKit"], "year": [2024, 2025],
                                 "n_persons": [5000, 7]})
        if "has_hk" in sql:
            return pd.DataFrame({"has_fitbit": [True] * 30 + [False] * 25,
                                 "has_hk": [False] * 10 + [True] * 45})
        if "SELECT * FROM mt" in sql:
            return pd.DataFrame({"concept_id_1": [123], "concept_id_2": [123],
                                 "relationship_id": ["Maps to"]})
        if "UNION DISTINCT" in sql:
            return concept
        if "cov_hk" in sql:
            seen["ev"] = params
            return _ev().replace({"M:1": "MONDO:A"})
        if "hk_after" in sql:
            return pd.DataFrame({"mondo_id": ["MONDO:A", wt.ALL] * 25,
                                 "fb_days": [5] * 50, "hk_days": [3] * 50,
                                 "fb_after": [1] * 50, "hk_after": [2] * 50,
                                 "any_after": [3] * 50})
        return pd.DataFrame({"mondo_id": ["MONDO:A", wt.ALL], "n_dx": [300, 300]})

    monkeypatch.setenv("WORKSPACE_CDR", "p.ds")
    monkeypatch.setenv("GOOGLE_CLOUD_PROJECT", "bill")
    monkeypatch.setattr(hk, "bq_client", lambda billing: object())
    monkeypatch.setattr(hk, "query", fake_query)
    monkeypatch.setattr(dw, "query", fake_query)
    monkeypatch.setattr(dw, "download_cached", lambda v, f, c: files[f])
    out = tmp_path / "out"
    assert hk.main(["--out-dir", str(out), "--hk-dataset", "p.hk", "--flags",
                    "orphanet_rare", "--under", "MONDO:AI", "--exact", "--tag", "ai",
                    "--ip-overnight"]) == 0
    assert seen["ev"]["ip_overnight"] == ("BOOL", True)
    assert seen["ev"]["lookback"] == ("INT64", 30)
    md = (out / "ds" / "ai_hk-report.md").read_text()
    assert "| hk_heart_rate | 1,000,000,000 | 500.0 | person_id | start_datetime | no: over --max-gb 100 |" in md
    assert "| steps_daily | 900 | 899 |" in md
    assert "| 2025 | 0 | <20 |" in md
    assert "Persons with Fitbit daily data / HealthKit data / both / HealthKit only: 30 / 45 / 20 / 25" in md
    assert "| Apple Watch | 400 |" in md and "Jo's" not in md
    assert "| ed_or_inpatient | 30 (30) | 20 (20) | <20 (<20) | 30 (30) | <20 (<20) |" in md
    assert "with HealthKit: 25" in md
    hk_sql = [s for s in seen["sql"] if "cov_hk" in s][0]
    assert "`p.hk.steps_daily`" in hk_sql and "`p.hk.hk_heart_rate`" not in hk_sql
    for f in ("hk-schema.tsv", "hk-cohort.tsv", "hk-events.tsv", "hk-run.json"):
        assert (out / "ds" / f"ai_{f}").exists()
    assert "Jo's" not in (out / "ds" / "ai_hk-events.tsv").read_text()


def test_sql_parses():
    sqlglot = pytest.importorskip("sqlglot")
    fb, _ = wt.typed_wear_sql("p.ds", {"activity_summary": {"date"}}, intraday=False)
    picks = hk.pick_columns(_schema())
    from audits import wearables_events as we
    ctes = (wt.timing_ctes("p.ds", fb + "\n    UNION ALL\n    " + hk.hk_wear_sql("p.hk", picks))
            + we.events_ctes(None).replace("{cdr}", "p.ds"))
    for body in (hk.COHORT_SELECT, hk.HK_EVENTS_SELECT, wt.N_DX_SELECT):
        sqlglot.parse_one(ctes + body, read="bigquery")
    all_days = ("WITH all_days AS (SELECT DISTINCT person_id, src, d FROM (\n    "
                + fb.replace(" JOIN cohort c ON t.person_id = c.person_id", "")
                + "\n    UNION ALL\n    " + hk.hk_wear_sql("p.hk", picks, cohort=False)
                + ") WHERE d IS NOT NULL)\n")
    assert "cohort" not in all_days
    for body in (hk.ALL_PERSONS_SELECT.format(cdr="p.ds"), hk.ALL_YEARS_SELECT,
                 hk.ALL_OVERLAP_SELECT):
        sqlglot.parse_one(all_days + body, read="bigquery")
    sqlglot.parse_one(hk.DEVICE_VALUES_SELECT.format(hk="p.hk", table="device",
                                                     col="device_name", pcol="person_id"),
                      read="bigquery")
