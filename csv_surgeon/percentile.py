"""Percentile and quantile computation for CSV columns."""
from __future__ import annotations

from typing import Iterable, Iterator
import math


def _to_float(value: str) -> float | None:
    try:
        return float(value)
    except (ValueError, TypeError):
        return None


def _percentile(sorted_values: list[float], p: float) -> float:
    """Linear interpolation percentile (same as numpy default)."""
    n = len(sorted_values)
    if n == 0:
        raise ValueError("Cannot compute percentile of empty sequence")
    if n == 1:
        return sorted_values[0]
    idx = (p / 100.0) * (n - 1)
    lo = int(math.floor(idx))
    hi = int(math.ceil(idx))
    if lo == hi:
        return sorted_values[lo]
    frac = idx - lo
    return sorted_values[lo] * (1 - frac) + sorted_values[hi] * frac


def percentile_column(
    rows: Iterable[dict],
    column: str,
    percentiles: list[float],
    out_columns: list[str] | None = None,
) -> Iterator[dict]:
    """Attach percentile rank columns to each row.

    For each row the value in *column* is compared against the precomputed
    percentile thresholds and a ``p_rank`` column (or custom names) is added
    indicating the highest percentile bucket the value falls into.
    """
    collected: list[dict] = list(rows)
    numeric = sorted(
        v for r in collected if (v := _to_float(r.get(column, ""))) is not None
    )
    if not numeric:
        yield from collected
        return

    thresholds = {p: _percentile(numeric, p) for p in percentiles}

    if out_columns is None:
        out_columns = [f"p{int(p)}" for p in percentiles]

    if len(out_columns) != len(percentiles):
        raise ValueError("out_columns length must match percentiles length")

    for row in collected:
        new_row = dict(row)
        val = _to_float(row.get(column, ""))
        for p, out_col in zip(percentiles, out_columns):
            if val is None:
                new_row[out_col] = ""
            else:
                new_row[out_col] = "1" if val <= thresholds[p] else "0"
        yield new_row


def quantile_summary(
    rows: Iterable[dict],
    column: str,
    q: int = 4,
) -> dict[str, float]:
    """Return a summary dict with min, max, and q-quantile cut points."""
    values = sorted(
        v for r in rows if (v := _to_float(r.get(column, ""))) is not None
    )
    if not values:
        return {}
    step = 100.0 / q
    result: dict[str, float] = {"min": values[0], "max": values[-1]}
    for i in range(1, q):
        p = step * i
        result[f"Q{i}"] = _percentile(values, p)
    return result
