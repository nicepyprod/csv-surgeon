"""Tests for csv_surgeon.sort."""
import pytest
from csv_surgeon.sort import sort_rows, sort_rows_multi


def _rows():
    return [
        {"name": "Charlie", "age": "30", "city": "Berlin"},
        {"name": "Alice",   "age": "25", "city": "Amsterdam"},
        {"name": "Bob",     "age": "35", "city": "Berlin"},
        {"name": "Diana",   "age": "25", "city": "Cairo"},
    ]


def test_sort_rows_alpha_asc():
    result = list(sort_rows(_rows(), key="name"))
    assert [r["name"] for r in result] == ["Alice", "Bob", "Charlie", "Diana"]


def test_sort_rows_alpha_desc():
    result = list(sort_rows(_rows(), key="name", reverse=True))
    assert result[0]["name"] == "Diana"


def test_sort_rows_numeric():
    result = list(sort_rows(_rows(), key="age", numeric=True))
    assert [r["age"] for r in result] == ["25", "25", "30", "35"]


def test_sort_rows_numeric_desc():
    result = list(sort_rows(_rows(), key="age", numeric=True, reverse=True))
    assert result[0]["age"] == "35"


def test_sort_rows_missing_key():
    rows = [{"name": "X"}, {"name": "A", "age": "10"}]
    result = list(sort_rows(rows, key="age", numeric=True))
    assert result[0]["name"] == "X"  # missing -> 0.0, sorts first


def test_sort_rows_multi_two_keys():
    result = list(sort_rows_multi(_rows(), keys=["age", "name"], numeric_keys=["age"]))
    ages = [r["age"] for r in result]
    assert ages == ["25", "25", "30", "35"]
    # within age=25, Alice before Diana
    assert result[0]["name"] == "Alice"
    assert result[1]["name"] == "Diana"


def test_sort_rows_multi_reverse():
    result = list(sort_rows_multi(_rows(), keys=["city", "name"], reverse=True))
    assert result[0]["city"] == "Cairo"
