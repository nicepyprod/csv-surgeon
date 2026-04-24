"""expression.py – evaluate arithmetic / string expressions per row.

Allows adding a derived column whose value is computed from an expression
string referencing other column names as variables, e.g.::

    total = price * quantity
    label = first_name + " " + last_name
    margin = (revenue - cost) / revenue * 100

Column names are injected into a restricted ``eval`` namespace so that only
safe built-ins are available (no imports, no builtins that touch the OS).
"""

from __future__ import annotations

import math
import re
from typing import Dict, Iterable, Iterator, List, Optional

# ---------------------------------------------------------------------------
# Safe eval helpers
# ---------------------------------------------------------------------------

_SAFE_GLOBALS: dict = {
    "__builtins__": {},
    # math functions commonly useful in CSV expressions
    "abs": abs,
    "round": round,
    "min": min,
    "max": max,
    "int": int,
    "float": float,
    "str": str,
    "len": len,
    "sqrt": math.sqrt,
    "log": math.log,
    "log10": math.log10,
    "ceil": math.ceil,
    "floor": math.floor,
    "pi": math.pi,
    "e": math.e,
}


def _safe_eval(expr: str, local_vars: dict):
    """Evaluate *expr* with *local_vars* injected; raises ValueError on error."""
    try:
        return eval(expr, _SAFE_GLOBALS, local_vars)  # noqa: S307
    except Exception as exc:
        raise ValueError(f"Expression evaluation failed: {exc!r}") from exc


def _coerce(value: str):
    """Try to coerce a CSV string value to int or float; fall back to str."""
    try:
        return int(value)
    except (ValueError, TypeError):
        pass
    try:
        return float(value)
    except (ValueError, TypeError):
        pass
    return value


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def add_expression_column(
    rows: Iterable[Dict[str, str]],
    expression: str,
    out_column: str,
    *,
    coerce: bool = True,
    on_error: str = "",
) -> Iterator[Dict[str, str]]:
    """Yield rows with a new *out_column* computed from *expression*.

    Parameters
    ----------
    rows:
        Iterable of ``{header: value}`` dicts.
    expression:
        Python expression string.  Column names are available as variables.
        Values are auto-coerced to ``int``/``float`` when possible unless
        *coerce* is ``False``.
    out_column:
        Name of the new (or overwritten) column.
    coerce:
        If ``True`` (default), attempt numeric coercion of column values
        before evaluation so that arithmetic works without explicit casts.
    on_error:
        Value to write when evaluation raises an exception.  Defaults to
        empty string; set to e.g. ``"ERROR"`` for visibility.
    """
    for row in rows:
        local_vars = (
            {k: _coerce(v) for k, v in row.items()}
            if coerce
            else dict(row)
        )
        try:
            result = _safe_eval(expression, local_vars)
        except ValueError:
            result = on_error
        out = dict(row)
        out[out_column] = str(result)
        yield out


def multi_expression(
    rows: Iterable[Dict[str, str]],
    expressions: List[tuple],  # list of (out_column, expression_str)
    *,
    coerce: bool = True,
    on_error: str = "",
) -> Iterator[Dict[str, str]]:
    """Apply multiple expressions in sequence, each seeing previous results.

    Parameters
    ----------
    expressions:
        Ordered list of ``(out_column, expression)`` pairs.  Later
        expressions can reference columns produced by earlier ones.
    """
    for row in rows:
        current = dict(row)
        for out_column, expr in expressions:
            local_vars = (
                {k: _coerce(v) for k, v in current.items()}
                if coerce
                else dict(current)
            )
            try:
                result = _safe_eval(expr, local_vars)
            except ValueError:
                result = on_error
            current[out_column] = str(result)
        yield current
