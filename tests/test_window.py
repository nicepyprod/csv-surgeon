"""Tests for csv_surgeon.window."""
import pytest
from csv_surgeon.window import rolling_mean, rolling_sum, rolling_apply


def _rows():
    return [
        {"name": "a", "val": "10"},
        {"name": "b", "val": "20"},
        {"name": "c", "val": "30"},
        {"name": "d", "val": "40"},
        {"name": "e", "val": ""},
    ]


def test_rolling_mean_window2():
    out = list(rolling_mean(_rows(), "val", window=2, out_column="rm"))
    assert out[0]["rm"] == "10.0"
    assert out[1]["rm"] == "15.0"
    assert out[2]["rm"] == "25.0"
    assert out[3]["rm"] == "35.0"
    # empty val — buffer unchanged, mean still from last two numerics
    assert out[4]["rm"] == "35.0"


def test_rolling_mean_default_out_column():
    out = list(rolling_mean(_rows(), "val", window=3))
    assert "val_rolling_mean_3" in out[0]


def test_rolling_sum_window2():
    out = list(rolling_sum(_rows(), "val", window=2, out_column="rs"))
    assert out[0]["rs"] == "10.0"
    assert out[1]["rs"] == "30.0"
    assert out[2]["rs"] == "50.0"
    assert out[3]["rs"] == "70.0"


def test_rolling_sum_default_out_column():
    out = list(rolling_sum(_rows(), "val", window=2))
    assert "val_rolling_sum_2" in out[0]


def test_rolling_apply_custom_func():
    out = list(rolling_apply(_rows()[:4], "val", window=2, func=max, out_column="rmax"))
    assert out[0]["rmax"] == "10.0"
    assert out[1]["rmax"] == "20.0"
    assert out[2]["rmax"] == "30.0"
    assert out[3]["rmax"] == "40.0"


def test_rolling_mean_preserves_other_columns():
    out = list(rolling_mean(_rows(), "val", window=2, out_column="rm"))
    assert out[0]["name"] == "a"
    assert out[2]["name"] == "c"


def test_rolling_mean_empty_input():
    out = list(rolling_mean([], "val", window=3, out_column="rm"))
    assert out == []
