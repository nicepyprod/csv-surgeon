"""Row-value shifting: lag and lead operations on a column."""
from typing import Iterator, Dict, List, Optional
from collections import deque


def lag_column(
    rows: Iterator[Dict[str, str]],
    column: str,
    periods: int = 1,
    out_column: Optional[str] = None,
    fill: str = "",
) -> Iterator[Dict[str, str]]:
    """Add a column containing the value of *column* from *periods* rows ago."""
    if periods < 1:
        raise ValueError("periods must be >= 1")
    out = out_column or f"{column}_lag{periods}"
    buf: deque = deque()
    for row in rows:
        buf.append(row.get(column, ""))
        lagged = buf[0] if len(buf) > periods else fill
        if len(buf) > periods:
            buf.popleft()
        yield {**row, out: lagged}


def lead_column(
    rows: Iterator[Dict[str, str]],
    column: str,
    periods: int = 1,
    out_column: Optional[str] = None,
    fill: str = "",
) -> Iterator[Dict[str, str]]:
    """Add a column containing the value of *column* from *periods* rows ahead."""
    if periods < 1:
        raise ValueError("periods must be >= 1")
    out = out_column or f"{column}_lead{periods}"
    buf: deque = deque()
    pending: List[Dict[str, str]] = []

    for row in rows:
        buf.append(row.get(column, ""))
        pending.append(row)
        if len(buf) > periods:
            lead_val = buf[periods] if len(buf) > periods else fill
            yield {**pending[0], out: buf[periods]}
            pending.pop(0)
            buf.popleft()

    # flush remaining rows with fill
    for row in pending:
        yield {**row, out: fill}
