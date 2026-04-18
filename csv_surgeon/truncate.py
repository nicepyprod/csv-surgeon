"""Truncate string values in CSV columns to a maximum length."""
from typing import Iterator, Dict, List, Optional


def truncate_column(
    rows: Iterator[Dict[str, str]],
    column: str,
    max_length: int,
    suffix: str = "",
) -> Iterator[Dict[str, str]]:
    """Truncate values in *column* to *max_length* chars, appending *suffix* when trimmed."""
    if max_length < 0:
        raise ValueError("max_length must be >= 0")
    for row in rows:
        row = dict(row)
        if column in row:
            val = row[column]
            if len(val) > max_length:
                core = max_length - len(suffix)
                row[column] = val[:max(core, 0)] + suffix
        yield row


def truncate_columns(
    rows: Iterator[Dict[str, str]],
    columns: List[str],
    max_length: int,
    suffix: str = "",
) -> Iterator[Dict[str, str]]:
    """Apply truncation to multiple columns."""
    if max_length < 0:
        raise ValueError("max_length must be >= 0")
    for row in rows:
        row = dict(row)
        for col in columns:
            if col in row:
                val = row[col]
                if len(val) > max_length:
                    core = max_length - len(suffix)
                    row[col] = val[:max(core, 0)] + suffix
        yield row


def pad_column(
    rows: Iterator[Dict[str, str]],
    column: str,
    width: int,
    fillchar: str = " ",
    align: str = "left",
) -> Iterator[Dict[str, str]]:
    """Pad values in *column* to *width* using *fillchar*. align: left|right|center."""
    if len(fillchar) != 1:
        raise ValueError("fillchar must be a single character")
    if align not in ("left", "right", "center"):
        raise ValueError("align must be 'left', 'right', or 'center'")
    for row in rows:
        row = dict(row)
        if column in row:
            val = row[column]
            if align == "left":
                row[column] = val.ljust(width, fillchar)
            elif align == "right":
                row[column] = val.rjust(width, fillchar)
            else:
                row[column] = val.center(width, fillchar)
        yield row
