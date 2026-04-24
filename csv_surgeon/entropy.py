"""Entropy and information-theoretic metrics for CSV columns."""
from __future__ import annotations

import math
from collections import Counter
from typing import Dict, Iterable, Iterator, List, Optional


def _counts(values: List[str]) -> Dict[str, int]:
    return Counter(v for v in values if v != "")


def shannon_entropy(values: List[str]) -> Optional[float]:
    """Return Shannon entropy (bits) for a list of string values.

    Empty strings are ignored.  Returns None if no non-empty values.
    """
    counts = _counts(values)
    total = sum(counts.values())
    if total == 0:
        return None
    return -sum(
        (c / total) * math.log2(c / total) for c in counts.values()
    )


def entropy_column(
    rows: Iterable[Dict[str, str]],
    column: str,
    out_column: Optional[str] = None,
) -> Iterator[Dict[str, str]]:
    """Annotate each row with the Shannon entropy of *column* computed over
    the entire stream.  Because entropy requires a full pass, all rows are
    buffered in memory.
    """
    buf = list(rows)
    values = [r.get(column, "") for r in buf]
    h = shannon_entropy(values)
    h_str = "" if h is None else f"{h:.6f}"
    out = out_column or f"{column}_entropy"
    for row in buf:
        yield {**row, out: h_str}


def mutual_information(
    rows: Iterable[Dict[str, str]],
    col_a: str,
    col_b: str,
) -> Optional[float]:
    """Return the mutual information (bits) between two columns."""
    buf = list(rows)
    pairs = [
        (r.get(col_a, ""), r.get(col_b, ""))
        for r in buf
        if r.get(col_a, "") != "" and r.get(col_b, "") != ""
    ]
    if not pairs:
        return None
    total = len(pairs)
    joint: Counter = Counter(pairs)
    count_a: Counter = Counter(a for a, _ in pairs)
    count_b: Counter = Counter(b for _, b in pairs)
    mi = 0.0
    for (a, b), c_ab in joint.items():
        p_ab = c_ab / total
        p_a = count_a[a] / total
        p_b = count_b[b] / total
        mi += p_ab * math.log2(p_ab / (p_a * p_b))
    return mi
