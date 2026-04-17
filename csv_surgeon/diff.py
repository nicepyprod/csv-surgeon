"""Row-level diff between two CSV streams."""
from typing import Iterator, Dict, List, Optional, Tuple

Row = Dict[str, str]


def _key(row: Row, key_cols: List[str]) -> Tuple:
    return tuple(row.get(c, "") for c in key_cols)


def diff_rows(
    left: Iterator[Row],
    right: Iterator[Row],
    key_cols: List[str],
) -> Iterator[Row]:
    """Yield rows with a '_diff' column: 'added', 'removed', or 'modified'."""
    left_index: Dict[Tuple, Row] = {_key(r, key_cols): r for r in left}
    right_index: Dict[Tuple, Row] = {_key(r, key_cols): r for r in right}

    all_keys = set(left_index) | set(right_index)
    for k in sorted(all_keys, key=lambda t: t):
        in_left = k in left_index
        in_right = k in right_index
        if in_left and not in_right:
            yield {**left_index[k], "_diff": "removed"}
        elif in_right and not in_left:
            yield {**right_index[k], "_diff": "added"}
        else:
            l, r = left_index[k], right_index[k]
            if l != r:
                yield {**r, "_diff": "modified"}


def diff_summary(
    left: Iterator[Row],
    right: Iterator[Row],
    key_cols: List[str],
) -> Dict[str, int]:
    """Return counts of added, removed, modified, and unchanged rows."""
    left_index = {_key(r, key_cols): r for r in left}
    right_index = {_key(r, key_cols): r for r in right}
    counts = {"added": 0, "removed": 0, "modified": 0, "unchanged": 0}
    all_keys = set(left_index) | set(right_index)
    for k in all_keys:
        in_left = k in left_index
        in_right = k in right_index
        if in_left and not in_right:
            counts["removed"] += 1
        elif in_right and not in_left:
            counts["added"] += 1
        elif left_index[k] != right_index[k]:
            counts["modified"] += 1
        else:
            counts["unchanged"] += 1
    return counts
