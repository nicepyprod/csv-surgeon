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
    """Replace values in *column* using a lookup *mapping*.

    If a value is not found in *mapping* and *default* is empty, the original
    cell value is preserved.  Supply an explicit *default* to override unmapped
    values with a fixed string instead.
    """
    for row in rows:
        out = dict(row)
        out[column] = mapping.get(out.get(column, ""), default or out.get(column, ""))
        yield out


def case_when(
    rows: Iterable[Dict[str, str]],
    cases: List[tuple[Callable[[Dict[str, str]], bool], str]],
    column: str,
    default: str = "",
) -> Iterator[Dict[str, str]]:
    """Set *column* by evaluating a list of (predicate, value) pairs in order.

    The first predicate that returns ``True`` determines the value written to
    *column*.  If no predicate matches, *default* is used.

    Args:
        rows: Iterable of row dicts.
        cases: Ordered list of ``(predicate, value)`` pairs.
        column: Name of the column to set.
        default: Value to use when no predicate matches.
    """
    for row in rows:
        out = dict(row)
        out[column] = next(
            (value for predicate, value in cases if predicate(out)),
            default,
        )
        yield out
