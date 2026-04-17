"""Encoding / decoding helpers for CSV columns."""
from __future__ import annotations
import base64
from typing import Iterable, Iterator


def _b64_encode(value: str) -> str:
    return base64.b64encode(value.encode()).decode()


def _b64_decode(value: str) -> str:
    try:
        return base64.b64decode(value.encode()).decode()
    except Exception:
        return value


_ENCODERS = {
    "base64": _b64_encode,
    "upper": str.upper,
    "lower": str.lower,
    "strip": str.strip,
    "reverse": lambda s: s[::-1],
}

_DECODERS = {
    "base64": _b64_decode,
    "upper": str.lower,
    "lower": str.upper,
    "strip": str.strip,
    "reverse": lambda s: s[::-1],
}


def encode_columns(
    rows: Iterable[dict],
    columns: list[str],
    encoding: str = "base64",
) -> Iterator[dict]:
    """Apply *encoding* to each value in *columns*."""
    fn = _ENCODERS.get(encoding)
    if fn is None:
        raise ValueError(f"Unknown encoding '{encoding}'. Choose from: {list(_ENCODERS)}.")
    for row in rows:
        out = dict(row)
        for col in columns:
            if col in out and out[col] != "":
                out[col] = fn(out[col])
        yield out


def decode_columns(
    rows: Iterable[dict],
    columns: list[str],
    encoding: str = "base64",
) -> Iterator[dict]:
    """Reverse *encoding* for each value in *columns*."""
    fn = _DECODERS.get(encoding)
    if fn is None:
        raise ValueError(f"Unknown encoding '{encoding}'. Choose from: {list(_DECODERS)}.")
    for row in rows:
        out = dict(row)
        for col in columns:
            if col in out and out[col] != "":
                out[col] = fn(out[col])
        yield out
