"""Flatten / explode rows on a multi-value column."""
from __future__ import annotations
from typing import Iterable, Iterator


def flatten_column(
    rows: Iterable[dict],
    column: str,
    sep: str = "|",
) -> Iterator[dict]:
    """Yield one row per value found in *column* after splitting on *sep*.

    Rows where the column is absent or empty are passed through unchanged.
    """
    for row in rows:
        value = row.get(column, "")
        if not value:
            yield row
            continue
        parts = [p.strip() for p in value.split(sep)]
        for part in parts:
            yield {**row, column: part}


def collapse_column(
    rows: Iterable[dict],
    column: str,
    key_column: str,
    sep: str = "|",
) -> Iterator[dict]:
    """Inverse of flatten: group rows sharing *key_column* and join *column* values.

    Rows are consumed eagerly per key group (stable order preserved).
    """
    seen: dict[str, dict] = {}
    order: list[str] = []
    groups: dict[str, list[str]] = {}

    for row in rows:
        key = row.get(key_column, "")
        if key not in seen:
            seen[key] = {k: v for k, v in row.items() if k != column}
            order.append(key)
            groups[key] = []
        val = row.get(column, "")
        if val:
            groups[key].append(val)

    for key in order:
        yield {**seen[key], column: sep.join(groups[key])}
