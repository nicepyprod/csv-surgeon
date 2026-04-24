"""Time-based resampling: group rows by a date column into fixed periods."""
from __future__ import annotations

from collections import defaultdict
from typing import Callable, Dict, Iterable, Iterator, List, Optional

_PERIODS = {"year": "%Y", "month": "%Y-%m", "week": "%Y-W%W", "day": "%Y-%m-%d", "hour": "%Y-%m-%dT%H"}


def _parse_date(value: str, fmt: Optional[str]):
    from datetime import datetime
    if not value:
        return None
    if fmt:
        return datetime.strptime(value, fmt)
    for f in ("%Y-%m-%d", "%Y-%m-%dT%H:%M:%S", "%d/%m/%Y", "%m/%d/%Y"):
        try:
            return datetime.strptime(value, f)
        except ValueError:
            continue
    return None


def resample_rows(
    rows: Iterable[Dict[str, str]],
    date_col: str,
    period: str = "month",
    agg_col: Optional[str] = None,
    agg_func: str = "count",
    date_fmt: Optional[str] = None,
    out_col: str = "value",
) -> Iterator[Dict[str, str]]:
    """Aggregate rows by time period bucket.

    Yields one row per bucket with keys: *date_col* (bucket label) and *out_col*.
    """
    if period not in _PERIODS:
        raise ValueError(f"period must be one of {list(_PERIODS)}")
    bucket_fmt = _PERIODS[period]
    buckets: Dict[str, List[str]] = defaultdict(list)
    for row in rows:
        raw = row.get(date_col, "")
        dt = _parse_date(raw, date_fmt)
        if dt is None:
            continue
        label = dt.strftime(bucket_fmt)
        val = row.get(agg_col, "") if agg_col else ""
        buckets[label].append(val)

    for label in sorted(buckets):
        vals = buckets[label]
        result = _aggregate(vals, agg_func)
        yield {date_col: label, out_col: result}


def _aggregate(values: List[str], func: str) -> str:
    numeric = []
    for v in values:
        try:
            numeric.append(float(v))
        except (ValueError, TypeError):
            pass
    if func == "count":
        return str(len(values))
    if not numeric:
        return ""
    if func == "sum":
        return str(sum(numeric))
    if func == "mean":
        return str(sum(numeric) / len(numeric))
    if func == "min":
        return str(min(numeric))
    if func == "max":
        return str(max(numeric))
    raise ValueError(f"Unknown agg_func: {func}")
