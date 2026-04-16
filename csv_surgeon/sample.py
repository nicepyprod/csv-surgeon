"""Sampling utilities: random and systematic row sampling."""
from __future__ import annotations

import random
from typing import Iterable, Iterator


def sample_rows(
    rows: Iterable[dict],
    n: int,
    seed: int | None = None,
) -> list[dict]:
    """Reservoir-sample up to *n* rows from an iterable (O(n) memory)."""
    rng = random.Random(seed)
    reservoir: list[dict] = []
    for i, row in enumerate(rows):
        if i < n:
            reservoir.append(row)
        else:
            j = rng.randint(0, i)
            if j < n:
                reservoir[j] = row
    return reservoir


def sample_fraction(
    rows: Iterable[dict],
    fraction: float,
    seed: int | None = None,
) -> Iterator[dict]:
    """Yield each row with probability *fraction* (0 < fraction <= 1)."""
    if not 0 < fraction <= 1:
        raise ValueError("fraction must be in (0, 1]")
    rng = random.Random(seed)
    for row in rows:
        if rng.random() < fraction:
            yield row


def systematic_sample(
    rows: Iterable[dict],
    step: int,
    offset: int = 0,
) -> Iterator[dict]:
    """Yield every *step*-th row starting from *offset*."""
    if step < 1:
        raise ValueError("step must be >= 1")
    for i, row in enumerate(rows):
        if i >= offset and (i - offset) % step == 0:
            yield row
