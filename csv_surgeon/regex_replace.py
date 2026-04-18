"""regex_replace: apply regex substitutions to CSV columns."""
from __future__ import annotations

import re
from typing import Dict, Iterable, Iterator, List


def regex_replace_column(
    rows: Iterable[Dict[str, str]],
    column: str,
    pattern: str,
    replacement: str,
    flags: int = 0,
) -> Iterator[Dict[str, str]]:
    """Replace occurrences of *pattern* in *column* with *replacement*.

    Rows where *column* is absent are passed through unchanged.
    """
    compiled = re.compile(pattern, flags)
    for row in rows:
        if column in row:
            row = {**row, column: compiled.sub(replacement, row[column])}
        yield row


def regex_replace_columns(
    rows: Iterable[Dict[str, str]],
    columns: List[str],
    pattern: str,
    replacement: str,
    flags: int = 0,
) -> Iterator[Dict[str, str]]:
    """Apply the same regex substitution across multiple *columns*."""
    compiled = re.compile(pattern, flags)
    for row in rows:
        new_row = dict(row)
        for col in columns:
            if col in new_row:
                new_row[col] = compiled.sub(replacement, new_row[col])
        yield new_row


def regex_extract_column(
    rows: Iterable[Dict[str, str]],
    column: str,
    pattern: str,
    out_column: str,
    group: int = 0,
    flags: int = 0,
) -> Iterator[Dict[str, str]]:
    """Extract the first match of *pattern* from *column* into *out_column*.

    If there is no match the *out_column* value is set to an empty string.
    """
    compiled = re.compile(pattern, flags)
    for row in rows:
        value = row.get(column, "")
        m = compiled.search(value)
        extracted = m.group(group) if m else ""
        yield {**row, out_column: extracted}
