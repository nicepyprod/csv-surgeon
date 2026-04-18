"""Auto-detect and report column types from streamed rows."""
from __future__ import annotations
from typing import Iterator
import re

_INT_RE = re.compile(r'^-?\d+$')
_FLOAT_RE = re.compile(r'^-?\d+\.\d*$|^-?\.\d+$')
_BOOL_VALS = {'true', 'false', '1', '0', 'yes', 'no'}


def _detect(value: str) -> str:
    v = value.strip()
    if v == '':
        return 'empty'
    if _INT_RE.match(v):
        return 'int'
    if _FLOAT_RE.match(v):
        return 'float'
    if v.lower() in _BOOL_VALS:
        return 'bool'
    return 'str'


def detect_column_types(
    rows: Iterator[dict],
    sample: int = 500,
) -> dict[str, str]:
    """Sample up to *sample* rows and return inferred type per column."""
    counts: dict[str, dict[str, int]] = {}
    for i, row in enumerate(rows):
        if i >= sample:
            break
        for col, val in row.items():
            t = _detect(val)
            counts.setdefault(col, {})
            counts[col][t] = counts[col].get(t, 0) + 1

    result: dict[str, str] = {}
    for col, tally in counts.items():
        non_empty = {t: n for t, n in tally.items() if t != 'empty'}
        if not non_empty:
            result[col] = 'empty'
        else:
            result[col] = max(non_empty, key=non_empty.__getitem__)
    return result


def type_report(rows: Iterator[dict], sample: int = 500) -> list[dict]:
    """Return a list of dicts suitable for CSV output."""
    types = detect_column_types(rows, sample=sample)
    return [{'column': col, 'inferred_type': t} for col, t in types.items()]
