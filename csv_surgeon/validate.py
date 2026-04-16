"""Row-level validation helpers for csv-surgeon."""
from __future__ import annotations

from typing import Callable, Dict, Iterable, Iterator, List, Optional, Tuple


ValidationRule = Callable[[str], bool]


def _cast_numeric(value: str) -> bool:
    try:
        float(value)
        return True
    except ValueError:
        return False


def validate_rows(
    rows: Iterable[Dict[str, str]],
    rules: Dict[str, List[ValidationRule]],
    *,
    skip_invalid: bool = False,
) -> Iterator[Dict[str, str]]:
    """Yield rows that pass all rules; optionally skip invalid ones."""
    for row in rows:
        errors = _check(row, rules)
        if not errors:
            yield row
        elif not skip_invalid:
            cols = ", ".join(f"{c}: {e}" for c, e in errors)
            raise ValueError(f"Validation failed — {cols}")


def _check(
    row: Dict[str, str], rules: Dict[str, List[ValidationRule]]
) -> List[Tuple[str, str]]:
    errors: List[Tuple[str, str]] = []
    for col, col_rules in rules.items():
        value = row.get(col, "")
        for rule in col_rules:
            if not rule(value):
                errors.append((col, f"rule '{rule.__name__}' failed on '{value}'"))
    return errors


def is_numeric(value: str) -> bool:
    """Rule: value must be numeric."""
    return _cast_numeric(value)


is_numeric.__name__ = "is_numeric"


def not_empty(value: str) -> bool:
    """Rule: value must not be empty or whitespace."""
    return bool(value.strip())


not_empty.__name__ = "not_empty"


def max_length(n: int) -> ValidationRule:
    """Rule factory: value length must not exceed *n*."""
    def _rule(value: str) -> bool:
        return len(value) <= n
    _rule.__name__ = f"max_length({n})"
    return _rule


def one_of(*choices: str, case_sensitive: bool = True) -> ValidationRule:
    """Rule factory: value must be one of the given choices."""
    allowed = set(choices) if case_sensitive else {c.lower() for c in choices}

    def _rule(value: str) -> bool:
        v = value if case_sensitive else value.lower()
        return v in allowed

    _rule.__name__ = f"one_of({', '.join(choices)})"
    return _rule
