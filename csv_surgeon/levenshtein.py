"""Fuzzy string matching / deduplication via Levenshtein distance."""
from __future__ import annotations
from typing import Iterator, List, Dict, Optional


def _levenshtein(a: str, b: str) -> int:
    """Compute Levenshtein edit distance between two strings."""
    if a == b:
        return 0
    if not a:
        return len(b)
    if not b:
        return len(a)
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        curr = [i] + [0] * len(b)
        for j, cb in enumerate(b, 1):
            curr[j] = min(
                prev[j] + 1,
                curr[j - 1] + 1,
                prev[j - 1] + (0 if ca == cb else 1),
            )
        prev = curr
    return prev[len(b)]


def fuzzy_match_column(
    rows: Iterator[Dict[str, str]],
    column: str,
    target: str,
    max_distance: int = 2,
    case_sensitive: bool = False,
) -> Iterator[Dict[str, str]]:
    """Yield rows where *column* is within *max_distance* edits of *target*."""
    t = target if case_sensitive else target.lower()
    for row in rows:
        val = row.get(column, "")
        v = val if case_sensitive else val.lower()
        if _levenshtein(v, t) <= max_distance:
            yield row


def add_distance_column(
    rows: Iterator[Dict[str, str]],
    column: str,
    target: str,
    out_column: Optional[str] = None,
    case_sensitive: bool = False,
) -> Iterator[Dict[str, str]]:
    """Append edit-distance to *target* as a new column."""
    out = out_column or f"{column}_dist"
    t = target if case_sensitive else target.lower()
    for row in rows:
        val = row.get(column, "")
        v = val if case_sensitive else val.lower()
        yield {**row, out: str(_levenshtein(v, t))}


def cluster_near_duplicates(
    rows: List[Dict[str, str]],
    column: str,
    max_distance: int = 1,
    case_sensitive: bool = False,
) -> List[List[Dict[str, str]]]:
    """Group rows whose *column* values are within *max_distance* of each other.

    Returns a list of clusters (each cluster is a list of rows).
    Uses a greedy single-linkage approach.
    """
    def norm(s: str) -> str:
        return s if case_sensitive else s.lower()

    clusters: List[List[Dict[str, str]]] = []
    cluster_keys: List[str] = []

    for row in rows:
        val = norm(row.get(column, ""))
        placed = False
        for idx, key in enumerate(cluster_keys):
            if _levenshtein(val, key) <= max_distance:
                clusters[idx].append(row)
                placed = True
                break
        if not placed:
            clusters.append([row])
            cluster_keys.append(val)
    return clusters
