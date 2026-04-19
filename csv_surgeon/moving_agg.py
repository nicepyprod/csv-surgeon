"""Group-by aggregations emitted as new columns on each row."""
from __future__ import annotations
from typing import Iterable, Iterator, Callable, Dict, List


def _numeric(v: str) -> float | None:
    try:
        return float(v)
    except (ValueError, TypeError):
        return None


def group_aggregate(
    rows: Iterable[Dict[str, str]],
    group_col: str,
    value_col: str,
    func: str = "sum",
    out_col: str | None = None,
) -> Iterator[Dict[str, str]]:
    """Two-pass: collect groups, then emit rows with aggregated column appended."""
    if func not in {"sum", "mean", "min", "max", "count"}:
        raise ValueError(f"Unsupported func: {func!r}")

    out_col = out_col or f"{value_col}_{func}"
    all_rows: List[Dict[str, str]] = list(rows)

    buckets: Dict[str, List[float]] = {}
    for row in all_rows:
        key = row.get(group_col, "")
        val = _numeric(row.get(value_col, ""))
        buckets.setdefault(key, [])
        if val is not None:
            buckets[key].append(val)

    def _agg(vals: List[float]) -> str:
        if not vals:
            return ""
        if func == "sum":
            return str(sum(vals))
        if func == "mean":
            return str(sum(vals) / len(vals))
        if func == "min":
            return str(min(vals))
        if func == "max":
            return str(max(vals))
        if func == "count":
            return str(len(vals))
        return ""

    agg_map = {k: _agg(v) for k, v in buckets.items()}

    for row in all_rows:
        out = dict(row)
        out[out_col] = agg_map.get(row.get(group_col, ""), "")
        yield out
