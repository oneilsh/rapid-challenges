"""Apple HealthKit coverage helpers (audits/wearables_healthkit.py)."""
import pandas as pd
import pytest

from audits import wearables_healthkit as hk
from audits import wearables_rare as dw
from audits import wearables_timing as wt


def _schema():
    """The V9 CT HealthKit layout (C_V9_R6_offcycle_healthkit), trimmed."""
    rows = [("activity_measurements", c, t) for c, t in (
        ("person_id", "INT64"), ("data_type", "STRING"), ("start_datetime", "TIMESTAMP"),
        ("end_datetime", "TIMESTAMP"), ("device_source_id", "STRING"),
        ("value", "STRING"), ("is_user_entered", "BOOL"))]
    rows += [("vital_measurements", c, t) for c, t in (
        ("person_id", "INT64"), ("datetime", "TIMESTAMP"), ("activity_type", "STRING"),
        ("device_source_id", "STRING"), ("is_user_entered", "BOOL"))]
    rows += [("physical_measurements", c, t) for c, t in (
        ("person_id", "INT64"), ("datetime", "TIMESTAMP"), ("activity_type", "STRING"))]
    rows += [("device_and_source", c, "STRING") for c in (
        "device_source_id", "device_name", "manufacturer", "model", "product_type",
        "source_name")]
    rows += [("steps_daily", "participant_id", "STRING"), ("steps_daily", "date", "DATE")]
    return pd.DataFrame(rows, columns=["table_name", "column_name", "data_type"])


def test_hk_candidates_prefers_named_datasets_then_cdr_tables():
    ds = ["p.C2025Q4R6", "p.C_V9_R6_offcycle_healthkit", "q.scratch"]
    assert hk.hk_candidates(ds, "p.C2025Q4R6", []) == ["p.C_V9_R6_offcycle_healthkit"]
    assert hk.hk_candidates(["p.C2025Q4R6", "q.scratch"], "p.C2025Q4R6",
                            ["person", "apple_heart_rate", "hk_steps", "chk_x"]) == \
        ["CDR:apple_heart_rate", "CDR:hk_steps"]


def test_pick_columns_and_device_table():
    p = hk.pick_columns(_schema(), skip={"physical_measurements"}).set_index("table_name")
    a = p.loc["activity_measurements"]
    assert (a.date_col, a.type_col, a.has_device, a.has_user, a.why) == \
        ("start_datetime", "data_type", True, True, "")
    assert p.loc["vital_measurements", "type_col"] == "activity_type"
    assert p.loc["physical_measurements", "why"] == "--hk-skip"
    assert p.loc["device_and_source", "why"] == "no person column"
    assert p.loc["steps_daily", "date_col"] == "date"
    assert hk.device_table(_schema()) == "device_and_source"


def test_hk_wear_sql_watch_flag_user_rows_and_casts():
    picks = hk.pick_columns(_schema(), skip={"physical_measurements"})
    dev = hk._dev_subquery("p.hk", "device_and_source", {"model", "product_type"})
    sql = hk.hk_wear_sql("p.hk", picks, dev)
    assert "CONCAT('hk_activity_measurements:', IF(IFNULL(dv.is_watch, FALSE), 'watch', " in sql
    assert "WHERE NOT IFNULL(t.is_user_entered, FALSE)" in sql
    assert "SAFE_CAST(t.participant_id AS INT64) AS person_id" in sql
    assert "CONCAT('hk_steps_daily:', 'other')" in sql
    assert "physical_measurements" not in sql and "JOIN cohort c" in sql
    assert "JOIN cohort" not in hk.hk_wear_sql("p.hk", picks, dev, cohort=False)


def test_nested_cells_suppresses_partners_of_small_parts():
    v = {"hk": 36, "both": 15, "only": 21, "fb": 300, "x_fb_only": 285}
    c = hk.nested_cells(v, [("hk", ("both", "only")), ("fb", ("both", "x_fb_only"))])
    assert (c["hk"], c["both"], c["only"], c["fb"]) == ("36", "<20", hk.SUPPRESSED, "300")
    c = hk.nested_cells({"a": 50, "b": 25, "c": 25}, [("a", ("b", "c"))])
    assert (c["b"], c["c"]) == ("25", "25")
    c = hk.nested_cells({"a": 30, "b": 30, "c": 0}, [("a", ("b", "c"))])
    assert c["b"] == "30"


def _ev():
    """ALL and M:1: 40 persons, an ED episode at day 10. Persons 0-19: Fitbit covered;
    20-24: HealthKit watch covered; 25-29: 10 + 10 days (added only together);
    30-39: no data."""
    rows = []
    for m in ("M:1", wt.ALL):
        for pid in range(40):
            fb, h, w = ((20, 0, 0) if pid < 20 else (0, 20, 20) if pid < 25
                        else (10, 10, 0) if pid < 30 else (0, 0, 0))
            rows.append((pid, m, 10, True, False, fb, h, w, fb + h))
            rows.append((pid, m, -5, True, False, 30, 30, 30, 30))   # before dx: excluded
    return pd.DataFrame(rows, columns=["pid", "mondo_id", "rel_day", "is_ed", "is_ip",
                                       "cov_fb", "cov_hk", "cov_watch", "cov_any"])


