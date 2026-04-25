"""Cartesian product and weighted sampling utilities for CSV rows."""
from __future__ import annotations

import itertools
from typing import Dict, Iterable, Iterator, List, Optional


Row = Dict[str, str]


def cartesian_product(
    left: Iterable[Row],
    right: Iterable[Row],
    left_prefix: str = "l_",
    right_prefix: str = "r_",
) -> Iterator[Row]:
    """Yield every combination of rows from *left* and *right*.

    Column names are prefixed to avoid collisions.
    """
    right_list: List[Row] = list(right)
    if not right_list:
        return
    for l_row in left:
        for r_row in right_list:
            merged: Row = {}
            for k, v in l_row.items():
                merged[f"{left_prefix}{k}"] = v
            for k, v in r_row.items():
                merged[f"{right_prefix}{k}"] = v
            yield merged


def zip_rows(
    left: Iterable[Row],
    right: Iterable[Row],
    fill_value: str = "",
) -> Iterator[Row]:
    """Zip two row streams side-by-side.

    If one stream is longer, missing values are filled with *fill_value*.
    Column names that clash in the right stream are suffixed with ``_right``.
    """
    sentinel = object()
    for l_row, r_row in itertools.zip_longest(left, right, fillvalue=sentinel):
        merged: Row = {}
        if l_row is sentinel:
            l_row = {}
        if r_row is sentinel:
            r_row = {}
        merged.update(l_row)  # type: ignore[arg-type]
        for k, v in r_row.items():  # type: ignore[union-attr]
            key = f"{k}_right" if k in merged else k
            merged[key] = v
        # Fill any columns missing from the shorter stream
        for k in list(merged):
            if merged[k] is sentinel:
                merged[k] = fill_value
        yield merged


def repeat_rows(
    rows: Iterable[Row],
    times: int,
) -> Iterator[Row]:
    """Yield each row *times* times in sequence."""
    if times < 1:
        raise ValueError("times must be >= 1")
    for row in rows:
        for _ in range(times):
            yield dict(row)
