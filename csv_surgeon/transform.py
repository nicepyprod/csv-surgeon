"""Column-level transform utilities for csv-surgeon."""
from typing import Callable, Dict, Iterable, Iterator, List


def apply_transforms(
    rows: Iterable[Dict[str, str]],
    transforms: Dict[str, Callable[[str], str]],
) -> Iterator[Dict[str, str]]:
    """Apply per-column transform functions to each row.

    Args:
        rows: Iterable of row dicts.
        transforms: Mapping of column name -> callable(value) -> value.

    Yields:
        Row dicts with transformed values.
    """
    for row in rows:
        new_row = dict(row)
        for col, fn in transforms.items():
            if col in new_row:
                new_row[col] = fn(new_row[col])
        yield new_row


def rename_columns(
    rows: Iterable[Dict[str, str]],
    mapping: Dict[str, str],
) -> Iterator[Dict[str, str]]:
    """Rename columns in each row.

    Args:
        rows: Iterable of row dicts.
        mapping: Old name -> new name.

    Yields:
        Row dicts with renamed keys.
    """
    for row in rows:
        yield {mapping.get(k, k): v for k, v in row.items()}


def add_column(
    rows: Iterable[Dict[str, str]],
    name: str,
    fn: Callable[[Dict[str, str]], str],
) -> Iterator[Dict[str, str]]:
    """Add a derived column to each row.

    Args:
        rows: Iterable of row dicts.
        name: New column name.
        fn: Callable that receives the row and returns the new column value.

    Yields:
        Row dicts with the new column appended.
    """
    for row in rows:
        new_row = dict(row)
        new_row[name] = fn(row)
        yield new_row


def strip_whitespace(rows: Iterable[Dict[str, str]]) -> Iterator[Dict[str, str]]:
    """Strip leading/trailing whitespace from all values."""
    for row in rows:
        yield {k: v.strip() for k, v in row.items()}
