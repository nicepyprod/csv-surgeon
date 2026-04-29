"""Compute the difference between two date/datetime columns."""
from __future__ import annotations

from datetime import datetime
from typing import Iterator, Dict, Any, Optional

_UNITS = ("days", "hours", "minutes", "seconds")


def _parse(value: str, fmt: Optional[str]) -> Optional[datetime]:
    if not value or not value.strip():
        return None
    if fmt:
        try:
            return datetime.strptime(value.strip(), fmt)
        except ValueError:
            return None
    for f in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d",
              "%d/%m/%Y", "%m/%d/%Y"):
        try:
            return datetime.strptime(value.strip(), f)
        except ValueError:
            continue
    return None


def datetime_diff_column(
    rows: Iterator[Dict[str, Any]],
    col_a: str,
    col_b: str,
    out_column: str = "diff_days",
    unit: str = "days",
    fmt: Optional[str] = None,
    absolute: bool = False,
) -> Iterator[Dict[str, Any]]:
    """Yield rows with *out_column* = col_b - col_a expressed in *unit*.

    Supported units: days, hours, minutes, seconds.
    Empty or unparseable values produce an empty string.
    """
    if unit not in _UNITS:
        raise ValueError(f"unit must be one of {_UNITS}, got {unit!r}")

    divisors = {"days": 86400, "hours": 3600, "minutes": 60, "seconds": 1}
    div = divisors[unit]

    for row in rows:
        new = dict(row)
        dt_a = _parse(row.get(col_a, ""), fmt)
        dt_b = _parse(row.get(col_b, ""), fmt)
        if dt_a is None or dt_b is None:
            new[out_column] = ""
        else:
            delta_seconds = (dt_b - dt_a).total_seconds()
            if absolute:
                delta_seconds = abs(delta_seconds)
            new[out_column] = str(round(delta_seconds / div, 6)).rstrip("0").rstrip(".")
        yield new
