"""Frequency / value-count helpers for CSV rows."""
from __future__ import annotations
from collections import Counter
from typing import Iterable, Iterator


def value_counts(
    rows: Iterable[dict],
    column: str,
    *,
    normalize: bool = False,
    sort: bool = True,
) -> list[dict]:
    """Return value-count rows for *column*.

    Each output row has keys ``value``, ``count``, and optionally ``percent``.
    """
    counter: Counter = Counter()
    for row in rows:
        counter[row.get(column, "")] += 1
    total = sum(counter.values())
    items = counter.most_common() if sort else list(counter.items())
    result = []
    for value, count in items:
        rec = {"value": value, "count": str(count)}
        if normalize:
            rec["percent"] = f"{count / total * 100:.2f}" if total else "0.00"
        result.append(rec)
    return result


def top_n(
    rows: Iterable[dict],
    column: str,
    n: int = 10,
) -> list[dict]:
    """Return the top-*n* most frequent values for *column*."""
    return value_counts(rows, column, sort=True)[:n]


def frequency_filter(
    rows: Iterable[dict],
    column: str,
    *,
    min_count: int = 1,
) -> Iterator[dict]:
    """Yield only rows whose *column* value appears at least *min_count* times."""
    rows_list = list(rows)
    counter: Counter = Counter(row.get(column, "") for row in rows_list)
    for row in rows_list:
        if counter[row.get(column, "")] >= min_count:
            yield row
