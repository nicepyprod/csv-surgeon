"""Tests for csv_surgeon.rename."""
import pytest
from csv_surgeon.rename import rename_headers, reorder_columns, select_columns, drop_columns


@pytest.fixture
def _rows():
    return [
        {"id": "1", "name": "Alice", "age": "30"},
        {"id": "2", "name": "Bob", "age": "25"},
        {"id": "3", "name": "Carol", "age": "40"},
    ]


def test_rename_headers_basic(_rows):
    result = list(rename_headers(iter(_rows), {"name": "full_name"}))
    assert result[0] == {"id": "1", "full_name": "Alice", "age": "30"}


def test_rename_headers_multiple(_rows):
    result = list(rename_headers(iter(_rows), {"id": "uid", "age": "years"}))
    assert list(result[0].keys()) == ["uid", "full_name" if "full_name" in result[0] else "name", "years"]
    assert result[1]["uid"] == "2"
    assert result[1]["years"] == "25"


def test_rename_headers_unknown_key_unchanged(_rows):
    result = list(rename_headers(iter(_rows), {"missing": "x"}))
    assert result[0] == _rows[0]


def test_reorder_columns(_rows):
    result = list(reorder_columns(iter(_rows), ["name", "id"]))
    assert list(result[0].keys()) == ["name", "id"]
    assert result[0]["name"] == "Alice"


def test_reorder_columns_missing_filled(_rows):
    result = list(reorder_columns(iter(_rows), ["name", "country"], fill="N/A"))
    assert result[0]["country"] == "N/A"


def test_select_columns(_rows):
    result = list(select_columns(iter(_rows), ["id", "name"]))
    assert list(result[0].keys()) == ["id", "name"]
    assert "age" not in result[0]


def test_select_columns_skips_missing(_rows):
    result = list(select_columns(iter(_rows), ["id", "ghost"]))
    assert list(result[0].keys()) == ["id"]


def test_drop_columns(_rows):
    result = list(drop_columns(iter(_rows), ["age"]))
    assert "age" not in result[0]
    assert "id" in result[0]
    assert "name" in result[0]


def test_drop_columns_multiple(_rows):
    result = list(drop_columns(iter(_rows), ["id", "age"]))
    assert list(result[0].keys()) == ["name"]
