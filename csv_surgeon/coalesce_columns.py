"""coalesce_columns: return the first non-empty value across a list of columns."""
from __future__ import annotations

from typing import Dict, Iterable, Iterator, List, Optional


def coalesce_columns(
    rows: Iterable[Dict[str, str]],
    columns: List[str],
    out_column: str,
    *,
    default: str = "",
    remove_sources: bool = False,
) -> Iterator[Dict[str, str]]:
    """Yield rows with *out_column* set to the first non-empty value in *columns*.

    Parameters
    ----------
    rows:
        Iterable of row dicts (header already consumed).
    columns:
        Ordered list of column names to inspect.
    out_column:
        Name of the output column.
    default:
        Value to use when all source columns are empty / missing.
    remove_sources:
        If *True*, drop the source columns from the output row.
    """
    for row in rows:
        value: Optional[str] = None
        for col in columns:
            candidate = row.get(col, "")
            if candidate.strip():
                value = candidate
                break
        out_row = dict(row)
        out_row[out_column] = value if value is not None else default
        if remove_sources:
            for col in columns:
                if col != out_column:
                    out_row.pop(col, None)
        yield out_row


def first_non_empty(
    rows: Iterable[Dict[str, str]],
    columns: List[str],
) -> Iterator[Optional[str]]:
    """Yield the first non-empty value for each row across *columns*.

    Convenience generator when you only need the resolved values, not full rows.
    """
    for row in rows:
        for col in columns:
            candidate = row.get(col, "")
            if candidate.strip():
                yield candidate
                break
        else:
            yield None
