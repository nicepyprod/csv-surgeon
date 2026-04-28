"""Imputation strategies for missing / empty CSV values."""
from __future__ import annotations

from statistics import mean, median
from typing import Dict, Iterable, Iterator, List


def _is_empty(v: str) -> bool:
    return v.strip() == ""


def _to_float(v: str) -> float | None:
    try:
        return float(v)
    except (ValueError, TypeError):
        return None


def impute_constant(
    rows: Iterable[Dict[str, str]],
    column: str,
    value: str,
) -> Iterator[Dict[str, str]]:
    """Replace empty cells in *column* with a fixed *value*."""
    for row in rows:
        out = dict(row)
        if column in out and _is_empty(out[column]):
            out[column] = value
        yield out


def impute_mean(
    rows: Iterable[Dict[str, str]],
    column: str,
    out_column: str | None = None,
) -> Iterator[Dict[str, str]]:
    """Replace empty cells with the column mean (two-pass)."""
    materialized: List[Dict[str, str]] = list(rows)
    nums = [_to_float(r[column]) for r in materialized if column in r and not _is_empty(r[column])]
    nums = [n for n in nums if n is not None]
    fill = str(mean(nums)) if nums else ""
    target = out_column or column
    for row in materialized:
        out = dict(row)
        if column in out and _is_empty(out[column]):
            out[target] = fill
        elif out_column and column in out:
            out[target] = out[column]
        yield out


def impute_median(
    rows: Iterable[Dict[str, str]],
    column: str,
    out_column: str | None = None,
) -> Iterator[Dict[str, str]]:
    """Replace empty cells with the column median (two-pass)."""
    materialized: List[Dict[str, str]] = list(rows)
    nums = [_to_float(r[column]) for r in materialized if column in r and not _is_empty(r[column])]
    nums = [n for n in nums if n is not None]
    fill = str(median(nums)) if nums else ""
    target = out_column or column
    for row in materialized:
        out = dict(row)
        if column in out and _is_empty(out[column]):
            out[target] = fill
        elif out_column and column in out:
            out[target] = out[column]
        yield out


def impute_mode(
    rows: Iterable[Dict[str, str]],
    column: str,
    out_column: str | None = None,
) -> Iterator[Dict[str, str]]:
    """Replace empty cells with the most frequent non-empty value."""
    materialized: List[Dict[str, str]] = list(rows)
    counts: Dict[str, int] = {}
    for row in materialized:
        v = row.get(column, "")
        if not _is_empty(v):
            counts[v] = counts.get(v, 0) + 1
    fill = max(counts, key=lambda k: counts[k]) if counts else ""
    target = out_column or column
    for row in materialized:
        out = dict(row)
        if column in out and _is_empty(out[column]):
            out[target] = fill
        elif out_column and column in out:
            out[target] = out[column]
        yield out
