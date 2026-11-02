"""Wearables-timing helpers (audits/wearables_timing.py)."""
import pandas as pd

from audits import wearables_rare as dw
from audits import wearables_timing as wt


def _per():
    """30 persons with disease M:1 and activity data (days before = 0..29, after = 40);
    5 of them also have intraday heart rate. ALL mirrors M:1."""
    rows = []
    for m in ("M:1", wt.ALL):
        for i in range(30):
            for src in (wt.ANY, "activity_summary"):
                rows.append((m, src, i, 40, min(i, 20), 40, i * 10, 400))
            if i < 5:
                rows.append((m, "heart_rate_minute_level", 0, 3, 0, 3, -5, 2))
    return pd.DataFrame(rows, columns=["mondo_id", "src", "days_before", "days_after",
                                       "days_pre_win", "days_post_win", "lead_days",
                                       "follow_days"])


def _n_dx():
    return pd.DataFrame({"mondo_id": ["M:1", "M:2", wt.ALL], "n_dx": [300, 12, 310]})


def test_profile_counts_quartiles_and_bins():
    prof = wt.profile(_per(), _n_dx(), thresholds=(7, 10)).set_index(["mondo_id", "src"])
    r = prof.loc[("M:1", "activity_summary")]
    assert (r["n_wear"], r["n_before"], r["n_after"]) == (30, 29, 30)
    assert (r["n_pre10"], r["n_post10"], r["n_both10"]) == (20, 30, 20)
    assert (r["n_pre7"], r["n_post7"], r["n_both7"]) == (23, 30, 23)
    assert r["before_p50"] == 15 and r["after_p50"] == 40
    assert r["before_1-29"] == 29 and r["after_30-89"] == 30 and r["before_730+"] == 0
    hr = prof.loc[("M:1", "heart_rate_minute_level")]
    assert hr["n_wear"] == 5 and pd.isna(hr["after_p50"])   # 5 persons: no quartiles
    m2 = prof.loc[("M:2", wt.ANY)]                          # diagnosed, no wear rows
    assert (m2["n_dx"], m2["n_wear"]) == (12, 0)
    assert list(prof.loc["M:1"].index)[0] == wt.ANY        # 'any' sorts first


def test_masked_masks_counts_not_quartiles():
    prof = wt.profile(_per(), _n_dx(), thresholds=(7, 10))
    m = wt.masked(prof, {"M:1": "foo"}).set_index(["mondo_id", "src"])
    hr = m.loc[("M:1", "heart_rate_minute_level")]
    assert (hr["n_wear"], hr["after_p50"], hr["after_1-29"]) == ("<20", "", "<20")
    a = m.loc[("M:1", "activity_summary")]
    assert (a["before_p50"], a["n_wear"], a["name"]) == ("15", "30", "foo")
    assert m.loc[("M:2", wt.ANY), "n_dx"] == "<20"
    assert m.loc[(wt.ALL, wt.ANY), "name"] == "all selected diseases"


def test_report_has_pooled_and_per_disease_sections():
    prof = wt.profile(_per(), _n_dx(), thresholds=(7, 10))
    meta = {"cdr": "p.ds", "wear_tables": ["activity_summary"], "flags": ["orphanet_rare"],
            "under": ["MONDO:AI"], "exact": True, "descendants": True, "min_dx_dates": 1,
            "window_days": 365, "window_thresholds": [7, 10], "n_rare_nodes": 2}
    md = wt.format_report(prof, {"M:1": "foo syndrome"}, meta, top=10)
    assert "Persons with any selected diagnosis: 310" in md
    assert ("| activity_summary | 30 | 29 | 30 | 23 | 30 | 23 | 20 | 30 | 20 | 15 (8–22) | "
            "40 (40–40) |") in md
    assert "| ≥7 in 365 before | ≥7 in 365 after | both ≥7 | ≥10 in 365 before |" in md
    assert "| M:1 | foo syndrome | 300 | 30 |" in md and "M:2" not in md
    assert "| foo syndrome | 29 / 30 | 0 / <20 |" in md


def test_typed_wear_sql_and_ctes_parse():
    sqlglot = __import__("pytest").importorskip("sqlglot")
    have = {"activity_summary": {"date"}, "heart_rate_minute_level": {"datetime"},
            "sleep_level": {"start_datetime"}}
    sql, found = wt.typed_wear_sql("p.ds", have)
    assert found == ["activity_summary", "heart_rate_minute_level", "sleep_level"]
    assert "CAST(t.start_datetime AS DATE)" in sql and " IN (SELECT" not in sql
    assert wt.typed_wear_sql("p.ds", have, intraday=False)[1] == ["activity_summary"]
    ctes = wt.timing_ctes("p.ds", sql)
    for body in (wt.N_DX_SELECT, wt.PER_PERSON_SELECT):
        sqlglot.parse_one(ctes + body, read="bigquery")


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
    per = _per().replace({"M:1": "MONDO:A"})
    seen = {}

    def fake_query(client, sql, params=None):
        if "SELECT * FROM mt" in sql:
            return pd.DataFrame({"concept_id_1": [123], "concept_id_2": [123],
                                 "relationship_id": ["Maps to"]})
        if "UNION DISTINCT" in sql:
            return concept
        if "INFORMATION_SCHEMA" in sql:
            return pd.DataFrame({"table_name": ["activity_summary", "heart_rate_minute_level"],
                                 "column_name": ["date", "datetime"]})
        if "days_before" in sql:
            seen["per"] = params
            return per
        return pd.DataFrame({"mondo_id": ["MONDO:A", wt.ALL], "n_dx": [300, 300]})

    monkeypatch.setenv("WORKSPACE_CDR", "p.ds")
    monkeypatch.setenv("GOOGLE_CLOUD_PROJECT", "bill")
    monkeypatch.setattr(wt, "bq_client", lambda billing: object())
    monkeypatch.setattr(wt, "query", fake_query)
    monkeypatch.setattr(dw, "query", fake_query)
    monkeypatch.setattr(dw, "download_cached", lambda v, f, c: files[f])
    out = tmp_path / "out"
    assert wt.main(["--out-dir", str(out), "--flags", "orphanet_rare", "--under",
                    "MONDO:AI", "--exact", "--tag", "ai"]) == 0
    out = out / "ds"
    assert seen["per"]["win_days"] == ("INT64", 365)
    assert list(zip(seen["per"]["mondo"][1], seen["per"]["cid"][1])) == [("MONDO:A", 123)]
    tsv = pd.read_csv(out / "ai_table.tsv", sep="\t", dtype=str)
    assert set(tsv["n_wear"]) <= {"0", "30", "<20"}
    md = (out / "ai_report.md").read_text()
    assert "CDR: `p.ds`" in md and "| MONDO:A | disease A | 300 | 30 |" in md
    assert {f.name for f in out.iterdir() if f.is_dir()} == set()   # flat folder
    assert (out / "ai_mapping.tsv").exists() and (out / "ai_run.json").exists()


