"""Tests for csv_surgeon.cast."""
import pytest
from csv_surgeon.cast import cast_columns, _cast


def _rows():
    return [
        {"id": "1", "price": "9.99", "active": "true", "name": "Alice"},
        {"id": "2", "price": "4.50", "active": "false", "name": "Bob"},
        {"id": "3", "price": "",     "active": "yes",   "name": "Carol"},
    ]


def test_cast_int():
    result = list(cast_columns(_rows(), {"id": "int"}))
    assert result[0]["id"] == "1"
    assert result[1]["id"] == "2"


def test_cast_float():
    result = list(cast_columns(_rows(), {"price": "float"}))
    assert result[0]["price"] == "9.99"
    assert result[1]["price"] == "4.5"


def test_cast_bool():
    result = list(cast_columns(_rows(), {"active": "bool"}))
    assert result[0]["active"] == "True"
    assert result[1]["active"] == "False"
    assert result[2]["active"] == "True"


def test_cast_empty_passthrough():
    result = list(cast_columns(_rows(), {"price": "float"}))
    assert result[2]["price"] == ""


def test_cast_unknown_column_passthrough():
    result = list(cast_columns(_rows(), {"nonexistent": "int"}))
    assert result[0] == _rows()[0]


def test_cast_unknown_type_raises():
    with pytest.raises(ValueError, match="Unknown type"):
        list(cast_columns(_rows(), {"id": "datetime"}))


def test_cast_bad_value_raises():
    rows = [{"id": "abc"}]
    with pytest.raises(ValueError):
        list(cast_columns(rows, {"id": "int"}, errors="raise"))


def test_cast_bad_value_ignore():
    rows = [{"id": "abc"}]
    result = list(cast_columns(rows, {"id": "int"}, errors="ignore"))
    assert result[0]["id"] == "abc"


def test_cast_bad_value_null():
    rows = [{"id": "abc"}]
    result = list(cast_columns(rows, {"id": "int"}, errors="null"))
    assert result[0]["id"] == ""


def test_cast_multiple_columns():
    result = list(cast_columns(_rows(), {"id": "int", "price": "float"}))
    assert result[0]["id"] == "1"
    assert result[0]["price"] == "9.99"
    assert result[0]["name"] == "Alice"
