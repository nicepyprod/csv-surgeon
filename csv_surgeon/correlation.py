"""Compute pairwise Pearson correlation between numeric columns."""
from __future__ import annotations

import math
from typing import Dict, Iterable, List, Optional, Tuple


def _to_float(val: str) -> Optional[float]:
    try:
        return float(val)
    except (ValueError, TypeError):
        return None


def _pearson(xs: List[float], ys: List[float]) -> Optional[float]:
    """Return Pearson r for two equal-length lists of floats."""
    n = len(xs)
    if n < 2:
        return None
    mean_x = sum(xs) / n
    mean_y = sum(ys) / n
    num = sum((x - mean_x) * (y - mean_y) for x, y in zip(xs, ys))
    den_x = math.sqrt(sum((x - mean_x) ** 2 for x in xs))
    den_y = math.sqrt(sum((y - mean_y) ** 2 for y in ys))
    if den_x == 0 or den_y == 0:
        return None
    return num / (den_x * den_y)


def correlation_matrix(
    rows: Iterable[Dict[str, str]],
    columns: List[str],
) -> Dict[Tuple[str, str], Optional[float]]:
    """Return a dict mapping (col_a, col_b) -> Pearson r for all pairs."""
    data: Dict[str, List[float]] = {col: [] for col in columns}
    for row in rows:
        vals = {col: _to_float(row.get(col, "")) for col in columns}
        if all(v is not None for v in vals.values()):
            for col in columns:
                data[col].append(vals[col])  # type: ignore[arg-type]

    result: Dict[Tuple[str, str], Optional[float]] = {}
    for i, col_a in enumerate(columns):
        for col_b in columns[i:]:
            r = 1.0 if col_a == col_b else _pearson(data[col_a], data[col_b])
            result[(col_a, col_b)] = r
            result[(col_b, col_a)] = r
    return result


def correlation_rows(
    rows: Iterable[Dict[str, str]],
    columns: List[str],
) -> Iterable[Dict[str, str]]:
    """Yield rows of a correlation matrix suitable for CSV output."""
    matrix = correlation_matrix(rows, columns)
    for col_a in columns:
        out: Dict[str, str] = {"column": col_a}
        for col_b in columns:
            val = matrix.get((col_a, col_b))
            out[col_b] = "" if val is None else f"{val:.6f}"
        yield out
