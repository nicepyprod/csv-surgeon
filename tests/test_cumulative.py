"""Tests for csv_surgeon.cumulative."""
import pytest
from csv_surgeon.cumulative import (
    cumulative_sum,
    cumulative_mean,
    cumulative_max,
    cumulative_min,
)


def _rows():
    return [
        {"name": "a", "val": "3"},
        {"name": "b", "val": "1"},
        {"name": "c", "val": "4"},
        {"name": "d", "val": ""},
        {"name": "e", "val": "2"},
    ]


def test_cumulative_sum_basic():
    result = list(cumulative_sum(iter(_rows()), "val"))
    assert [r["val_cumsum"] for r in result] == ["3.0", "4.0", "8.0", "", "10.0"]


def test_cumulative_sum_custom_out_column():
    result = list(cumulative_sum(iter(_rows()), "val", out_column="running"))
    assert "running" in result[0]
    assert result[2]["running"] == "8.0"


def test_cumulative_sum_preserves_other_columns():
    result = list(cumulative_sum(iter(_rows()), "val"))
    assert result[0]["name"] == "a"
    assert result[3]["name"] == "d"


def test_cumulative_mean_basic():
    result = list(cumulative_mean(iter(_rows()), "val"))
    assert result[0]["val_cummean"] == "3.0"
    assert result[1]["val_cummean"] == "2.0"   # (3+1)/2
    assert result[2]["val_cummean"] == pytest.approx(str(8 / 3))
    assert result[3]["val_cummean"] == ""       # empty value, count unchanged
    assert result[4]["val_cummean"] == "2.5"    # (3+1+4+2)/4


def test_cumulative_mean_all_empty():
    rows = [{"v": ""}, {"v": ""}]
    result = list(cumulative_mean(iter(rows), "v"))
    assert all(r["v_cummean"] == "" for r in result)


def test_cumulative_max_basic():
    result = list(cumulative_max(iter(_rows()), "val"))
    assert [r["val_cummax"] for r in result] == ["3.0", "3.0", "4.0", "", "4.0"]


def test_cumulative_max_empty_start():
    rows = [{"v": ""}, {"v": "5"}, {"v": "3"}]
    result = list(cumulative_max(iter(rows), "v"))
    assert result[0]["v_cummax"] == ""
    assert result[1]["v_cummax"] == "5.0"
    assert result[2]["v_cummax"] == "5.0"


def test_cumulative_min_basic():
    result = list(cumulative_min(iter(_rows()), "val"))
    assert [r["val_cummin"] for r in result] == ["3.0", "1.0", "1.0", "", "1.0"]


def test_cumulative_min_custom_out_column():
    result = list(cumulative_min(iter(_rows()), "val", out_column="low"))
    assert result[1]["low"] == "1.0"


def test_cumulative_does_not_mutate_input():
    rows = [{"val": "5"}, {"val": "2"}]
    original = [dict(r) for r in rows]
    list(cumulative_sum(iter(rows), "val"))
    assert rows == original
