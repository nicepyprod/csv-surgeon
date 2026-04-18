"""Tests for csv_surgeon.regex_replace."""
import re
import pytest
from csv_surgeon.regex_replace import (
    regex_replace_column,
    regex_replace_columns,
    regex_extract_column,
)


def _rows():
    return [
        {"name": "Alice Smith", "email": "alice@example.com", "note": "hello world"},
        {"name": "Bob Jones",  "email": "bob@example.com",   "note": "foo bar"},
        {"name": "Carol",      "email": "carol@example.com", "note": ""},
    ]


def test_replace_column_basic():
    result = list(regex_replace_column(_rows(), "note", r"\s+", "_"))
    assert result[0]["note"] == "hello_world"
    assert result[1]["note"] == "foo_bar"
    assert result[2]["note"] == ""


def test_replace_column_case_insensitive():
    result = list(
        regex_replace_column(_rows(), "name", r"alice", "Alicia", flags=re.IGNORECASE)
    )
    assert result[0]["name"] == "Alicia Smith"
    assert result[1]["name"] == "Bob Jones"  # unchanged


def test_replace_column_unknown_column_passthrough():
    rows = list(regex_replace_column(_rows(), "missing", r"x", "y"))
    assert rows == _rows()


def test_replace_columns_multiple():
    result = list(
        regex_replace_columns(_rows(), ["name", "note"], r"\s+", "-")
    )
    assert result[0]["name"] == "Alice-Smith"
    assert result[0]["note"] == "hello-world"
    assert result[0]["email"] == "alice@example.com"  # untouched


def test_replace_columns_partial_missing():
    """Columns not present in a row are silently skipped."""
    rows = [{"name": "Alice Smith"}]  # no 'note'
    result = list(regex_replace_columns(rows, ["name", "note"], r" ", "_"))
    assert result[0]["name"] == "Alice_Smith"
    assert "note" not in result[0]


def test_extract_column_basic():
    result = list(
        regex_extract_column(_rows(), "email", r"@(\w+)\.com", "domain", group=1)
    )
    assert result[0]["domain"] == "example"
    assert result[1]["domain"] == "example"


def test_extract_column_no_match_empty_string():
    result = list(
        regex_extract_column(_rows(), "note", r"\d+", "digits")
    )
    assert result[0]["digits"] == ""
    assert result[2]["digits"] == ""


def test_extract_column_full_match_group0():
    result = list(
        regex_extract_column(_rows(), "email", r"\w+@\w+\.com", "full_email", group=0)
    )
    assert result[0]["full_email"] == "alice@example.com"
