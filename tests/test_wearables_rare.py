"""Wearables × rare-disease census helpers (audits/wearables_rare.py)."""
import pandas as pd

from audits import wearables_rare as dw


def _mapping():
    return pd.DataFrame({
        "mondo_id": ["M:1", "M:1", "M:2", "M:3"],
        "standard_concept_id": [10, 11, 20, 30],
        "rare": [1, 1, 1, 0], "gard_rare": [1, 1, 0, 0], "orphanet_rare": [0, 0, 1, 0],
        "nord_rare": [0, 0, 0, 0], "inferred_rare": [0, 0, 0, 0], "mondo_rare": [0, 0, 0, 0]})


def test_rare_concept_map_filters_by_any_flag():
    r = dw.rare_concept_map(_mapping(), ["rare"])
    assert set(r["mondo_id"]) == {"M:1", "M:2"} and len(r) == 3
    g = dw.rare_concept_map(_mapping(), ["gard_rare"])
    assert set(g["mondo_id"]) == {"M:1"}


def test_group_nodes_marks_ancestors_of_other_mapped_rare_nodes():
    child = {"M:0": ["M:a"], "M:a": ["M:1"], "M:1": [], "M:2": []}
    assert dw.group_nodes({"M:0", "M:1", "M:2"}, child) == {"M:0"}


def test_table_rows_and_report_respect_the_floor():
    per = pd.DataFrame({"mondo_id": ["M:1", "M:2", "M:3"], "n_dx": [500, 40, 9000],
                        "n_wear": [60, 12, 300], "n_wear_before": [25, 3, 7],
                        "n_wear_span": [10, 0, 5]})
    rows = dw.table_rows(per, {"M:1": "foo syndrome"}, {"M:3"},
                         {"M:1": ["gard_rare"]}, n_cond_pop=100_000, suspect_share=0.005)
    assert list(rows["mondo_id"]) == ["M:3", "M:1"]             # M:2 under the floor
    assert bool(rows.loc[0, "suspect"]) and bool(rows.loc[0, "group"])
    txt = dw.format_report(rows, {"wear_tables": ["activity_summary"], "flags": ["rare"],
                                  "n_rare_nodes": 3, "n_rare_concepts": 3,
                                  "n_rare_concepts_desc": 9,
                                  "counts": {"persons with any rare dx": 7}},
                           min_days=30, top=10)
    assert "foo syndrome" in txt and "| <20 |" in txt and "M:2" not in txt
    assert "| 25 |" in txt and "| <20 | gard |" in txt


def test_keep_small_keeps_every_row_and_masks_1_to_19():
    per = pd.DataFrame({"mondo_id": ["M:1", "M:2"], "n_dx": [500, 40],
                        "n_wear": [60, 12], "n_wear_before": [25, 3],
                        "n_wear_span": [10, 0]})
    per_all = (pd.DataFrame({"mondo_id": ["M:1", "M:2", "M:9"]})
               .merge(per, on="mondo_id", how="left").fillna(0))
    rows = dw.table_rows(per_all, {}, set(), {}, n_cond_pop=100_000,
                         suspect_share=0.005, keep_small=True)
    assert list(rows["mondo_id"]) == ["M:1", "M:2", "M:9"]
    m2 = rows.set_index("mondo_id").loc["M:2"]
    assert [dw.cell(m2[c]) for c in ("n_dx", "n_wear", "n_wear_before", "n_wear_span")] \
        == ["40", "<20", "<20", "0"]
    assert dw.cell(rows.set_index("mondo_id").loc["M:9", "n_dx"]) == "0"


def test_wear_union_sql_picks_present_tables_and_date_columns():
    sql, found = dw.wear_union_sql("p.ds", {"activity_summary": {"person_id", "date"},
                                            "sleep_daily_summary": {"person_id", "sleep_date"}})
    assert found == ["activity_summary", "sleep_daily_summary"]
    assert "CAST(date AS DATE) AS d FROM `p.ds.activity_summary`" in sql
    assert "CAST(sleep_date AS DATE) AS d FROM `p.ds.sleep_daily_summary`" in sql
    assert "heart_rate_summary" not in sql


def test_census_sql_parses_as_bigquery():
    sqlglot = __import__("pytest").importorskip("sqlglot")
    union, _ = dw.wear_union_sql("p.ds", {"activity_summary": {"date"},
                                          "heart_rate_summary": {"date"}})
    ctes = dw.census_ctes("p.ds", union)
    for body in (dw.PER_NODE_SELECT, dw.overall_select("p.ds")):
        sqlglot.parse_one(ctes + body, read="bigquery")


