"""Row filtering utilities for csv-surgeon."""

from typing import Callable, Dict, Iterator, List, Optional


def filter_rows(
    rows: Iterator[Dict[str, str]],
    predicate: Callable[[Dict[str, str]], bool],
) -> Iterator[Dict[str, str]]:
    """Yield only rows for which predicate returns True."""
    for row in rows:
        if predicate(row):
            yield row


def filter_by_value(
    rows: Iterator[Dict[str, str]],
    column: str,
    value: str,
    case_sensitive: bool = True,
) -> Iterator[Dict[str, str]]:
    """Yield rows where column equals value."""
    if not case_sensitive:
        value = value.lower()

    for row in rows:
        cell = row.get(column, "")
        if not case_sensitive:
            cell = cell.lower()
        if cell == value:
            yield row


def filter_by_contains(
    rows: Iterator[Dict[str, str]],
    column: str,
    substring: str,
    case_sensitive: bool = True,
) -> Iterator[Dict[str, str]]:
    """Yield rows where column contains substring."""
    if not case_sensitive:
        substring = substring.lower()

    for row in rows:
        cell = row.get(column, "")
        if not case_sensitive:
            cell = cell.lower()
        if substring in cell:
            yield row


def filter_columns(
    rows: Iterator[Dict[str, str]],
    columns: List[str],
) -> Iterator[Dict[str, str]]:
    """Yield rows with only the specified columns retained."""
    for row in rows:
        yield {col: row[col] for col in columns if col in row}


def drop_empty(
    rows: Iterator[Dict[str, str]],
    column: Optional[str] = None,
) -> Iterator[Dict[str, str]]:
    """Yield rows where the given column (or any column) is not empty."""
    for row in rows:
        if column:
            if row.get(column, "").strip():
                yield row
        else:
            if any(v.strip() for v in row.values()):
                yield row
