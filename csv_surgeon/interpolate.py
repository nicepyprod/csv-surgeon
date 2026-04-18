"""Linear and constant interpolation for missing values in numeric columns."""
from __future__ import annotations
from typing import Iterator, Iterable


def _to_float(v: str):
    try:
        return float(v)
    except (ValueError, TypeError):
        return None


def interpolate_linear(rows: Iterable[dict], column: str) -> list[dict]:
    """Fill empty cells in *column* using linear interpolation between neighbours."""
    data = list(rows)
    if not data or column not in data[0]:
        return data

    values = [_to_float(r[column]) for r in data]

    # find runs of None and interpolate
    n = len(values)
    i = 0
    while i < n:
        if values[i] is None:
            # find start of gap
            left_idx = i - 1
            j = i
            while j < n and values[j] is None:
                j += 1
            right_idx = j  # first non-None after gap

            if left_idx >= 0 and right_idx < n:
                left_val = values[left_idx]
                right_val = values[right_idx]
                span = right_idx - left_idx
                for k in range(i, j):
                    frac = (k - left_idx) / span
                    values[k] = left_val + frac * (right_val - left_val)
            elif left_idx < 0 and right_idx < n:
                for k in range(i, j):
                    values[k] = values[right_idx]
            elif left_idx >= 0 and right_idx >= n:
                for k in range(i, j):
                    values[k] = values[left_idx]
            i = j
        else:
            i += 1

    result = []
    for row, val in zip(data, values):
        r = dict(row)
        if val is not None:
            r[column] = str(round(val, 10)).rstrip('0').rstrip('.')
        result.append(r)
    return result


def interpolate_constant(rows: Iterable[dict], column: str, fill: str = "0") -> Iterator[dict]:
    """Replace empty cells in *column* with a constant *fill* value."""
    for row in rows:
        r = dict(row)
        if column in r and r[column].strip() == "":
            r[column] = fill
        yield r


def interpolate_columns(rows: Iterable[dict], columns: list[str], method: str = "linear", fill: str = "0") -> list[dict]:
    """Apply interpolation over multiple columns sequentially."""
    data = list(rows)
    for col in columns:
        if method == "linear":
            data = interpolate_linear(data, col)
        else:
            data = list(interpolate_constant(data, col, fill))
    return data
