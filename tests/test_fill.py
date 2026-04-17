"""Tests for csv_surgeon.fill."""
import pytest
from csv_surgeon.fill import fill_value, fill_forward, fill_backward, fill_mean


def _rows():
    return [
        {"name": "Alice", "score": "90"},
        {"name": "", "score": "85"},
        {"name": "Bob", "score": ""},
        {"name": "", "score": ""},
        {"name": "Carol", "score": "70"},
    ]


def test_fill_value_replaces_empty():
    result = list(fill_value(_rows(), "name", "UNKNOWN"))
    assert result[1]["name"] == "UNKNOWN"
    assert result[3]["name"] == "UNKNOWN"
    assert result[0]["name"] == "Alice"


def test_fill_value_leaves_nonempty_unchanged():
    result = list(fill_value(_rows(), "score", "0"))
    assert result[0]["score"] == "90"
    assert result[2]["score"] == "0"


def test_fill_value_unknown_column_passthrough():
    result = list(fill_value(_rows(), "nonexistent", "X"))
    assert result == _rows()


def test_fill_forward_basic():
    result = list(fill_forward(_rows(), "name"))
    assert result[1]["name"] == "Alice"
    assert result[3]["name"] == "Bob"


def test_fill_forward_leading_empty_stays_empty():
    rows = [{"v": ""}, {"v": "A"}, {"v": ""}]
    result = list(fill_forward(rows, "v"))
    assert result[0]["v"] == ""
    assert result[2]["v"] == "A"


def test_fill_backward_basic():
    result = list(fill_backward(_rows(), "score"))
    assert result[2]["score"] == "70"
    assert result[3]["score"] == "70"


def test_fill_backward_trailing_empty_stays_empty():
    rows = [{"v": "A"}, {"v": ""}, {"v": ""}]
    result = list(fill_backward(rows, "v"))
    assert result[1]["v"] == ""
    assert result[2]["v"] == ""


def test_fill_mean_basic():
    result = list(fill_mean(_rows(), "score"))
    # non-empty scores: 90, 85, 70 -> mean = 81.6667
    filled = result[2]["score"]
    assert abs(float(filled) - 81.6667) < 0.01


def test_fill_mean_all_empty_stays_empty():
    rows = [{"v": ""}, {"v": ""}]
    result = list(fill_mean(rows, "v"))
    assert result[0]["v"] == ""
    assert result[1]["v"] == ""
