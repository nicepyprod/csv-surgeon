"""Tests for csv_surgeon.rolling_window."""
from __future__ import annotations

import pytest
from csv_surgeon.rolling_window import window_context, window_diff


def _rows():
    return [
        {"id": "1", "val": "10"},
        {"id": "2", "val": "20"},
        {"id": "3", "val": "30"},
        {"id": "4", "val": "40"},
    ]


def test_window_context_adds_prev_and_next_columns():
    result = list(window_context(_rows(), before=1, after=1))
    assert "prev_id" in result[1]
    assert "next_id" in result[1]


def test_window_context_first_row_prev_is_fill():
    result = list(window_context(_rows(), before=1, after=1, fill="N/A"))
    assert result[0]["prev_id"] == "N/A"
    assert result[0]["prev_val"] == "N/A"


def test_window_context_last_row_next_is_fill():
    result = list(window_context(_rows(), before=1, after=1, fill=""))
    assert result[-1]["next_id"] == ""


def test_window_context_middle_row_correct_values():
    result = list(window_context(_rows(), before=1, after=1))
    assert result[1]["prev_id"] == "1"
    assert result[1]["next_id"] == "3"


def test_window_context_before_zero():
    result = list(window_context(_rows(), before=0, after=1))
    assert "prev_id" not in result[1]
    assert "next_id" in result[1]


def test_window_context_multi_before_uses_numbered_prefix():
    result = list(window_context(_rows(), before=2, after=0))
    assert "prev_1_id" in result[2]
    assert "prev_2_id" in result[2]
    assert result[2]["prev_1_id"] == "2"
    assert result[2]["prev_2_id"] == "1"


def test_window_context_empty_input():
    result = list(window_context([], before=1, after=1))
    assert result == []


def test_window_context_negative_before_raises():
    with pytest.raises(ValueError):
        list(window_context(_rows(), before=-1, after=0))


def test_window_diff_basic():
    result = list(window_diff(_rows(), column="val"))
    assert result[0]["val_diff"] == ""
    assert result[1]["val_diff"] == "10.0"
    assert result[2]["val_diff"] == "10.0"


def test_window_diff_custom_out_column():
    result = list(window_diff(_rows(), column="val", out_column="delta"))
    assert "delta" in result[0]
    assert result[2]["delta"] == "10.0"


def test_window_diff_non_numeric_fills():
    rows = [{"x": "a"}, {"x": "b"}, {"x": "c"}]
    result = list(window_diff(rows, column="x", fill="?"))
    assert all(r["x_diff"] == "?" for r in result)


def test_window_diff_preserves_other_columns():
    result = list(window_diff(_rows(), column="val"))
    assert result[1]["id"] == "2"
