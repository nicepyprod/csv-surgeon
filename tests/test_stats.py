"""Tests for csv_surgeon.stats."""
import pytest
from csv_surgeon.stats import column_stats, multi_column_stats


def _rows():
    return [
        {"name": "alice", "score": "90", "age": "30"},
        {"name": "bob",   "score": "80", "age": ""},
        {"name": "carol", "score": "70", "age": "25"},
        {"name": "dave",  "score": "",   "age": "40"},
        {"name": "eve",   "score": "100","age": "35"},
    ]


def test_column_stats_basic():
    s = column_stats(_rows(), "score")
    assert s["total"] == 5
    assert s["count"] == 4
    assert s["null_count"] == 1
    assert s["min"] == 70.0
    assert s["max"] == 100.0
    assert s["mean"] == pytest.approx(85.0)


def test_column_stats_stddev():
    s = column_stats(_rows(), "score")
    assert s["stddev"] is not None
    assert s["stddev"] > 0


def test_column_stats_all_null():
    rows = [{"x": ""}, {"x": "abc"}, {"x": ""}]
    s = column_stats(rows, "x")
    assert s["count"] == 0
    assert s["mean"] is None
    assert s["stddev"] is None


def test_column_stats_missing_column():
    rows = [{"a": "1"}, {"a": "2"}]
    s = column_stats(rows, "z")
    assert s["count"] == 0
    assert s["null_count"] == 2


def test_multi_column_stats_returns_all():
    results = multi_column_stats(_rows(), ["score", "age"])
    assert len(results) == 2
    cols = {r["column"] for r in results}
    assert cols == {"score", "age"}


def test_multi_column_stats_values():
    results = multi_column_stats(_rows(), ["score", "age"])
    age = next(r for r in results if r["column"] == "age")
    assert age["count"] == 4
    assert age["null_count"] == 1
    assert age["min"] == 25.0
    assert age["max"] == 40.0


def test_multi_column_stats_single_value():
    rows = [{"v": "42"}]
    results = multi_column_stats(rows, ["v"])
    assert results[0]["mean"] == pytest.approx(42.0)
    assert results[0]["stddev"] == pytest.approx(0.0)
