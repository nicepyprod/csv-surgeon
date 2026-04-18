"""Column value normalization: strip, lowercase, uppercase, title, slug."""
from __future__ import annotations

import re
from typing import Callable, Dict, Iterable, Iterator


_NORMALIZERS: Dict[str, Callable[[str], str]] = {
    "lower": str.lower,
    "upper": str.upper,
    "title": str.title,
    "strip": str.strip,
    "slug": lambda v: re.sub(r"[^a-z0-9]+", "-", v.lower().strip()).strip("-"),
}


def _get(name: str) -> Callable[[str], str]:
    if name not in _NORMALIZERS:
        raise ValueError(f"Unknown normalizer '{name}'. Choose from: {list(_NORMALIZERS)}.")
    return _NORMALIZERS[name]


def normalize_column(
    rows: Iterable[Dict[str, str]],
    column: str,
    method: str = "strip",
) -> Iterator[Dict[str, str]]:
    """Apply a single normalization method to *column* in every row."""
    fn = _get(method)
    for row in rows:
        out = dict(row)
        if column in out:
            out[column] = fn(out[column])
        yield out


def normalize_columns(
    rows: Iterable[Dict[str, str]],
    column_methods: Dict[str, str],
) -> Iterator[Dict[str, str]]:
    """Apply per-column normalization methods.

    *column_methods* maps column name -> method name.
    """
    fns = {col: _get(m) for col, m in column_methods.items()}
    for row in rows:
        out = dict(row)
        for col, fn in fns.items():
            if col in out:
                out[col] = fn(out[col])
        yield out
