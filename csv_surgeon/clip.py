"""Clip numeric values in columns to [min, max] bounds."""
from __future__ import annotations
from typing import Dict, Iterable, Iterator, Optional


def _to_float(v: str) -> Optional[float]:
    try:
        return float(v)
    except (ValueError, TypeError):
        return None


def clip_column(
    rows: Iterable[Dict[str, str]],
    column: str,
    lower: Optional[float] = None,
    upper: Optional[float] = None,
    out_column: Optional[str] = None,
) -> Iterator[Dict[str, str]]:
    """Clip values in *column* to [lower, upper]. Writes result to out_column
    (defaults to column itself). Non-numeric values are passed through unchanged."""
    dest = out_column or column
    for row in rows:
        row = dict(row)
        val = _to_float(row.get(column, ""))
        if val is not None:
            if lower is not None and val < lower:
                val = lower
            if upper is not None and val > upper:
                val = upper
            # Preserve int-like appearance when possible
            row[dest] = str(int(val)) if val == int(val) else str(val)
        elif out_column:
            row[dest] = row.get(column, "")
        yield row


def clip_columns(
    rows: Iterable[Dict[str, str]],
    bounds: Dict[str, tuple],
) -> Iterator[Dict[str, str]]:
    """Apply clip_column for multiple columns.
    bounds maps column name -> (lower, upper) where either may be None.
    """
    rows = list(rows)
    for col, (lower, upper) in bounds.items():
        rows = list(clip_column(rows, col, lower, upper))
    yield from rows
