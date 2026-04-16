"""Tests for csv_surgeon.dedupe."""
import pytest
from csv_surgeon.dedupe import dedupe_rows, count_duplicates


def _rows():
    return [
        {"name": "Alice", "city": "NY"},
        {"name": "Bob",   "city": "LA"},
        {"name": "Alice", "city": "NY"},
        {"name": "Bob",   "city": "SF"},
        {"name": "Alice", "city": "NY"},
    ]


def test_dedupe_keep_first_all_columns():
    result = list(dedupe_rows(_rows()))
    assert result == [
        {"name": "Alice", "city": "NY"},
        {"name": "Bob",   "city": "LA"},
        {"name": "Bob",   "city": "SF"},
    ]


def test_dedupe_keep_last_all_columns():
    result = list(dedupe_rows(_rows(), keep="last"))
    assert result == [
        {"name": "Alice", "city": "NY"},
        {"name": "Bob",   "city": "LA"},
        {"name": "Bob",   "city": "SF"},
    ]


def test_dedupe_keep_first_by_key():
    result = list(dedupe_rows(_rows(), keys=["name"]))
    assert result == [
        {"name": "Alice", "city": "NY"},
        {"name": "Bob",   "city": "LA"},
    ]


def test_dedupe_keep_last_by_key():
    result = list(dedupe_rows(_rows(), keys=["name"], keep="last"))
    assert result == [
        {"name": "Alice", "city": "NY"},
        {"name": "Bob",   "city": "SF"},
    ]


def test_dedupe_no_duplicates():
    rows = [{"id": "1"}, {"id": "2"}, {"id": "3"}]
    assert list(dedupe_rows(rows)) == rows


def test_dedupe_invalid_keep():
    with pytest.raises(ValueError):
        list(dedupe_rows(_rows(), keep="middle"))


def test_count_duplicates_all_columns():
    assert count_duplicates(_rows()) == 2


def test_count_duplicates_by_key():
    assert count_duplicates(_rows(), keys=["name"]) == 3


def test_count_duplicates_none():
    rows = [{"id": "1"}, {"id": "2"}]
    assert count_duplicates(rows) == 0
