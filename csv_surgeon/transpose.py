"""Transpose and pivot-style row/column flipping utilities."""
from typing import Iterator, List, Dict


def transpose_rows(
    rows: List[Dict[str, str]],
    header: List[str],
    index_col: str = "column",
    value_col_prefix: str = "row",
) -> Iterator[Dict[str, str]]:
    """Transpose a list of row dicts so columns become rows.

    Each output row represents one original column.  The values for that
    column across every input row become ``row0``, ``row1``, … fields.

    Args:
        rows: Materialised list of input row dicts.
        header: Ordered list of column names (defines output row order).
        index_col: Name of the output column that holds the original column name.
        value_col_prefix: Prefix for the synthetic per-row value columns.

    Yields:
        One dict per original column.
    """
    for col in header:
        out: Dict[str, str] = {index_col: col}
        for i, row in enumerate(rows):
            out[f"{value_col_prefix}{i}"] = row.get(col, "")
        yield out


def transposed_header(
    n_rows: int,
    index_col: str = "column",
    value_col_prefix: str = "row",
) -> List[str]:
    """Return the header list that matches :func:`transpose_rows` output.

    Args:
        n_rows: Number of original data rows (determines how many value columns).
        index_col: Same value passed to :func:`transpose_rows`.
        value_col_prefix: Same value passed to :func:`transpose_rows`.

    Returns:
        List of column name strings.
    """
    return [index_col] + [f"{value_col_prefix}{i}" for i in range(n_rows)]
