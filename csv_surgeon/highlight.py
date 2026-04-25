"""highlight.py – mark rows or cells that match a condition.

Adds a configurable marker column (or annotates an existing column)
so downstream tools can visually identify interesting rows.
"""
from __future__ import annotations

import re
from typing import Callable, Dict, Iterable, Iterator, List, Optional

Row = Dict[str, str]


def highlight_rows(
    rows: Iterable[Row],
    predicate: Callable[[Row], bool],
    *,
    out_column: str = "_highlight",
    true_value: str = "1",
    false_value: str = "0",
) -> Iterator[Row]:
    """Yield every row with *out_column* set to *true_value* / *false_value*."""
    for row in rows:
        marked = dict(row)
        marked[out_column] = true_value if predicate(row) else false_value
        yield marked


def highlight_by_value(
    rows: Iterable[Row],
    column: str,
    value: str,
    *,
    case_sensitive: bool = True,
    out_column: str = "_highlight",
    true_value: str = "1",
    false_value: str = "0",
) -> Iterator[Row]:
    """Highlight rows where *column* equals *value*."""
    if case_sensitive:
        pred: Callable[[Row], bool] = lambda r: r.get(column, "") == value
    else:
        v_lower = value.lower()
        pred = lambda r: r.get(column, "").lower() == v_lower
    return highlight_rows(
        rows, pred, out_column=out_column,
        true_value=true_value, false_value=false_value,
    )


def highlight_by_regex(
    rows: Iterable[Row],
    column: str,
    pattern: str,
    *,
    flags: int = 0,
    out_column: str = "_highlight",
    true_value: str = "1",
    false_value: str = "0",
) -> Iterator[Row]:
    """Highlight rows where *column* matches *pattern*."""
    rx = re.compile(pattern, flags)
    pred: Callable[[Row], bool] = lambda r: bool(rx.search(r.get(column, "")))
    return highlight_rows(
        rows, pred, out_column=out_column,
        true_value=true_value, false_value=false_value,
    )


def highlight_top_n(
    rows: Iterable[Row],
    column: str,
    n: int,
    *,
    out_column: str = "_highlight",
    true_value: str = "1",
    false_value: str = "0",
) -> Iterator[Row]:
    """Highlight the top-*n* rows by numeric value in *column* (descending)."""
    collected: List[Row] = list(rows)

    def _key(r: Row) -> float:
        try:
            return float(r.get(column, ""))
        except (ValueError, TypeError):
            return float("-inf")

    top_values = sorted(collected, key=_key, reverse=True)[:n]
    top_set = {id(r) for r in top_values}
    for row in collected:
        marked = dict(row)
        marked[out_column] = true_value if id(row) in top_set else false_value
        yield marked
