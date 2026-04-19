"""Date parsing and formatting utilities for CSV columns."""
from __future__ import annotations
from datetime import datetime
from typing import Iterable, Iterator, Optional

_COMMON_FORMATS = [
    "%Y-%m-%d",
    "%d/%m/%Y",
    "%m/%d/%Y",
    "%Y/%m/%d",
    "%d-%m-%Y",
    "%Y-%m-%dT%H:%M:%S",
    "%Y-%m-%d %H:%M:%S",
]


def _parse(value: str, formats: list[str]) -> Optional[datetime]:
    for fmt in formats:
        try:
            return datetime.strptime(value.strip(), fmt)
        except ValueError:
            continue
    return None


def parse_date_column(
    rows: Iterable[dict],
    column: str,
    out_column: Optional[str] = None,
    fmt: Optional[str] = None,
    extra_formats: Optional[list[str]] = None,
) -> Iterator[dict]:
    """Parse dates in *column*, storing datetime objects in *out_column*."""
    formats = ([fmt] if fmt else []) + (extra_formats or []) + _COMMON_FORMATS
    dest = out_column or column
    for row in rows:
        r = dict(row)
        val = r.get(column, "")
        dt = _parse(val, formats) if val else None
        r[dest] = dt
        yield r


def format_date_column(
    rows: Iterable[dict],
    column: str,
    out_fmt: str,
    out_column: Optional[str] = None,
    in_fmt: Optional[str] = None,
    extra_formats: Optional[list[str]] = None,
) -> Iterator[dict]:
    """Re-format date strings in *column* to *out_fmt*."""
    formats = ([in_fmt] if in_fmt else []) + (extra_formats or []) + _COMMON_FORMATS
    dest = out_column or column
    for row in rows:
        r = dict(row)
        val = r.get(column, "")
        if val:
            dt = _parse(val, formats)
            r[dest] = dt.strftime(out_fmt) if dt else ""
        else:
            r[dest] = ""
        yield r


def extract_date_part(
    rows: Iterable[dict],
    column: str,
    part: str,
    out_column: Optional[str] = None,
    in_fmt: Optional[str] = None,
) -> Iterator[dict]:
    """Extract a date part ('year','month','day','weekday') into *out_column*."""
    valid = {"year", "month", "day", "weekday", "hour", "minute", "second"}
    if part not in valid:
        raise ValueError(f"part must be one of {valid}")
    formats = ([in_fmt] if in_fmt else []) + _COMMON_FORMATS
    dest = out_column or f"{column}_{part}"
    for row in rows:
        r = dict(row)
        val = r.get(column, "")
        if val:
            dt = _parse(val, formats)
            if dt is not None:
                r[dest] = str(getattr(dt, part) if part != "weekday" else dt.weekday())
            else:
                r[dest] = ""
        else:
            r[dest] = ""
        yield r
