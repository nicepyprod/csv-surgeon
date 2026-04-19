"""Bucket / bin a numeric column into labeled ranges."""
from __future__ import annotations
from typing import Iterator, List, Optional, Tuple

Row = dict


def _find_bucket(
    value: float,
    edges: List[float],
    labels: List[str],
    include_lowest: bool,
) -> str:
    for i in range(len(edges) - 1):
        lo, hi = edges[i], edges[i + 1]
        if include_lowest and i == 0:
            if lo <= value <= hi:
                return labels[i]
        else:
            if lo < value <= hi:
                return labels[i]
    return ""


def bucket_column(
    rows: Iterator[Row],
    column: str,
    edges: List[float],
    labels: Optional[List[str]] = None,
    out_column: Optional[str] = None,
    include_lowest: bool = True,
) -> Iterator[Row]:
    """Assign each row a bucket label based on *column* value.

    *edges* must be a sorted list of N+1 boundary values producing N buckets.
    *labels* defaults to "edge[i]-edge[i+1]" strings.
    *out_column* defaults to "<column>_bucket".
    """
    if len(edges) < 2:
        raise ValueError("edges must contain at least 2 values")
    n_buckets = len(edges) - 1
    if labels is None:
        labels = [f"{edges[i]}-{edges[i+1]}" for i in range(n_buckets)]
    if len(labels) != n_buckets:
        raise ValueError(f"Expected {n_buckets} labels, got {len(labels)}")
    out = out_column or f"{column}_bucket"
    for row in rows:
        new = dict(row)
        raw = row.get(column, "")
        try:
            val = float(raw)
            new[out] = _find_bucket(val, edges, labels, include_lowest)
        except (ValueError, TypeError):
            new[out] = ""
        yield new


def equal_width_edges(min_val: float, max_val: float, bins: int) -> List[float]:
    """Return *bins+1* evenly spaced edges between min_val and max_val."""
    if bins < 1:
        raise ValueError("bins must be >= 1")
    step = (max_val - min_val) / bins
    return [min_val + step * i for i in range(bins + 1)]