def test_main_end_to_end_with_fake_bigquery(tmp_path, monkeypatch):
    """Wiring check: Mondo -> mapping -> queries -> masked outputs, BigQuery faked."""
    sc = "biolink:subclass_of"
    nodes = pd.DataFrame(
        [("MONDO:0700096", "biolink:Disease", "human disease", None, None),
         ("MONDO:A", "biolink:Disease", "disease A",
          "http://identifiers.org/snomedct/123", "rare|orphanet_rare"),
         ("MONDO:B", "biolink:Disease", "disease B",
          "http://identifiers.org/snomedct/456", "rare|gard_rare")],
        columns=["id", "category", "name", "same_as", "subsets"])
    edges = pd.DataFrame([("MONDO:A", "MONDO:0700096", sc), ("MONDO:B", "MONDO:0700096", sc)],
                         columns=["subject", "object", "predicate"])
    files = {"mondo_nodes.tsv": tmp_path / "n.tsv", "mondo_edges.tsv": tmp_path / "e.tsv"}
    nodes.to_csv(files["mondo_nodes.tsv"], sep="\t", index=False)
    edges.to_csv(files["mondo_edges.tsv"], sep="\t", index=False)

    concept = pd.DataFrame(
        [(1, "src A", "SNOMED", "Condition", "123", None),
         (2, "src B", "SNOMED", "Condition", "456", None),
         (10, "Std A", "SNOMED", "Condition", "10", "S"),
         (20, "Std B", "SNOMED", "Condition", "20", "S")],
        columns=["concept_id", "concept_name", "vocabulary_id", "domain_id",
                 "concept_code", "standard_concept"])
    seen = {}

    def fake_query(client, sql, params=None):
        if "SELECT * FROM mt" in sql:
            assert set(params["keys"][1]) == {"SNOMED|123", "SNOMED|456"}
            return pd.DataFrame({"concept_id_1": [1, 2], "concept_id_2": [10, 20],
                                 "relationship_id": ["Maps to"] * 2})
        if "UNION DISTINCT" in sql:
            return concept
        if "INFORMATION_SCHEMA" in sql:
            return pd.DataFrame({"table_name": ["activity_summary"], "column_name": ["date"]})
        if "GROUP BY mondo_id" in sql:
            seen["per"] = params
            return pd.DataFrame({"mondo_id": ["MONDO:A", "MONDO:B"], "n_dx": [400, 30],
                                 "n_wear": [50, 7], "n_wear_before": [21, 0],
                                 "n_wear_span": [3, 0]})
        seen["overall"] = params
        cols = ["n_cond_pop", "n_wear_any", "n_wear_ok", "n_desc", "rare_dx", "rare_wear",
                "nongroup_wear", "orphanet_rare_dx", "orphanet_rare_wear", "gard_rare_dx",
                "gard_rare_wear", "nord_rare_dx", "nord_rare_wear"]
        return pd.DataFrame([[100_000, 5000, 4000, 2, 430, 57, 57, 400, 50, 30, 7, 0, 0]],
                            columns=cols)

    monkeypatch.setenv("WORKSPACE_CDR", "p.ds")
    monkeypatch.setenv("GOOGLE_CLOUD_PROJECT", "bill")
    monkeypatch.setattr(dw, "bq_client", lambda billing: object())
    monkeypatch.setattr(dw, "query", fake_query)
    monkeypatch.setattr(dw, "download_cached", lambda v, f, c: files[f])
    out = tmp_path / "out"
    assert dw.main(["--out-dir", str(out)]) == 0

    assert sorted(zip(seen["per"]["mondo"][1], seen["per"]["cid"][1])) == \
        [("MONDO:A", 10), ("MONDO:B", 20)]
    assert seen["overall"]["orphanet_rare"][1] == ["MONDO:A"]
    every = pd.read_csv(out / "wearables_rare_rare_d30_all.tsv", sep="\t", dtype=str)
    b = every.set_index("mondo_id").loc["MONDO:B"]
    assert (b["n_dx"], b["n_wear"], b["n_wear_before"]) == ("30", "<20", "0")
    top = pd.read_csv(out / "wearables_rare_rare_d30.tsv", sep="\t", dtype=str)
    assert list(top["mondo_id"]) == ["MONDO:A"]          # B under the floor
    assert "| <20 |" in (out / "wearables_rare_rare_d30.md").read_text()
