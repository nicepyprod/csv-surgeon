"""Basic column statistics for CSV streams."""
from __future__ import annotations
from typing import Iterable, Iterator
import math


def _numeric(value: str) -> float | None:
    try:
        return float(value)
    except (ValueError, TypeError):
        return None


def column_stats(rows: Iterable[dict], column: str) -> dict:
    """Return count, min, max, mean, stddev, null_count for a column."""
    total = 0
    null_count = 0
    values: list[float] = []

    for row in rows:
        total += 1
        raw = row.get(column, "")
        if raw is None or raw.strip() == "":
            null_count += 1
            continue
        n = _numeric(raw)
        if n is None:
            null_count += 1
        else:
            values.append(n)

    count = len(values)
    if count == 0:
        return {"column": column, "total": total, "count": 0,
                "null_count": null_count, "min": None, "max": None,
                "mean": None, "stddev": None}

    mean = sum(values) / count
    variance = sum((v - mean) ** 2 for v in values) / count
    return {
        "column": column,
        "total": total,
        "count": count,
        "null_count": null_count,
        "min": min(values),
        "max": max(values),
        "mean": mean,
        "stddev": math.sqrt(variance),
    }


def multi_column_stats(rows: Iterable[dict], columns: list[str]) -> list[dict]:
    """Compute stats for multiple columns in a single pass."""
    totals = {c: 0 for c in columns}
    null_counts = {c: 0 for c in columns}
    values: dict[str, list[float]] = {c: [] for c in columns}

    for row in rows:
        for c in columns:
            totals[c] += 1
            raw = row.get(c, "")
            if raw is None or raw.strip() == "":
                null_counts[c] += 1
                continue
            n = _numeric(raw)
            if n is None:
                null_counts[c] += 1
            else:
                values[c].append(n)

    results = []
    for c in columns:
        vs = values[c]
        count = len(vs)
        if count == 0:
            results.append({"column": c, "total": totals[c], "count": 0,
                            "null_count": null_counts[c], "min": None,
                            "max": None, "mean": None, "stddev": None})
        else:
            mean = sum(vs) / count
            variance = sum((v - mean) ** 2 for v in vs) / count
            results.append({"column": c, "total": totals[c], "count": count,
                            "null_count": null_counts[c], "min": min(vs),
                            "max": max(vs), "mean": mean,
                            "stddev": math.sqrt(variance)})
    return results