def test_plots_read_only_the_masked_report(tmp_path):
    pytest = __import__("pytest")
    pytest.importorskip("matplotlib")
    from audits import wearables_timing_plots as wp
    prof = wt.profile(_per(), _n_dx(), thresholds=(7, 10))
    meta = {"cdr": "p.ds", "wear_tables": ["activity_summary"], "flags": ["x"],
            "n_rare_nodes": 2, "window_days": 365, "window_thresholds": [7, 10]}
    md = wt.format_report(prof, {"M:1": "foo"}, meta, top=10)
    t = wp.read_report(md)
    assert set(t) == {"pooled", "bins_before", "bins_after", "diseases", "kinds"}
    assert wp.parse_count("<20") == wp.MASK and wp.parse_count("1,808") == 1808
    assert wp.parse_iqr("471 (180–1,052)") == (471, 180, 1052) and wp.parse_iqr("—") is None
    d = t["diseases"]
    assert wp.window_columns(d)[("both", 7)] == "both ≥7"
    assert wp.window_columns(d)[("after", 10)] == "≥10 in 365 after"
    old = pd.DataFrame(columns=["≥30 in 365 before", "≥30 in 365 after", "both"])
    assert wp.window_columns(old) == {("before", 30): "≥30 in 365 before",
                                      ("after", 30): "≥30 in 365 after",
                                      ("both", 30): "both"}
    paths = wp.write_plots(md, tmp_path, prefix="run_plot-")
    assert [p.name for p in paths] == ["run_plot-pooled-bins.png", "run_plot-pooled-medians.png",
                                       "run_plot-disease-counts.png",
                                       "run_plot-disease-medians.png"]
    assert all(p.stat().st_size > 0 for p in paths)


def test_patient_plots_need_do_not_egress_in_the_name(tmp_path):
    pytest = __import__("pytest")
    pytest.importorskip("matplotlib")
    from audits import wearables_timing_plots as wp
    with pytest.raises(ValueError):
        wp.write_patient_plots(_per(), {}, tmp_path, prefix="run_")
    assert wp.facet_order(_per(), wt.ANY, 5, wt.ALL) == [wt.ALL, "M:1"]
    paths = wp.write_patient_plots(_per(), {"M:1": "foo"}, tmp_path,
                                   prefix="run_DO_NOT_EGRESS_", kinds=(wt.ANY, "activity_summary"))
    assert [p.name for p in paths][:4] == [
        "run_DO_NOT_EGRESS_patients-days.png", "run_DO_NOT_EGRESS_patients-days-marginal.png",
        "run_DO_NOT_EGRESS_patients-span.png", "run_DO_NOT_EGRESS_patients-span-marginal.png"]
    assert paths[4].name == "run_DO_NOT_EGRESS_patients-days-activity_summary.png"


def test_run_name_is_short_and_readable():
    names = {"MONDO:0007179": "autoimmune disease", "MONDO:0004995": "cardiovascular disorder"}
    std = ["orphanet_rare", "gard_rare", "nord_rare", "mondo_rare"]
    assert wt.run_name(["MONDO:0007179"], names, std, exact=True) == "autoimmune-disease_exact"
    assert wt.run_name(["MONDO:0004995"], names, ["rare"], min_dx_dates=2) == \
        "cardiovascular-disorder_rare_dx2"
    assert wt.run_name([], names, std, descendants=False) == "all-rare_nodesc"


def test_by_disease_keeps_only_diseases_with_a_window_count_over_the_floor():
    """M:3 has 25 persons with data but none with >= 7 days in either window: dropped
    from the per-disease table, while M:1 (window counts >= 20) stays."""
    extra = pd.DataFrame([("M:3", wt.ANY, 1, 1, 1, 1, 1, 1)] * 25, columns=_per().columns)
    per = pd.concat([_per(), extra], ignore_index=True)
    n_dx = pd.concat([_n_dx(), pd.DataFrame({"mondo_id": ["M:3"], "n_dx": [99]})])
    prof = wt.profile(per, n_dx, thresholds=(7, 10))
    meta = {"cdr": "p.ds", "wear_tables": ["activity_summary"], "flags": ["x"],
            "n_rare_nodes": 3, "window_days": 365, "window_thresholds": [7, 10]}
    md = wt.format_report(prof, {"M:1": "foo", "M:3": "bar"}, meta, top=0)
    assert "| M:1 | foo |" in md and "| M:3 |" not in md
