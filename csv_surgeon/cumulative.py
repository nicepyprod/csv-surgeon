"""Cumulative aggregations over a streaming column."""
from __future__ import annotations
from typing import Iterator, Dict, Any, Optional


def _to_float(v: str) -> Optional[float]:
    try:
        return float(v)
    except (ValueError, TypeError):
        return None


def cumulative_sum(
    rows: Iterator[Dict[str, Any]],
    column: str,
    out_column: Optional[str] = None,
) -> Iterator[Dict[str, Any]]:
    """Yield rows with a running cumulative sum appended."""
    out = out_column or f"{column}_cumsum"
    total = 0.0
    for row in rows:
        v = _to_float(row.get(column, ""))
        if v is not None:
            total += v
        r = dict(row)
        r[out] = "" if v is None else str(total)
        yield r


def cumulative_mean(
    rows: Iterator[Dict[str, Any]],
    column: str,
    out_column: Optional[str] = None,
) -> Iterator[Dict[str, Any]]:
    """Yield rows with a running cumulative mean appended."""
    out = out_column or f"{column}_cummean"
    total = 0.0
    count = 0
    for row in rows:
        v = _to_float(row.get(column, ""))
        if v is not None:
            total += v
            count += 1
        r = dict(row)
        r[out] = "" if count == 0 else str(total / count)
        yield r


def cumulative_max(
    rows: Iterator[Dict[str, Any]],
    column: str,
    out_column: Optional[str] = None,
) -> Iterator[Dict[str, Any]]:
    """Yield rows with a running cumulative max appended."""
    out = out_column or f"{column}_cummax"
    cur_max: Optional[float] = None
    for row in rows:
        v = _to_float(row.get(column, ""))
        if v is not None:
            cur_max = v if cur_max is None else max(cur_max, v)
        r = dict(row)
        r[out] = "" if cur_max is None else str(cur_max)
        yield r


def cumulative_min(
    rows: Iterator[Dict[str, Any]],
    column: str,
    out_column: Optional[str] = None,
) -> Iterator[Dict[str, Any]]:
    """Yield rows with a running cumulative min appended."""
    out = out_column or f"{column}_cummin"
    cur_min: Optional[float] = None
    for row in rows:
        v = _to_float(row.get(column, ""))
        if v is not None:
            cur_min = v if cur_min is None else min(cur_min, v)
        r = dict(row)
        r[out] = "" if cur_min is None else str(cur_min)
        yield r
