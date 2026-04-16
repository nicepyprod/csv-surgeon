"""Join two CSV streams on a common key column."""
from typing import Iterator, Dict, List, Optional


def _index(rows: Iterator[Dict], key: str) -> Dict[str, List[Dict]]:
    """Load right-side rows into a dict keyed by join column."""
    idx: Dict[str, List[Dict]] = {}
    for row in rows:
        k = row.get(key, "")
        idx.setdefault(k, []).append(row)
    return idx


def inner_join(
    left: Iterator[Dict],
    right: Iterator[Dict],
    left_key: str,
    right_key: Optional[str] = None,
) -> Iterator[Dict]:
    """Yield merged rows where key matches in both sides."""
    rk = right_key or left_key
    idx = _index(right, rk)
    for lrow in left:
        k = lrow.get(left_key, "")
        for rrow in idx.get(k, []):
            merged = {**rrow, **lrow}
            yield merged


def left_join(
    left: Iterator[Dict],
    right: Iterator[Dict],
    left_key: str,
    right_key: Optional[str] = None,
) -> Iterator[Dict]:
    """Yield all left rows; merge matching right rows or leave blanks."""
    rk = right_key or left_key
    idx = _index(right, rk)
    for lrow in left:
        k = lrow.get(left_key, "")
        matches = idx.get(k, [{}])
        for rrow in matches:
            merged = {**rrow, **lrow}
            yield merged
