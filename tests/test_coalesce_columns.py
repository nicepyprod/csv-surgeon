"""Tests for csv_surgeon.coalesce_columns."""
from __future__ import annotations

from typing import Dict, List

import pytest

from csv_surgeon.coalesce_columns import coalesce_columns, first_non_empty


def _rows() -> List[Dict[str, str]]:
    return [
        {"a": "alpha", "b": "",      "c": "gamma"},
        {"a": "",      "b": "beta",  "c": "gamma"},
        {"a": "",      "b": "",      "c": "gamma"},
        {"a": "",      "b": "",      "c": ""},
        {"a": "  ",    "b": "beta2", "c": ""},
    ]


def test_coalesce_picks_first_non_empty():
    result = list(coalesce_columns(_rows(), ["a", "b", "c"], out_column="val"))
    assert result[0]["val"] == "alpha"
    assert result[1]["val"] == "beta"
    assert result[2]["val"] == "gamma"


def test_coalesce_uses_default_when_all_empty():
    result = list(coalesce_columns(_rows(), ["a", "b", "c"], out_column="val", default="N/A"))
    assert result[3]["val"] == "N/A"


def test_coalesce_default_is_empty_string_by_default():
    result = list(coalesce_columns(_rows(), ["a", "b", "c"], out_column="val"))
    assert result[3]["val"] == ""


def test_coalesce_treats_whitespace_only_as_empty():
    # row index 4: a=" ", b="beta2" -> should pick b
    result = list(coalesce_columns(_rows(), ["a", "b", "c"], out_column="val"))
    assert result[4]["val"] == "beta2"


def test_coalesce_preserves_source_columns_by_default():
    result = list(coalesce_columns(_rows(), ["a", "b", "c"], out_column="val"))
    assert "a" in result[0]
    assert "b" in result[0]
    assert "c" in result[0]


def test_coalesce_remove_sources():
    result = list(
        coalesce_columns(_rows(), ["a", "b", "c"], out_column="val", remove_sources=True)
    )
    assert "a" not in result[0]
    assert "b" not in result[0]
    assert "c" not in result[0]
    assert result[0]["val"] == "alpha"


def test_coalesce_out_column_same_as_source_not_dropped():
    """When out_column matches a source column, it should not be removed."""
    result = list(
        coalesce_columns(_rows(), ["a", "b"], out_column="a", remove_sources=True)
    )
    assert "a" in result[0]
    assert "b" not in result[0]


def test_coalesce_missing_column_treated_as_empty():
    rows = [{"a": "", "b": "found"}]
    result = list(coalesce_columns(rows, ["missing", "b"], out_column="val"))
    assert result[0]["val"] == "found"


def test_first_non_empty_basic():
    values = list(first_non_empty(_rows(), ["a", "b", "c"]))
    assert values[0] == "alpha"
    assert values[1] == "beta"
    assert values[3] is None


def test_first_non_empty_all_empty_yields_none():
    rows = [{"x": "", "y": "  "}]
    values = list(first_non_empty(rows, ["x", "y"]))
    assert values[0] is None
