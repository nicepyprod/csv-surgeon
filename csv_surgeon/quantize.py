"""Quantize numeric columns into discrete bins of equal width or custom edges."""
from __future__ import annotations

from typing import Iterable, Iterator, List, Optional


def _to_float(v: str) -> Optional[float]:
    try:
        return float(v)
    except (ValueError, TypeError):
        return None


def quantize_column(
    rows: Iterable[dict],
    column: str,
    edges: List[float],
    out_column: Optional[str] = None,
    labels: Optional[List[str]] = None,
    include_lowest: bool = True,
) -> Iterator[dict]:
    """Assign each value in *column* to a bin defined by *edges*.

    *edges* must be sorted ascending and contain at least 2 values.
    The number of bins is ``len(edges) - 1``.
    *labels* must have length ``len(edges) - 1`` when provided.
    """
    if len(edges) < 2:
        raise ValueError("edges must contain at least 2 values")
    edges = sorted(edges)
    n_bins = len(edges) - 1
    if labels is not None and len(labels) != n_bins:
        raise ValueError("labels length must equal len(edges) - 1")
    out_col = out_column or f"{column}_bin"

    def _find(val: float) -> str:
        for i in range(n_bins):
            lo, hi = edges[i], edges[i + 1]
            if i == 0 and include_lowest:
                if lo <= val <= hi:
                    return labels[i] if labels else f"[{lo},{hi}]"
            else:
                if lo < val <= hi:
                    return labels[i] if labels else f"({lo},{hi}]"
        return ""

    for row in rows:
        row = dict(row)
        raw = row.get(column, "")
        fval = _to_float(raw)
        row[out_col] = _find(fval) if fval is not None else ""
        yield row


def equal_width_quantize(
    rows: Iterable[dict],
    column: str,
    n_bins: int,
    out_column: Optional[str] = None,
    labels: Optional[List[str]] = None,
) -> Iterator[dict]:
    """Two-pass quantize: first scan to find min/max, then assign bins."""
    if n_bins < 1:
        raise ValueError("n_bins must be >= 1")
    data = list(rows)
    values = [_to_float(r.get(column, "")) for r in data]
    numeric = [v for v in values if v is not None]
    if not numeric:
        for row in data:
            row = dict(row)
            row[out_column or f"{column}_bin"] = ""
            yield row
        return
    lo, hi = min(numeric), max(numeric)
    if lo == hi:
        edges = [lo - 0.5, hi + 0.5]
    else:
        step = (hi - lo) / n_bins
        edges = [lo + i * step for i in range(n_bins + 1)]
    yield from quantize_column(data, column, edges, out_column=out_column, labels=labels)
