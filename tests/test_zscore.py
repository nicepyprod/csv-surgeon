"""Tests for csv_surgeon.zscore."""
import math
import pytest
from csv_surgeon.zscore import zscore_column, flag_outliers


def _rows():
    return [
        {"name": "a", "val": "10"},
        {"name": "b", "val": "20"},
        {"name": "c", "val": "30"},
        {"name": "d", "val": "40"},
        {"name": "e", "val": "50"},
    ]


def test_zscore_column_adds_output_column():
    result = zscore_column(_rows(), "val")
    assert all("val_zscore" in r for r in result)


def test_zscore_column_custom_out():
    result = zscore_column(_rows(), "val", out_column="z")
    assert all("z" in r for r in result)


def test_zscore_middle_value_is_zero():
    result = zscore_column(_rows(), "val")
    # median row (val=30) should have z-score 0
    mid = next(r for r in result if r["val"] == "30")
    assert float(mid["val_zscore"]) == pytest.approx(0.0)


def test_zscore_symmetric():
    result = zscore_column(_rows(), "val")
    z_a = float(next(r for r in result if r["val"] == "10")["val_zscore"])
    z_e = float(next(r for r in result if r["val"] == "50")["val_zscore"])
    assert z_a == pytest.approx(-z_e)


def test_zscore_empty_string_for_non_numeric():
    rows = [{"val": "abc"}, {"val": "2"}, {"val": "3"}]
    result = zscore_column(rows, "val")
    assert result[0]["val_zscore"] == ""


def test_zscore_constant_column_yields_empty():
    rows = [{"val": "5"}, {"val": "5"}, {"val": "5"}]
    result = zscore_column(rows, "val")
    assert all(r["val_zscore"] == "" for r in result)


def test_flag_outliers_marks_extreme():
    rows = [
        {"val": "10"}, {"val": "10"}, {"val": "10"},
        {"val": "10"}, {"val": "1000"},
    ]
    result = list(flag_outliers(rows, "val", threshold=2.0))
    flags = [r["val_outlier"] for r in result]
    assert flags[-1] == "true"
    assert all(f == "false" for f in flags[:-1])


def test_flag_outliers_custom_threshold():
    result = list(flag_outliers(_rows(), "val", threshold=0.1))
    # with low threshold most should be outliers
    outliers = [r for r in result if r["val_outlier"] == "true"]
    assert len(outliers) >= 2


def test_flag_outliers_preserves_original_columns():
    result = list(flag_outliers(_rows(), "val"))
    assert all("name" in r and "val" in r for r in result)
