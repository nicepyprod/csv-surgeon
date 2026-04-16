"""Column renaming and reordering utilities."""
from typing import Iterator, Dict, List, Optional


def rename_headers(
    rows: Iterator[Dict[str, str]],
    mapping: Dict[str, str],
) -> Iterator[Dict[str, str]]:
    """Yield rows with columns renamed according to mapping."""
    for row in rows:
        yield {mapping.get(k, k): v for k, v in row.items()}


def reorder_columns(
    rows: Iterator[Dict[str, str]],
    order: List[str],
    fill: str = "",
) -> Iterator[Dict[str, str]]:
    """Yield rows with keys in the given order.

    Columns not in *order* are dropped; missing columns are filled with *fill*.
    """
    for row in rows:
        yield {col: row.get(col, fill) for col in order}


def select_columns(
    rows: Iterator[Dict[str, str]],
    columns: List[str],
) -> Iterator[Dict[str, str]]:
    """Yield rows containing only the specified columns."""
    for row in rows:
        yield {col: row[col] for col in columns if col in row}


def drop_columns(
    rows: Iterator[Dict[str, str]],
    columns: List[str],
) -> Iterator[Dict[str, str]]:
    """Yield rows with specified columns removed."""
    drop = set(columns)
    for row in rows:
        yield {k: v for k, v in row.items() if k not in drop}
