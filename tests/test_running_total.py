"""Tests for csv_surgeon.running_total."""
from __future__ import annotations

from typing import List, Dict

import pytest

from csv_surgeon.running_total import running_total_column, running_total_columns


def _rows() -> List[Dict[str, str]]:
    return [
        {"dept": "A", "sales": "10"},
        {"dept": "A", "sales": "20"},
        {"dept": "B", "sales": "5"},
        {"dept": "A", "sales": "30"},
        {"dept": "B", "sales": "15"},
    ]


def test_running_total_no_group():
    result = list(running_total_column(_rows(), "sales"))
    totals = [r["sales_running_total"] for r in result]
    assert totals == ["10.0", "30.0", "35.0", "65.0", "80.0"]


def test_running_total_with_group():
    result = list(running_total_column(_rows(), "sales", group_col="dept"))
    a_totals = [r["sales_running_total"] for r in result if r["dept"] == "A"]
    b_totals = [r["sales_running_total"] for r in result if r["dept"] == "B"]
    assert a_totals == ["10.0", "30.0", "60.0"]
    assert b_totals == ["5.0", "20.0"]


def test_running_total_custom_out_col():
    result = list(running_total_column(_rows(), "sales", out_col="cum_sales"))
    assert "cum_sales" in result[0]
    assert "sales_running_total" not in result[0]


def test_running_total_empty_value_resets():
    rows = [
        {"v": "10"},
        {"v": ""},
        {"v": "5"},
    ]
    result = list(running_total_column(rows, "v", reset_on_empty=True))
    assert result[0]["v_running_total"] == "10.0"
    assert result[1]["v_running_total"] == ""
    assert result[2]["v_running_total"] == "5.0"  # reset after empty


def test_running_total_empty_value_no_reset():
    rows = [
        {"v": "10"},
        {"v": ""},
        {"v": "5"},
    ]
    result = list(running_total_column(rows, "v", reset_on_empty=False))
    assert result[0]["v_running_total"] == "10.0"
    assert result[1]["v_running_total"] == ""
    assert result[2]["v_running_total"] == "15.0"  # continues from 10


def test_running_total_missing_column_yields_empty():
    rows = [{"a": "1"}, {"a": "2"}]
    result = list(running_total_column(rows, "nonexistent"))
    assert all(r["nonexistent_running_total"] == "" for r in result)


def test_running_total_does_not_mutate_original():
    rows = [{"v": "1"}, {"v": "2"}]
    originals = [dict(r) for r in rows]
    list(running_total_column(rows, "v"))
    assert rows == originals


def test_running_total_columns_multi_spec():
    rows = [
        {"a": "1", "b": "10"},
        {"a": "2", "b": "20"},
        {"a": "3", "b": "30"},
    ]
    specs = [
        {"value_col": "a", "out_col": "a_rt"},
        {"value_col": "b", "out_col": "b_rt"},
    ]
    result = list(running_total_columns(rows, specs))
    assert result[-1]["a_rt"] == "6.0"
    assert result[-1]["b_rt"] == "60.0"
