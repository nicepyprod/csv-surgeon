"""Cross-join and semi-join utilities for CSV rows."""
from typing import Iterator, List, Dict, Optional


def cross_join(
    left: List[Dict[str, str]],
    right: List[Dict[str, str]],
    left_prefix: str = "l_",
    right_prefix: str = "r_",
) -> Iterator[Dict[str, str]]:
    """Yield the Cartesian product of left and right row lists."""
    for l_row in left:
        for r_row in right:
            merged: Dict[str, str] = {}
            for k, v in l_row.items():
                merged[left_prefix + k] = v
            for k, v in r_row.items():
                merged[right_prefix + k] = v
            yield merged


def semi_join(
    left: List[Dict[str, str]],
    right: List[Dict[str, str]],
    key: str,
    right_key: Optional[str] = None,
) -> Iterator[Dict[str, str]]:
    """Yield left rows whose key value exists in right (SQL semi-join)."""
    rk = right_key or key
    right_keys = {r[rk] for r in right if rk in r}
    for row in left:
        if row.get(key) in right_keys:
            yield row


def anti_join(
    left: List[Dict[str, str]],
    right: List[Dict[str, str]],
    key: str,
    right_key: Optional[str] = None,
) -> Iterator[Dict[str, str]]:
    """Yield left rows whose key value does NOT exist in right."""
    rk = right_key or key
    right_keys = {r[rk] for r in right if rk in r}
    for row in left:
        if row.get(key) not in right_keys:
            yield row
