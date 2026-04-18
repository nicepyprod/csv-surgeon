"""unnest.py – split a multi-value cell into multiple rows."""
from __future__ import annotations
from typing import Iterator


def unnest_column(
    rows: Iterator[dict],
    column: str,
    sep: str = "|",
) -> Iterator[dict]:
    """For each row, split *column* on *sep* and emit one row per value.

    Rows where *column* is missing or empty are passed through unchanged.
    """
    for row in rows:
        value = row.get(column, "")
        if not value:
            yield row
            continue
        parts = value.split(sep)
        for part in parts:
            yield {**row, column: part.strip()}


def nest_column(
    rows: Iterator[dict],
    column: str,
    group_by: str,
    sep: str = "|",
) -> Iterator[dict]:
    """Inverse of unnest: collapse rows sharing the same *group_by* value
    by joining *column* values with *sep*.

    Preserves the first occurrence of all other fields.
    Rows are consumed eagerly and re-emitted in group order.
    """
    from collections import OrderedDict

    groups: OrderedDict[str, dict] = OrderedDict()
    accum: dict[str, list[str]] = {}

    for row in rows:
        key = row.get(group_by, "")
        if key not in groups:
            groups[key] = dict(row)
            accum[key] = [row.get(column, "")]
        else:
            accum[key].append(row.get(column, ""))

    for key, base_row in groups.items():
        base_row[column] = sep.join(v for v in accum[key] if v)
        yield base_row
