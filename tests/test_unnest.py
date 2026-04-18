"""Tests for csv_surgeon.unnest."""
import pytest
from csv_surgeon.unnest import unnest_column, nest_column


def _rows():
    return [
        {"id": "1", "name": "Alice", "tags": "python|csv|cli"},
        {"id": "2", "name": "Bob",   "tags": "java"},
        {"id": "3", "name": "Carol", "tags": ""},
        {"id": "4", "name": "Dave",  "tags": "go | rust"},
    ]


def test_unnest_basic():
    result = list(unnest_column(iter(_rows()), "tags"))
    assert len(result) == 6  # 3 + 1 + 1 (empty passthrough) + 2
    tag_values = [r["tags"] for r in result]
    assert "python" in tag_values
    assert "csv" in tag_values
    assert "cli" in tag_values
    assert "java" in tag_values


def test_unnest_empty_passthrough():
    result = list(unnest_column(iter(_rows()), "tags"))
    carol_rows = [r for r in result if r["name"] == "Carol"]
    assert len(carol_rows) == 1
    assert carol_rows[0]["tags"] == ""


def test_unnest_strips_whitespace():
    result = list(unnest_column(iter(_rows()), "tags"))
    dave_rows = [r for r in result if r["name"] == "Dave"]
    assert len(dave_rows) == 2
    assert dave_rows[0]["tags"] == "go"
    assert dave_rows[1]["tags"] == "rust"


def test_unnest_missing_column_passthrough():
    rows = [{"id": "1", "name": "Alice"}]
    result = list(unnest_column(iter(rows), "tags"))
    assert result == rows


def test_unnest_custom_sep():
    rows = [{"id": "1", "vals": "a,b,c"}]
    result = list(unnest_column(iter(rows), "vals", sep=","))
    assert [r["vals"] for r in result] == ["a", "b", "c"]


def test_nest_column_basic():
    unnested = [
        {"id": "1", "name": "Alice", "tag": "python"},
        {"id": "1", "name": "Alice", "tag": "csv"},
        {"id": "2", "name": "Bob",   "tag": "java"},
    ]
    result = list(nest_column(iter(unnested), column="tag", group_by="id"))
    assert len(result) == 2
    alice = next(r for r in result if r["id"] == "1")
    assert alice["tag"] == "python|csv"


def test_nest_column_single_value():
    unnested = [{"id": "2", "name": "Bob", "tag": "java"}]
    result = list(nest_column(iter(unnested), column="tag", group_by="id"))
    assert result[0]["tag"] == "java"


def test_nest_roundtrip():
    original = [{"id": "1", "name": "Alice", "tags": "python|csv|cli"}]
    unnested = list(unnest_column(iter(original), "tags"))
    renested = list(nest_column(iter(unnested), column="tags", group_by="id"))
    assert renested[0]["tags"] == "python|csv|cli"
