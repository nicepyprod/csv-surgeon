"""Row aggregation: group-by with sum/count/min/max/mean."""
from collections import defaultdict
from typing import Iterable, Iterator, Dict, List


def _numeric(v: str) -> float:
    try:
        return float(v)
    except (ValueError, TypeError):
        return None


def aggregate_rows(
    rows: Iterable[Dict[str, str]],
    group_by: List[str],
    agg_col: str,
    func: str = "sum",
) -> Iterator[Dict[str, str]]:
    """Group rows by *group_by* columns and aggregate *agg_col*.

    func: sum | count | min | max | mean
    """
    buckets: Dict[tuple, List[float]] = defaultdict(list)
    key_order: List[tuple] = []

    for row in rows:
        key = tuple(row.get(c, "") for c in group_by)
        if key not in buckets:
            key_order.append(key)
        val = _numeric(row.get(agg_col, ""))
        if val is not None:
            buckets[key].append(val)

    for key in key_order:
        vals = buckets[key]
        if func == "sum":
            result = sum(vals)
        elif func == "count":
            result = len(vals)
        elif func == "min":
            result = min(vals) if vals else ""
        elif func == "max":
            result = max(vals) if vals else ""
        elif func == "mean":
            result = sum(vals) / len(vals) if vals else ""
        else:
            raise ValueError(f"Unknown aggregation function: {func}")

        out = dict(zip(group_by, key))
        out[f"{func}_{agg_col}"] = "" if result == "" else str(result)
        yield out