def test_events_summary_and_suppressed_cells():
    s = hk.events_summary(_ev(), min_cov=14).set_index("event_class")
    r = s.loc["ed_or_inpatient"]
    assert (r.n_ev, r.cov_fb, r.cov_hk, r.cov_watch, r.cov_added, r.cov_any) == \
        (40, 20, 5, 5, 10, 30)
    assert (r.x_unc, r.x_unc_p, r.x_hk_nw) == (20, 20, 0)
    assert s.loc["inpatient", "n_ev"] == 0
    cells = hk._ev_cells(next(s.reset_index().itertuples()))
    assert cells == ["40 (40)", "20 (20)", "<20 (<20)", "<20 (<20)", "<20 (<20)"]
    d = hk.events_summary(_ev(), min_cov=14, by_disease=True)
    assert set(d["mondo_id"]) == {"M:1", wt.ALL}


def test_cohort_summary_and_top_values():
    per = pd.DataFrame({"mondo_id": [wt.ALL] * 4, "fb_days": [5, 0, 3, 0],
                        "hk_days": [0, 7, 2, 0], "watch_days": [0, 7, 0, 0],
                        "fb_after": [1, 0, 1, 0], "hk_after": [0, 3, 0, 0],
                        "watch_after": [0, 3, 0, 0], "any_after": [1, 3, 1, 0]})
    c = hk.cohort_summary(per, pd.DataFrame({"mondo_id": [wt.ALL], "n_dx": [10]})).iloc[0]
    assert (c.n_fitbit, c.n_hk, c.n_watch, c.n_both, c.n_hk_only, c.n_hk_after) == \
        (2, 2, 1, 1, 1, 1)
    assert (c.x_fb_only, c.x_hk_no_watch, c.x_hk_not_after) == (1, 1, 1)
    v = hk.top_values(pd.DataFrame({"value": ["StepCount", None, "Rare"],
                                    "n_persons": [50, 25, 1], "n_rows": [9, 9, 9]}))
    assert list(v["value"]) == ["StepCount", "(null)", "(other: <20 values)"]
    m = hk.top_values(pd.DataFrame({"manufacturer": ["Apple", "X"], "model": ["Watch", "Y"],
                                    "n_persons": [500, 3]}))
    assert list(m["manufacturer"]) == ["Apple", "(other: <20 values)"]


def test_sql_parses():
    sqlglot = pytest.importorskip("sqlglot")
    from audits import wearables_events as we
    fb, _ = wt.typed_wear_sql("p.ds", {"activity_summary": {"date"}}, intraday=False)
    picks = hk.pick_columns(_schema(), skip={"physical_measurements"})
    dev = hk._dev_subquery("p.hk", "device_and_source", {"model", "product_type"})
    ctes = (wt.timing_ctes("p.ds", fb + "\n    UNION ALL\n    "
                           + hk.hk_wear_sql("p.hk", picks, dev))
            + we.events_ctes(None).replace("{cdr}", "p.ds"))
    for body in (hk.COHORT_SELECT, hk.HK_EVENTS_SELECT, wt.N_DX_SELECT):
        sqlglot.parse_one(ctes + body, read="bigquery")
    all_days = hk.all_days_sql(fb, hk.hk_wear_sql("p.hk", picks, dev, cohort=False))
    assert "cohort" not in all_days
    for body in (hk.ALL_KINDS_SELECT.format(cdr="p.ds"), hk.ALL_YEARS_SELECT,
                 hk.ALL_OVERLAP_SELECT):
        sqlglot.parse_one(all_days + body, read="bigquery")
    r = next(picks[picks["table_name"] == "activity_measurements"].itertuples())
    rows = hk.hk_rows_sql("p.hk", r, None, False, "{pid} AS person_id, t.data_type AS value")
    sqlglot.parse_one(hk.TYPES_SELECT.format(rows=rows), read="bigquery")
    rows = hk.hk_rows_sql("p.hk", r, None, False, "{pid} AS person_id, t.device_source_id")
    sqlglot.parse_one(hk.MODELS_SELECT.format(rows=rows, hk="p.hk", dev="device_and_source"),
                      read="bigquery")


