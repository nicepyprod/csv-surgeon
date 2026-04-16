"""Sorting utilities for CSV rows."""
from typing import Iterable, Iterator, List, Optional


def sort_rows(
    rows: Iterable[dict],
    key: str,
    reverse: bool = False,
    numeric: bool = False,
) -> Iterator[dict]:
    """Sort rows by a column key. Loads all rows into memory."""
    def _key(row: dict):
        val = row.get(key, "")
        if numeric:
            try:
                return float(val)
            except (ValueError, TypeError):
                return 0.0
        return val

    yield from sorted(rows, key=_key, reverse=reverse)


def sort_rows_multi(
    rows: Iterable[dict],
    keys: List[str],
    reverse: bool = False,
    numeric_keys: Optional[List[str]] = None,
) -> Iterator[dict]:
    """Sort rows by multiple column keys."""
    numeric_keys = set(numeric_keys or [])

    def _key(row: dict):
        parts = []
        for k in keys:
            val = row.get(k, "")
            if k in numeric_keys:
                try:
                    parts.append(float(val))
                except (ValueError, TypeError):
                    parts.append(0.0)
            else:
                parts.append(val)
        return parts

    yield from sorted(rows, key=_key, reverse=reverse)
