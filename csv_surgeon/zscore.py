"""Z-score normalization and outlier flagging for numeric columns."""
from __future__ import annotations
import math
from typing import Iterable, Iterator


def _stats(values: list[float]) -> tuple[float, float]:
    n = len(values)
    if n == 0:
        return 0.0, 0.0
    mean = sum(values) / n
    variance = sum((v - mean) ** 2 for v in values) / n
    return mean, math.sqrt(variance)


def zscore_column(
    rows: Iterable[dict],
    column: str,
    out_column: str | None = None,
    round_digits: int = 4,
) -> list[dict]:
    """Add a z-score column for *column*. Consumes the iterable into memory."""
    out = out_column or f"{column}_zscore"
    data = list(rows)
    numeric: list[float] = []
    for row in data:
        try:
            numeric.append(float(row[column]))
        except (ValueError, KeyError):
            numeric.append(float("nan"))

    clean = [v for v in numeric if not math.isnan(v)]
    mean, std = _stats(clean)

    result = []
    for row, raw in zip(data, numeric):
        new = dict(row)
        if math.isnan(raw) or std == 0.0:
            new[out] = ""
        else:
            new[out] = str(round((raw - mean) / std, round_digits))
        result.append(new)
    return result


def flag_outliers(
    rows: Iterable[dict],
    column: str,
    threshold: float = 3.0,
    out_column: str | None = None,
) -> Iterator[dict]:
    """Yield rows with a boolean outlier flag based on z-score threshold."""
    out = out_column or f"{column}_outlier"
    scored = zscore_column(rows, column)
    for row in scored:
        new = dict(row)
        zscore_col = f"{column}_zscore"
        try:
            z = float(new[zscore_col])
            new[out] = "true" if abs(z) >= threshold else "false"
        except (ValueError, KeyError):
            new[out] = ""
        yield new
