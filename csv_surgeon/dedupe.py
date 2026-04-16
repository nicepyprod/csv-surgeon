"""Deduplication utilities for CSV rows."""
from typing import Iterable, Iterator, List, Optional


def dedupe_rows(
    rows: Iterable[dict],
    keys: Optional[List[str]] = None,
    keep: str = "first",
) -> Iterator[dict]:
    """Yield rows with duplicates removed.

    Args:
        rows: Iterable of row dicts.
        keys: Columns to use as the uniqueness key. None means all columns.
        keep: 'first' keeps first occurrence; 'last' keeps last occurrence.
    """
    if keep not in ("first", "last"):
        raise ValueError("keep must be 'first' or 'last'")

    if keep == "first":
        seen: set = set()
        for row in rows:
            fingerprint = _fingerprint(row, keys)
            if fingerprint not in seen:
                seen.add(fingerprint)
                yield row
    else:  # last
        # Buffer all rows, then yield last occurrence of each key
        index: dict = {}
        order: list = []
        for row in rows:
            fingerprint = _fingerprint(row, keys)
            if fingerprint not in index:
                order.append(fingerprint)
            index[fingerprint] = row
        for fp in order:
            yield index[fp]


def _fingerprint(row: dict, keys: Optional[List[str]]) -> tuple:
    """Return a hashable fingerprint for a row."""
    if keys is None:
        return tuple(sorted(row.items()))
    return tuple((k, row.get(k, "")) for k in keys)


def count_duplicates(rows: Iterable[dict], keys: Optional[List[str]] = None) -> int:
    """Return the number of duplicate rows (total rows minus unique rows)."""
    seen: set = set()
    total = 0
    dupes = 0
    for row in rows:
        total += 1
        fp = _fingerprint(row, keys)
        if fp in seen:
            dupes += 1
        else:
            seen.add(fp)
    return dupes
