"""Column type casting utilities."""
from __future__ import annotations
from typing import Iterable, Iterator, Dict, Callable, Any


_CASTERS: Dict[str, Callable[[str], Any]] = {
    "int": int,
    "float": float,
    "str": str,
    "bool": lambda v: v.strip().lower() in ("1", "true", "yes"),
}


def _cast(value: str, typename: str) -> str:
    """Cast *value* to *typename* and return its string representation."""
    if typename not in _CASTERS:
        raise ValueError(f"Unknown type '{typename}'. Choose from: {list(_CASTERS)}")
    if value == "":
        return value
    return str(_CASTERS[typename](value))


def cast_columns(
    rows: Iterable[Dict[str, str]],
    casts: Dict[str, str],
    errors: str = "raise",
) -> Iterator[Dict[str, str]]:
    """Yield rows with specified columns cast to target types.

    Args:
        rows:   Iterable of header-keyed dicts.
        casts:  Mapping of column name -> type name (int/float/str/bool).
        errors: 'raise' to propagate errors, 'ignore' to leave value unchanged,
                'null' to replace bad values with empty string.
    """
    if errors not in ("raise", "ignore", "null"):
        raise ValueError("errors must be 'raise', 'ignore', or 'null'")

    for row in rows:
        out = dict(row)
        for col, typename in casts.items():
            if col not in out:
                continue
            try:
                out[col] = _cast(out[col], typename)
            except (ValueError, TypeError):
                if errors == "raise":
                    raise
                elif errors == "null":
                    out[col] = ""
                # else 'ignore': leave original value
        yield out
