"""Tests for csv_surgeon.levenshtein."""
import pytest
from csv_surgeon.levenshtein import (
    _levenshtein,
    fuzzy_match_column,
    add_distance_column,
    cluster_near_duplicates,
)


def _rows():
    return [
        {"name": "Alice", "score": "90"},
        {"name": "Alise", "score": "85"},
        {"name": "Bob", "score": "70"},
        {"name": "Bobby", "score": "72"},
        {"name": "Charlie", "score": "60"},
    ]


def test_levenshtein_identical():
    assert _levenshtein("abc", "abc") == 0


def test_levenshtein_insertion():
    assert _levenshtein("ab", "abc") == 1


def test_levenshtein_deletion():
    assert _levenshtein("abc", "ab") == 1


def test_levenshtein_substitution():
    assert _levenshtein("abc", "axc") == 1


def test_levenshtein_empty():
    assert _levenshtein("", "abc") == 3
    assert _levenshtein("abc", "") == 3


def test_fuzzy_match_column_basic():
    result = list(fuzzy_match_column(iter(_rows()), "name", "Alice", max_distance=1))
    names = [r["name"] for r in result]
    assert "Alice" in names
    assert "Alise" in names
    assert "Bob" not in names


def test_fuzzy_match_column_case_insensitive():
    result = list(fuzzy_match_column(iter(_rows()), "name", "alice", max_distance=0))
    assert any(r["name"] == "Alice" for r in result)


def test_fuzzy_match_column_case_sensitive_no_match():
    result = list(fuzzy_match_column(iter(_rows()), "name", "alice",
                                      max_distance=0, case_sensitive=True))
    assert result == []


def test_add_distance_column_default_name():
    result = list(add_distance_column(iter(_rows()), "name", "Alice"))
    assert "name_dist" in result[0]
    assert result[0]["name_dist"] == "0"   # Alice vs Alice
    assert result[1]["name_dist"] == "1"   # Alise vs Alice


def test_add_distance_column_custom_name():
    result = list(add_distance_column(iter(_rows()), "name", "Bob", out_column="dist"))
    assert "dist" in result[0]


def test_cluster_near_duplicates_basic():
    clusters = cluster_near_duplicates(_rows(), "name", max_distance=1)
    # Alice + Alise should cluster; Bob + Bobby may not (distance=2)
    sizes = sorted(len(c) for c in clusters)
    assert max(sizes) >= 2


def test_cluster_near_duplicates_zero_distance():
    clusters = cluster_near_duplicates(_rows(), "name", max_distance=0)
    # each name is unique -> 5 clusters
    assert len(clusters) == 5
