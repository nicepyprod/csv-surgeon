"""Split CSV rows into multiple output files based on a column value."""
from __future__ import annotations

import csv
import io
from collections import defaultdict
from typing import Dict, Iterable, Iterator, List, Optional


def split_rows(
    rows: Iterable[dict],
    column: str,
    *,
    max_groups: Optional[int] = None,
) -> Dict[str, List[dict]]:
    """Partition rows into groups keyed by *column* value.

    Args:
        rows: Iterable of header-keyed dicts.
        column: Column whose value determines the group.
        max_groups: If set, raise ValueError when exceeded.

    Returns:
        Ordered dict mapping group key -> list of rows.
    """
    groups: Dict[str, List[dict]] = defaultdict(list)
    for row in rows:
        key = row.get(column, "")
        groups[key].append(row)
        if max_groups is not None and len(groups) > max_groups:
            raise ValueError(
                f"Number of distinct values in '{column}' exceeds max_groups={max_groups}"
            )
    return dict(groups)


def split_to_buffers(
    rows: Iterable[dict],
    column: str,
    fieldnames: List[str],
) -> Dict[str, io.StringIO]:
    """Like split_rows but returns a StringIO CSV buffer per group."""
    groups = split_rows(rows, column)
    buffers: Dict[str, io.StringIO] = {}
    for key, group_rows in groups.items():
        buf = io.StringIO()
        writer = csv.DictWriter(buf, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(group_rows)
        buf.seek(0)
        buffers[key] = buf
    return buffers


def split_evenly(
    rows: Iterable[dict],
    chunk_size: int,
) -> Iterator[List[dict]]:
    """Yield successive chunks of *chunk_size* rows."""
    if chunk_size < 1:
        raise ValueError("chunk_size must be >= 1")
    chunk: List[dict] = []
    for row in rows:
        chunk.append(row)
        if len(chunk) == chunk_size:
            yield chunk
            chunk = []
    if chunk:
        yield chunk
