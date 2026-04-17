"""Fill and impute missing values in CSV rows."""
from __future__ import annotations
from typing import Iterable, Iterator


def fill_value(
    rows: Iterable[dict],
    column: str,
    value: str,
) -> Iterator[dict]:
    """Replace empty/missing values in *column* with *value*."""
    for row in rows:
        out = dict(row)
        if column in out and out[column].strip() == "":
            out[column] = value
        yield out


def fill_forward(
    rows: Iterable[dict],
    column: str,
) -> Iterator[dict]:
    """Forward-fill empty values in *column* from the previous non-empty value."""
    last: str = ""
    for row in rows:
        out = dict(row)
        if column in out:
            if out[column].strip() == "":
                out[column] = last
            else:
                last = out[column]
        yield out


def fill_backward(
    rows: Iterable[dict],
    column: str,
) -> Iterator[dict]:
    """Backward-fill empty values in *column* from the next non-empty value."""
    collected = list(rows)
    last: str = ""
    for row in reversed(collected):
        if column in row and row[column].strip() == "":
            row[column] = last
        elif column in row:
            last = row[column]
    yield from collected


def fill_mean(
    rows: Iterable[dict],
    column: str,
) -> Iterator[dict]:
    """Fill empty values in *column* with the mean of non-empty numeric values."""
    collected = list(rows)
    nums = []
    for row in collected:
        v = row.get(column, "").strip()
        try:
            nums.append(float(v))
        except ValueError:
            pass
    mean_str = f"{sum(nums) / len(nums):.6g}" if nums else ""
    for row in collected:
        out = dict(row)
        if column in out and out[column].strip() == "":
            out[column] = mean_str
        yield out
