"""Pivot-table aggregation: group rows by one or more key columns and
aggregate a value column into a wide table with one column per unique
pivot value."""
from __future__ import annotations

from collections import defaultdict
from typing import Callable, Dict, Iterable, Iterator, List, Optional


def _numeric(v: str) -> Optional[float]:
    try:
        return float(v)
    except (ValueError, TypeError):
        return None


def _agg(values: List[str], func: str) -> str:
    nums = [n for n in (_numeric(v) for v in values) if n is not None]
    if func == "count":
        return str(len(values))
    if not nums:
        return ""
    if func == "sum":
        return str(sum(nums))
    if func == "mean":
        return str(sum(nums) / len(nums))
    if func == "min":
        return str(min(nums))
    if func == "max":
        return str(max(nums))
    if func == "first":
        return values[0] if values else ""
    if func == "last":
        return values[-1] if values else ""
    raise ValueError(f"Unknown aggfunc: {func!r}")


def pivot_table(
    rows: Iterable[Dict[str, str]],
    index: List[str],
    pivot_col: str,
    value_col: str,
    aggfunc: str = "sum",
    fill_value: str = "",
) -> Iterator[Dict[str, str]]:
    """Group *rows* by *index* columns, pivot *pivot_col* into new columns,
    and aggregate *value_col* with *aggfunc*."""
    # bucket: index_key -> pivot_value -> [raw values]
    bucket: Dict[tuple, Dict[str, List[str]]] = defaultdict(lambda: defaultdict(list))
    index_rows: Dict[tuple, Dict[str, str]] = {}
    pivot_values_seen: list = []
    pivot_set: set = set()

    for row in rows:
        key = tuple(row.get(c, "") for c in index)
        pval = row.get(pivot_col, "")
        vval = row.get(value_col, "")
        bucket[key][pval].append(vval)
        if key not in index_rows:
            index_rows[key] = {c: row.get(c, "") for c in index}
        if pval not in pivot_set:
            pivot_set.add(pval)
            pivot_values_seen.append(pval)

    for key, base in index_rows.items():
        out = dict(base)
        for pval in pivot_values_seen:
            vals = bucket[key].get(pval, [])
            out[pval] = _agg(vals, aggfunc) if vals else fill_value
        yield out
