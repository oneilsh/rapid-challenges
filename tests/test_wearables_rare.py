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
