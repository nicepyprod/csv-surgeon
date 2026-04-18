"""Conditional column assignment based on predicates."""
from __future__ import annotations
from typing import Callable, Dict, Iterable, Iterator, List


def if_then(
    rows: Iterable[Dict[str, str]],
    predicate: Callable[[Dict[str, str]], bool],
    column: str,
    true_value: str,
    false_value: str = "",
) -> Iterator[Dict[str, str]]:
    """Set *column* to *true_value* when predicate holds, else *false_value*."""
    for row in rows:
        out = dict(row)
        out[column] = true_value if predicate(out) else false_value
        yield out


def if_then_else_column(
    rows: Iterable[Dict[str, str]],
    condition_col: str,
    condition_value: str,
    target_col: str,
    true_value: str,
    false_value: str = "",
    case_sensitive: bool = True,
) -> Iterator[Dict[str, str]]:
    """Set *target_col* based on whether *condition_col* equals *condition_value*."""
    for row in rows:
        out = dict(row)
        cell = out.get(condition_col, "")
        if not case_sensitive:
            match = cell.lower() == condition_value.lower()
        else:
            match = cell == condition_value
        out[target_col] = true_value if match else false_value
        yield out


def coalesce(
    rows: Iterable[Dict[str, str]],
    columns: List[str],
    output_col: str,
) -> Iterator[Dict[str, str]]:
    """Set *output_col* to the first non-empty value among *columns*."""
    for row in rows:
        out = dict(row)
        out[output_col] = next((out.get(c, "") for c in columns if out.get(c, "")), "")
        yield out


def map_values(
    rows: Iterable[Dict[str, str]],
    column: str,
    mapping: Dict[str, str],
    default: str = "",
) -> Iterator[Dict[str, str]]:
    """Replace values in *column* using a lookup *mapping*."""
    for row in rows:
        out = dict(row)
        out[column] = mapping.get(out.get(column, ""), default or out.get(column, ""))
        yield out
