"""Rolling/window aggregations over CSV rows."""
from collections import deque
from typing import Callable, Dict, Generator, Iterable, List, Optional


def _numeric(val: str) -> Optional[float]:
    try:
        return float(val)
    except (ValueError, TypeError):
        return None


def rolling_mean(
    rows: Iterable[Dict[str, str]],
    column: str,
    window: int,
    out_column: str = "",
) -> Generator[Dict[str, str], None, None]:
    """Append a rolling mean of *column* over *window* rows."""
    if not out_column:
        out_column = f"{column}_rolling_mean_{window}"
    buf: deque = deque(maxlen=window)
    for row in rows:
        val = _numeric(row.get(column, ""))
        if val is not None:
            buf.append(val)
        result = str(round(sum(buf) / len(buf), 6)) if buf else ""
        yield {**row, out_column: result}


def rolling_sum(
    rows: Iterable[Dict[str, str]],
    column: str,
    window: int,
    out_column: str = "",
) -> Generator[Dict[str, str], None, None]:
    """Append a rolling sum of *column* over *window* rows."""
    if not out_column:
        out_column = f"{column}_rolling_sum_{window}"
    buf: deque = deque(maxlen=window)
    for row in rows:
        val = _numeric(row.get(column, ""))
        if val is not None:
            buf.append(val)
        result = str(round(sum(buf), 6)) if buf else ""
        yield {**row, out_column: result}


def rolling_apply(
    rows: Iterable[Dict[str, str]],
    column: str,
    window: int,
    func: Callable[[List[float]], float],
    out_column: str = "result",
) -> Generator[Dict[str, str], None, None]:
    """Apply an arbitrary function over a rolling window of numeric values."""
    buf: deque = deque(maxlen=window)
    for row in rows:
        val = _numeric(row.get(column, ""))
        if val is not None:
            buf.append(val)
        result = str(round(func(list(buf)), 6)) if buf else ""
        yield {**row, out_column: result}
