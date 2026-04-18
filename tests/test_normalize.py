"""Tests for csv_surgeon.normalize."""
import pytest
from csv_surgeon.normalize import normalize_column, normalize_columns


def _rows():
    return [
        {"name": "  Alice ", "city": "NEW YORK", "tag": "Hello World"},
        {"name": "BOB", "city": "los angeles", "tag": "foo  bar"},
        {"name": "charlie", "city": "Chicago", "tag": "Baz-Qux"},
    ]


def test_normalize_column_strip():
    result = list(normalize_column(_rows(), "name", "strip"))
    assert result[0]["name"] == "Alice"
    assert result[1]["name"] == "BOB"  # no change needed


def test_normalize_column_lower():
    result = list(normalize_column(_rows(), "city", "lower"))
    assert result[0]["city"] == "new york"
    assert result[1]["city"] == "los angeles"


def test_normalize_column_upper():
    result = list(normalize_column(_rows(), "city", "upper"))
    assert result[0]["city"] == "NEW YORK"
    assert result[2]["city"] == "CHICAGO"


def test_normalize_column_title():
    result = list(normalize_column(_rows(), "city", "title"))
    assert result[1]["city"] == "Los Angeles"


def test_normalize_column_slug():
    result = list(normalize_column(_rows(), "tag", "slug"))
    assert result[0]["tag"] == "hello-world"
    assert result[1]["tag"] == "foo-bar"
    assert result[2]["tag"] == "baz-qux"


def test_normalize_column_unknown_method():
    with pytest.raises(ValueError, match="Unknown normalizer"):
        list(normalize_column(_rows(), "name", "reverse"))


def test_normalize_column_missing_column_passthrough():
    result = list(normalize_column(_rows(), "nonexistent", "lower"))
    assert result[0] == _rows()[0]


def test_normalize_columns_multi():
    result = list(
        normalize_columns(_rows(), {"name": "strip", "city": "lower"})
    )
    assert result[0]["name"] == "Alice"
    assert result[0]["city"] == "new york"
    assert result[0]["tag"] == "Hello World"  # untouched


def test_normalize_columns_preserves_other_fields():
    result = list(normalize_columns(_rows(), {"tag": "slug"}))
    assert result[1]["name"] == "BOB"
    assert result[1]["city"] == "los angeles"
