"""Unit tests for csv_surgeon.impute."""
from __future__ import annotations

from typing import List, Dict

import pytest

from csv_surgeon.impute import impute_constant, impute_mean, impute_median, impute_mode


def _rows() -> List[Dict[str, str]]:
    return [
        {"name": "Alice", "score": "10"},
        {"name": "Bob", "score": ""},
        {"name": "Carol", "score": "20"},
        {"name": "Dave", "score": ""},
        {"name": "Eve", "score": "30"},
    ]


def test_impute_constant_fills_empty():
    result = list(impute_constant(_rows(), "score", "0"))
    assert result[1]["score"] == "0"
    assert result[3]["score"] == "0"


def test_impute_constant_leaves_non_empty_unchanged():
    result = list(impute_constant(_rows(), "score", "0"))
    assert result[0]["score"] == "10"
    assert result[2]["score"] == "20"


def test_impute_constant_unknown_column_passthrough():
    result = list(impute_constant(_rows(), "missing", "x"))
    assert [r["score"] for r in result] == ["10", "", "20", "", "30"]


def test_impute_mean_fills_empty():
    result = list(impute_mean(_rows(), "score"))
    # mean of 10, 20, 30 = 20.0
    assert result[1]["score"] == "20.0"
    assert result[3]["score"] == "20.0"


def test_impute_mean_does_not_change_non_empty():
    result = list(impute_mean(_rows(), "score"))
    assert result[0]["score"] == "10"


def test_impute_mean_out_column():
    result = list(impute_mean(_rows(), "score", out_column="score_imputed"))
    assert "score_imputed" in result[0]
    assert result[1]["score_imputed"] == "20.0"
    assert result[0]["score_imputed"] == "10"  # non-empty copied


def test_impute_median_fills_empty():
    result = list(impute_median(_rows(), "score"))
    assert result[1]["score"] == "20"
    assert result[3]["score"] == "20"


def test_impute_median_all_empty_fills_empty_string():
    rows = [{"x": ""}, {"x": ""}]
    result = list(impute_median(rows, "x"))
    assert result[0]["x"] == ""


def test_impute_mode_fills_empty():
    rows = [
        {"cat": "A"},
        {"cat": ""},
        {"cat": "A"},
        {"cat": "B"},
        {"cat": ""},
    ]
    result = list(impute_mode(rows, "cat"))
    assert result[1]["cat"] == "A"
    assert result[4]["cat"] == "A"


def test_impute_mode_out_column():
    rows = [{"cat": "A"}, {"cat": ""}]
    result = list(impute_mode(rows, "cat", out_column="cat_filled"))
    assert result[1]["cat_filled"] == "A"
    assert result[0]["cat_filled"] == "A"  # non-empty copied


def test_impute_mode_all_empty_fills_empty_string():
    rows = [{"x": ""}, {"x": ""}]
    result = list(impute_mode(rows, "x"))
    assert result[0]["x"] == ""
