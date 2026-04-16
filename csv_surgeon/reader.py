"""Streaming CSV reader that yields rows without loading the full file."""

import csv
from pathlib import Path
from typing import Generator, Optional


def stream_rows(
    filepath: str | Path,
    delimiter: str = ",",
    encoding: str = "utf-8",
    skip_header: bool = False,
) -> Generator[list[str], None, None]:
    """Yield rows from a CSV file one at a time.

    Args:
        filepath: Path to the CSV file.
        delimiter: Field delimiter character.
        encoding: File encoding.
        skip_header: If True, skip the first row.

    Yields:
        Each row as a list of strings.
    """
    filepath = Path(filepath)
    if not filepath.exists():
        raise FileNotFoundError(f"CSV file not found: {filepath}")

    with filepath.open(newline="", encoding=encoding) as fh:
        reader = csv.reader(fh, delimiter=delimiter)
        if skip_header:
            next(reader, None)
        for row in reader:
            yield row


def read_header(
    filepath: str | Path,
    delimiter: str = ",",
    encoding: str = "utf-8",
) -> Optional[list[str]]:
    """Return only the header row of a CSV file.

    Args:
        filepath: Path to the CSV file.
        delimiter: Field delimiter character.
        encoding: File encoding.

    Returns:
        The header row as a list of strings, or None if the file is empty.
    """
    filepath = Path(filepath)
    if not filepath.exists():
        raise FileNotFoundError(f"CSV file not found: {filepath}")

    with filepath.open(newline="", encoding=encoding) as fh:
        reader = csv.reader(fh, delimiter=delimiter)
        return next(reader, None)
