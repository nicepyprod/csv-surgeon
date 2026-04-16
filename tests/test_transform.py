"""Tests for csv_surgeon.transform module."""
import pytest
from csv_surgeon.transform import (
    add_column,
    apply_transforms,
    rename_columns,
    strip_whitespace,
)


def _rows():
    return [
        {"name": "alice", "age": "30", "city": "berlin"},
        {"name": "bob", "age": "25", "city": "paris"},
        {"name": "carol", "age": "40", "city": "rome"},
    ]


def test_apply_transforms_single_column():
    result = list(apply_transforms(_rows(), {"name": str.upper}))
    assert result[0]["name"] == "ALICE"
    assert result[1]["age"] == "25"  # untouched


def test_apply_transforms_multiple_columns():
    result = list(apply_transforms(_rows(), {"name": str.upper, "city": str.upper}))
    assert result[2]["name"] == "CAROL"
    assert result[2]["city"] == "ROME"


def test_apply_transforms_missing_column_ignored():
    result = list(apply_transforms(_rows(), {"nonexistent": str.upper}))
    assert result[0] == _rows()[0]


def test_apply_transforms_numeric_cast():
    result = list(apply_transforms(_rows(), {"age": lambda v: str(int(v) + 1)}))
    assert result[0]["age"] == "31"
    assert result[1]["age"] == "26"


def test_rename_columns_basic():
    result = list(rename_columns(_rows(), {"name": "full_name"}))
    assert "full_name" in result[0]
    assert "name" not in result[0]
    assert result[0]["full_name"] == "alice"


def test_rename_columns_no_match_passthrough():
    result = list(rename_columns(_rows(), {"unknown": "x"}))
    assert result[0] == _rows()[0]


def test_add_column_constant():
    result = list(add_column(_rows(), "country", lambda r: "DE"))
    assert result[0]["country"] == "DE"
    assert "country" in result[1]


def test_add_column_derived():
    result = list(add_column(_rows(), "label", lambda r: f"{r['name']}_{r['age']}"))
    assert result[0]["label"] == "alice_30"
    assert result[1]["label"] == "bob_25"


def test_strip_whitespace():
    dirty = [{"name": "  alice ", "age": " 30", "city": "berlin  "}]
    result = list(strip_whitespace(dirty))
    assert result[0]["name"] == "alice"
    assert result[0]["age"] == "30"
    assert result[0]["city"] == "berlin"
