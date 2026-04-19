"""Tests for csv_surgeon.clip."""
import pytest
from csv_surgeon.clip import clip_column, clip_columns


def _rows():
    return [
        {"name": "a", "score": "5"},
        {"name": "b", "score": "-3"},
        {"name": "c", "score": "150"},
        {"name": "d", "score": ""},
        {"name": "e", "score": "50"},
    ]


def test_clip_lower_bound():
    result = list(clip_column(_rows(), "score", lower=0))
    assert result[0]["score"] == "5"
    assert result[1]["score"] == "0"
    assert result[2]["score"] == "150"


def test_clip_upper_bound():
    result = list(clip_column(_rows(), "score", upper=100))
    assert result[2]["score"] == "100"
    assert result[4]["score"] == "50"


def test_clip_both_bounds():
    result = list(clip_column(_rows(), "score", lower=0, upper=100))
    assert result[1]["score"] == "0"
    assert result[2]["score"] == "100"
    assert result[0]["score"] == "5"


def test_clip_empty_value_passthrough():
    result = list(clip_column(_rows(), "score", lower=0, upper=100))
    assert result[3]["score"] == ""


def test_clip_out_column():
    result = list(clip_column(_rows(), "score", lower=0, upper=100, out_column="clipped"))
    assert result[1]["clipped"] == "0"
    assert result[1]["score"] == "-3"  # original unchanged


def test_clip_unknown_column_passthrough():
    rows = [{"a": "1"}]
    result = list(clip_column(rows, "missing", lower=0, upper=10))
    assert result[0] == {"a": "1"}


def test_clip_columns_multiple():
    rows = [
        {"x": "-5", "y": "200"},
        {"x": "50", "y": "50"},
    ]
    result = list(clip_columns(rows, {"x": (0, 100), "y": (0, 100)}))
    assert result[0]["x"] == "0"
    assert result[0]["y"] == "100"
    assert result[1]["x"] == "50"
    assert result[1]["y"] == "50"


def test_clip_preserves_other_columns():
    result = list(clip_column(_rows(), "score", lower=0, upper=100))
    assert result[0]["name"] == "a"
