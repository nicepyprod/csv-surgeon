"""Streaming CSV writer utilities for in-place and temp-file-based edits."""

import csv
import os
import tempfile
from pathlib import Path
from typing import Callable, Iterable


def write_rows(
    filepath: str | Path,
    rows: Iterable[list[str]],
    delimiter: str = ",",
    encoding: str = "utf-8",
) -> None:
    """Write rows to a CSV file, overwriting any existing content.

    Args:
        filepath: Destination path.
        rows: Iterable of rows (lists of strings).
        delimiter: Field delimiter character.
        encoding: File encoding.
    """
    filepath = Path(filepath)
    with filepath.open("w", newline="", encoding=encoding) as fh:
        writer = csv.writer(fh, delimiter=delimiter)
        writer.writerows(rows)


def transform_inplace(
    filepath: str | Path,
    transform: Callable[[list[str]], list[str] | None],
    delimiter: str = ",",
    encoding: str = "utf-8",
) -> int:
    """Apply a transform function to each row and write results back in-place.

    Uses a temporary file to avoid data loss on failure.

    Args:
        filepath: Path to the CSV file to transform.
        transform: Callable that receives a row and returns a transformed row,
                   or None to drop the row.
        delimiter: Field delimiter character.
        encoding: File encoding.

    Returns:
        Number of rows written (excluding dropped rows).
    """
    filepath = Path(filepath)
    dir_ = filepath.parent
    written = 0

    with tempfile.NamedTemporaryFile(
        mode="w",
        newline="",
        encoding=encoding,
        dir=dir_,
        delete=False,
        suffix=".tmp",
    ) as tmp:
        tmp_path = tmp.name
        writer = csv.writer(tmp, delimiter=delimiter)
        try:
            with filepath.open(newline="", encoding=encoding) as src:
                reader = csv.reader(src, delimiter=delimiter)
                for row in reader:
                    result = transform(row)
                    if result is not None:
                        writer.writerow(result)
                        written += 1
        except Exception:
            os.unlink(tmp_path)
            raise

    os.replace(tmp_path, filepath)
    return written
