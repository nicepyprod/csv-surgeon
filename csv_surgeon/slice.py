"""Row slicing utilities — head, tail, and range extraction."""
from __future__ import annotations
from typing import Iterator


def head_rows(rows: Iterator[dict], n: int) -> Iterator[dict]:
    """Yield the first *n* rows."""
    for i, row in enumerate(rows):
        if i >= n:
            break
        yield row


def tail_rows(rows: Iterator[dict], n: int) -> list[dict]:
    """Return the last *n* rows (buffers internally)."""
    buf: list[dict] = []
    for row in rows:
        buf.append(row)
        if len(buf) > n:
            buf.pop(0)
    return buf


def slice_rows(
    rows: Iterator[dict],
    start: int = 0,
    stop: int | None = None,
    step: int = 1,
) -> Iterator[dict]:
    """Yield rows in the half-open range [start, stop) with *step*."""
    if step < 1:
        raise ValueError("step must be >= 1")
    for i, row in enumerate(rows):
        if stop is not None and i >= stop:
            break
        if i >= start and (i - start) % step == 0:
            yield row
