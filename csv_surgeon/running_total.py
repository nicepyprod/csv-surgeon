"""running_total.py – per-group running totals (cumulative sum within groups)."""
from __future__ import annotations

from typing import Callable, Dict, Generator, Iterable, List, Optional


def _to_float(v: str) -> Optional[float]:
    try:
        return float(v)
    except (ValueError, TypeError):
        return None


def running_total_column(
    rows: Iterable[Dict[str, str]],
    value_col: str,
    *,
    group_col: Optional[str] = None,
    out_col: str = "",
    reset_on_empty: bool = True,
) -> Generator[Dict[str, str], None, None]:
    """Yield rows with a new column containing the running total of *value_col*.

    Parameters
    ----------
    rows:
        Input row dicts (must share a common header set).
    value_col:
        Column whose numeric values are accumulated.
    group_col:
        Optional column to partition by; the running total resets for each
        distinct value in this column.
    out_col:
        Name of the output column.  Defaults to ``"<value_col>_running_total"``.
    reset_on_empty:
        When *True* (default) an empty or non-numeric cell resets the
        accumulator to 0 and emits an empty string for that row.
    """
    if not out_col:
        out_col = f"{value_col}_running_total"

    totals: Dict[str, float] = {}  # group_key -> running total

    for row in rows:
        group_key = row.get(group_col, "__all__") if group_col else "__all__"
        current = totals.get(group_key, 0.0)

        raw = row.get(value_col, "")
        val = _to_float(raw)

        if val is None:
            if reset_on_empty:
                totals[group_key] = 0.0
            new_row = dict(row)
            new_row[out_col] = ""
        else:
            current += val
            totals[group_key] = current
            new_row = dict(row)
            new_row[out_col] = str(current)

        yield new_row


def running_total_columns(
    rows: Iterable[Dict[str, str]],
    specs: List[Dict],
) -> Generator[Dict[str, str], None, None]:
    """Apply multiple running-total specs in sequence.

    Each spec is a dict accepted as keyword arguments to
    :func:`running_total_column` (``value_col`` is required).
    """
    result: Iterable[Dict[str, str]] = rows
    for spec in specs:
        spec = dict(spec)  # copy so we can pop
        value_col = spec.pop("value_col")
        result = running_total_column(result, value_col, **spec)
    return result  # type: ignore[return-value]
