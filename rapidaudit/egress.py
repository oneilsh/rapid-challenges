"""All of Us small-count egress rule, shared by every audit.

Any participant count from 1 to 19 leaves the Workbench as "<20"; 0 is shown as-is.
Anything derived from a masked count (a percentage, a difference, a ratio) would let a
reader back it out, so it must not be published next to the mask: drop the column, or
compute it only where every input is >= the floor.
"""
from __future__ import annotations

import pandas as pd

EGRESS_FLOOR = 20


def cell(n, floor: int = EGRESS_FLOOR) -> str:
    """One count as an egress-safe string: 0 -> "0", 1..floor-1 -> "<20", else "1,234"."""
    n = int(n)
    return f"<{floor}" if 0 < n < floor else f"{n:,}"


def mask_counts(df: pd.DataFrame, cols, floor: int = EGRESS_FLOOR) -> pd.DataFrame:
    """Copy of `df` with each count column in `cols` passed through `cell`."""
    out = df.copy()
    for c in cols:
        out[c] = out[c].map(lambda n: cell(n, floor))
    return out