def _fake_bq(tmp_path, monkeypatch, seen, est_bytes=1e9):
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
    seen.setdefault("sql", [])

    def fake_query(client, sql, params=None):
        seen["sql"].append(sql)
        if "__TABLES__" in sql:
            return pd.DataFrame({"table_name": ["activity_measurements", "vital_measurements"],
                                 "row_count": [2931284290, 10**9], "size_bytes": [3.488e11, 1e11]})
        if "ordinal_position" in sql:
            return _schema()
        if "INFORMATION_SCHEMA" in sql:
            return pd.DataFrame({"table_name": ["activity_summary"], "column_name": ["date"]})
        if "AS manufacturer" in sql:
            return pd.DataFrame({"manufacturer": ["Apple Inc.", "Apple Inc.", "Jo"],
                                 "model": ["Watch", "iPhone", "Jo's scale"],
                                 "n_persons": [9000, 15000, 1]})
        if "n_rows" in sql:
            return pd.DataFrame({"value": ["HKQuantityTypeIdentifierStepCount", "Odd"],
                                 "n_persons": [17000, 2], "n_rows": [10**9, 5]})
        if "n_in_cdr" in sql:
            return pd.DataFrame({"src": ["any HealthKit", "hk_activity_measurements:watch"],
                                 "n_persons": [17500, 9000], "n_in_cdr": [17495, 9000]})
        if "EXTRACT(YEAR" in sql:
            return pd.DataFrame({"year": [2023, 2024], "n_fitbit": [54000, 50000],
                                 "n_hk": [9000, 40], "n_watch": [4000, 30]})
        if "n_hk_only" in sql:
            return pd.DataFrame({"n_fitbit": [68779], "n_hk": [17500], "n_watch": [9000],
                                 "n_both": [4000], "n_hk_only": [13500]})
        if "SELECT * FROM mt" in sql:
            return pd.DataFrame({"concept_id_1": [123], "concept_id_2": [123],
                                 "relationship_id": ["Maps to"]})
        if "UNION DISTINCT" in sql:
            return concept
        if "cov_watch" in sql:
            seen["ev"] = params
            return _ev().replace({"M:1": "MONDO:A"})
        if "watch_after" in sql:
            return pd.DataFrame({"mondo_id": ["MONDO:A", wt.ALL] * 25,
                                 "fb_days": [5] * 50, "hk_days": [3] * 50,
                                 "watch_days": [3] * 50, "fb_after": [1] * 50,
                                 "hk_after": [2] * 50, "watch_after": [2] * 50,
                                 "any_after": [3] * 50})
        return pd.DataFrame({"mondo_id": ["MONDO:A", wt.ALL], "n_dx": [300, 300]})

    monkeypatch.setenv("WORKSPACE_CDR", "p.ds")
    monkeypatch.setenv("GOOGLE_CLOUD_PROJECT", "bill")
    monkeypatch.setattr(hk, "bq_client", lambda billing: object())
    monkeypatch.setattr(hk, "query", fake_query)
    monkeypatch.setattr(hk, "dry_run_bytes", lambda c, s, p=None: est_bytes)
    monkeypatch.setattr(dw, "query", fake_query)
    monkeypatch.setattr(dw, "download_cached", lambda v, f, c: files[f])


ARGS = ["--hk-dataset", "p.hk", "--flags", "orphanet_rare", "--under", "MONDO:AI",
        "--exact", "--tag", "ai", "--ip-overnight"]


def test_main_end_to_end_with_fake_bigquery(tmp_path, monkeypatch):
    seen = {}
    _fake_bq(tmp_path, monkeypatch, seen)
    out = tmp_path / "out"
    assert hk.main(["--out-dir", str(out)] + ARGS) == 0
    assert seen["ev"]["ip_overnight"] == ("BOOL", True)
    md = (out / "ds" / "ai_hk-report.md").read_text()
    assert "| activity_measurements | 2,931,284,290 | 348.8 | person_id | start_datetime | data_type | yes |" in md
    assert "| physical_measurements |  |  | person_id | datetime | activity_type | no: --hk-skip |" in md
    assert f"| any HealthKit | 17,500 | {hk.SUPPRESSED} |" in md      # 5 not in CDR
    assert "| activity_measurements · watch | 9,000 | 9,000 |" in md
    assert "HealthKit from a watch: 9,000 · both Fitbit and HealthKit: 4,000" in md
    assert f"| 2024 | 50,000 | 40 | {hk.SUPPRESSED} |" in md            # 10 non-watch
    assert "| HKQuantityTypeIdentifierStepCount | 17,000 | 1,000,000,000 |" in md
    assert "| (other: <20 values) | <20 | 5 |" in md and "nan" not in md
    assert "| Apple Inc. | Watch | 9,000 |" in md and "Jo's" not in md
    assert "| ed_or_inpatient | 40 (40) | 20 (20) | <20 (<20) | <20 (<20) | <20 (<20) |" in md
    assert "either 75" in md and "| either |" not in md
    assert "| MONDO:A | disease A | 20 (20) | <20 (<20) | <20 (<20) | <20 (<20) |" in md
    ev_sql = [s for s in seen["sql"] if "cov_watch" in s][0]
    assert "`p.hk.activity_measurements`" in ev_sql and "physical_measurements" not in ev_sql
    for f in ("hk-schema.tsv", "hk-run.json"):
        assert (out / "ds" / f"ai_{f}").exists()


def test_main_stops_over_budget(tmp_path, monkeypatch):
    seen = {}
    _fake_bq(tmp_path, monkeypatch, seen, est_bytes=1e12)
    with pytest.raises(SystemExit, match="over --max-tb"):
        hk.main(["--out-dir", str(tmp_path / "out")] + ARGS)
    assert not any("cov_watch" in s for s in seen["sql"])   # nothing heavy ran
