"""Rolling window join: attach preceding/following N rows of context to each row."""
from __future__ import annotations

from collections import deque
from typing import Dict, Generator, Iterable, List, Optional


Row = Dict[str, str]


def _prefix_row(row: Row, prefix: str) -> Row:
    return {f"{prefix}{k}": v for k, v in row.items()}


def window_context(
    rows: Iterable[Row],
    before: int = 1,
    after: int = 1,
    prefix_before: str = "prev_",
    prefix_after: str = "next_",
    fill: str = "",
) -> Generator[Row, None, None]:
    """Yield each row enriched with `before` preceding rows and `after` following rows.

    Missing context cells are filled with *fill* (default empty string).
    """
    if before < 0 or after < 0:
        raise ValueError("before and after must be non-negative integers")

    buffer: List[Row] = []
    all_rows = list(rows)
    if not all_rows:
        return

    header = list(all_rows[0].keys())
    empty_row: Row = {k: fill for k in header}

    for idx, row in enumerate(all_rows):
        merged: Row = dict(row)

        for lag in range(1, before + 1):
            src = all_rows[idx - lag] if idx - lag >= 0 else empty_row
            merged.update(_prefix_row(src, f"{prefix_before}{lag}_" if before > 1 else prefix_before))

        for lead in range(1, after + 1):
            src = all_rows[idx + lead] if idx + lead < len(all_rows) else empty_row
            merged.update(_prefix_row(src, f"{prefix_after}{lead}_" if after > 1 else prefix_after))

        yield merged


def window_diff(
    rows: Iterable[Row],
    column: str,
    out_column: Optional[str] = None,
    fill: str = "",
) -> Generator[Row, None, None]:
    """Add a column with the difference between the current and previous row value."""
    out = out_column or f"{column}_diff"
    prev: Optional[str] = None
    for row in rows:
        merged = dict(row)
        cur = row.get(column, "")
        if prev is None or cur == "" or prev == "":
            merged[out] = fill
        else:
            try:
                merged[out] = str(float(cur) - float(prev))
            except ValueError:
                merged[out] = fill
        prev = cur if cur != "" else prev
        yield merged
