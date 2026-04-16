"""Tests for csv_surgeon.filter module."""

import pytest

from csv_surgeon.filter import (
    filter_rows,
    filter_by_value,
    filter_by_contains,
    filter_columns,
    drop_empty,
)

ROWS = [
    {"name": "Alice", "city": "New York", "score": "90"},
    {"name": "Bob", "city": "Boston", "score": "75"},
    {"name": "Charlie", "city": "new york", "score": ""},
    {"name": "", "city": "Denver", "score": "88"},
]


def _rows():
    return iter(list(ROWS))


def test_filter_rows_predicate():
    result = list(filter_rows(_rows(), lambda r: int(r["score"]) > 80 if r["score"] else False))
    assert len(result) == 2
    assert result[0]["name"] == "Alice"


def test_filter_by_value_exact():
    result = list(filter_by_value(_rows(), "city", "New York"))
    assert len(result) == 1
    assert result[0]["name"] == "Alice"


def test_filter_by_value_case_insensitive():
    result = list(filter_by_value(_rows(), "city", "new york", case_sensitive=False))
    assert len(result) == 2


def test_filter_by_contains():
    result = list(filter_by_contains(_rows(), "city", "on"))
    assert len(result) == 1
    assert result[0]["name"] == "Bob"


def test_filter_by_contains_case_insensitive():
    result = list(filter_by_contains(_rows(), "city", "NEW", case_sensitive=False))
    assert len(result) == 2


def test_filter_columns():
    result = list(filter_columns(_rows(), ["name", "score"]))
    assert list(result[0].keys()) == ["name", "score"]
    assert "city" not in result[0]


def test_filter_columns_missing_column():
    result = list(filter_columns(_rows(), ["name", "nonexistent"]))
    assert "nonexistent" not in result[0]


def test_drop_empty_specific_column():
    result = list(drop_empty(_rows(), column="name"))
    assert all(r["name"].strip() for r in result)
    assert len(result) == 3


def test_drop_empty_any_column():
    result = list(drop_empty(_rows()))
    assert len(result) == 4  # all rows have at least one non-empty value


def test_drop_empty_score_column():
    result = list(drop_empty(_rows(), column="score"))
    assert len(result) == 3
    assert all(r["score"].strip() for r in result)
