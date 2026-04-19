"""Outlier detection and removal using IQR or z-score thresholds."""
from __future__ import annotations
from typing import Iterator, Dict, Any, Optional


def _to_float(v: str) -> Optional[float]:
    try:
        return float(v)
    except (ValueError, TypeError):
        return None


def _iqr_bounds(values: list[float]) -> tuple[float, float]:
    s = sorted(values)
    n = len(s)
    q1 = s[n // 4]
    q3 = s[(3 * n) // 4]
    iqr = q3 - q1
    return q1 - 1.5 * iqr, q3 + 1.5 * iqr


def filter_outliers_iqr(
    rows: Iterator[Dict[str, Any]],
    column: str,
    keep_outliers: bool = False,
) -> Iterator[Dict[str, Any]]:
    """Filter rows whose *column* value is an IQR outlier.
    Buffers all rows to compute quartiles, then streams results."""
    buffered = list(rows)
    values = [v for r in buffered if (v := _to_float(r.get(column, ""))) is not None]
    if not values:
        yield from buffered
        return
    lo, hi = _iqr_bounds(values)
    for row in buffered:
        v = _to_float(row.get(column, ""))
        is_out = v is None or v < lo or v > hi
        if keep_outliers:
            if is_out:
                yield row
        else:
            if not is_out:
                yield row


def flag_iqr_outliers(
    rows: Iterator[Dict[str, Any]],
    column: str,
    out_column: str = "",
    flag_true: str = "1",
    flag_false: str = "0",
) -> Iterator[Dict[str, Any]]:
    """Add a flag column indicating whether each row is an IQR outlier."""
    out_col = out_column or f"{column}_iqr_outlier"
    buffered = list(rows)
    values = [v for r in buffered if (v := _to_float(r.get(column, ""))) is not None]
    if not values:
        for row in buffered:
            yield {**row, out_col: flag_false}
        return
    lo, hi = _iqr_bounds(values)
    for row in buffered:
        v = _to_float(row.get(column, ""))
        is_out = v is None or v < lo or v > hi
        yield {**row, out_col: flag_true if is_out else flag_false}
