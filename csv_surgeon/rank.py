"""Row ranking utilities — add rank columns based on a numeric field."""
from __future__ import annotations
from typing import Iterator, Callable, Optional


def _to_float(v: str) -> float:
    try:
        return float(v)
    except (ValueError, TypeError):
        return float("nan")


def rank_rows(
    rows: list[dict],
    column: str,
    out_column: str = "rank",
    ascending: bool = True,
    method: str = "dense",  # "dense" | "row_number" | "percent"
) -> Iterator[dict]:
    """Yield rows with a new rank column.

    method:
        dense       – ties share a rank, no gaps  (1,1,2,3)
        row_number  – unique sequential rank in sort order (1,2,3,4)
        percent     – rank as fraction 0-1 (percentile)
    """
    if method not in ("dense", "row_number", "percent"):
        raise ValueError(f"Unknown rank method: {method!r}")

    data = list(rows)
    if not data:
        return

    indexed = [(i, _to_float(r.get(column, "")), r) for i, r in enumerate(data)]
    sorted_idx = sorted(indexed, key=lambda t: (float("inf") if t[1] != t[1] else t[1]),
                        reverse=not ascending)

    rank_map: dict[int, str] = {}
    n = len(sorted_idx)

    if method == "dense":
        current_rank = 1
        prev_val = object()
        for pos, (orig_i, val, _) in enumerate(sorted_idx):
            if val != prev_val:
                current_rank = pos + 1  # reset only when value changes
                # recalc dense
            rank_map[orig_i] = str(current_rank)
            prev_val = val
        # proper dense: re-do
        rank_map.clear()
        current_rank = 1
        prev_val = object()
        dense = 1
        for pos, (orig_i, val, _) in enumerate(sorted_idx):
            if val != prev_val:
                dense = current_rank
            rank_map[orig_i] = str(dense)
            prev_val = val
            current_rank += 1
    elif method == "row_number":
        for pos, (orig_i, val, _) in enumerate(sorted_idx):
            rank_map[orig_i] = str(pos + 1)
    else:  # percent
        for pos, (orig_i, val, _) in enumerate(sorted_idx):
            rank_map[orig_i] = f"{pos / max(n - 1, 1):.6f}"

    for i, row in enumerate(data):
        out = dict(row)
        out[out_column] = rank_map.get(i, "")
        yield out
