"""The small-count egress rule (rapidaudit/egress.py)."""
import pandas as pd

from rapidaudit.egress import cell, mask_counts


def test_cell_masks_1_to_19_and_keeps_zero():
    assert [cell(n) for n in (0, 1, 19, 20, 12345)] == ["0", "<20", "<20", "20", "12,345"]
    assert cell(19.0) == "<20"   # counts filled from NaN arrive as floats


def test_mask_counts_only_touches_named_columns():
    df = pd.DataFrame({"name": ["a", "b"], "n": [5, 300], "m": [0, 21]})
    out = mask_counts(df, ["n", "m"])
    assert out.to_dict("list") == {"name": ["a", "b"], "n": ["<20", "300"], "m": ["0", "21"]}
    assert df["n"].tolist() == [5, 300]   # input untouched
