"""Tests for csv_surgeon.outlier."""
import pytest
from csv_surgeon.outlier import filter_outliers_iqr, flag_iqr_outliers, _iqr_bounds


def _rows():
    # values: 1,2,3,4,5,6,7,8,9,100  — 100 is a clear outlier
    return [
        {"id": str(i), "val": str(v)}
        for i, v in enumerate([1, 2, 3, 4, 5, 6, 7, 8, 9, 100])
    ]


def test_iqr_bounds_basic():
    lo, hi = _iqr_bounds([1, 2, 3, 4, 5, 6, 7, 8, 9, 100])
    assert lo < 1
    assert hi < 100


def test_filter_outliers_removes_outlier():
    result = list(filter_outliers_iqr(iter(_rows()), "val"))
    vals = [r["val"] for r in result]
    assert "100" not in vals
    assert "5" in vals


def test_filter_outliers_keep_mode():
    result = list(filter_outliers_iqr(iter(_rows()), "val", keep_outliers=True))
    vals = [r["val"] for r in result]
    assert vals == ["100"]


def test_filter_outliers_no_numeric_passthrough():
    rows = [{"id": "1", "val": "abc"}, {"id": "2", "val": "xyz"}]
    result = list(filter_outliers_iqr(iter(rows), "val"))
    assert len(result) == 2


def test_filter_outliers_unknown_column_passthrough():
    result = list(filter_outliers_iqr(iter(_rows()), "nonexistent"))
    assert len(result) == 10


def test_flag_iqr_outliers_adds_column():
    result = list(flag_iqr_outliers(iter(_rows()), "val"))
    assert "val_iqr_outlier" in result[0]


def test_flag_iqr_outliers_correct_flags():
    result = list(flag_iqr_outliers(iter(_rows()), "val"))
    flags = {r["val"]: r["val_iqr_outlier"] for r in result}
    assert flags["100"] == "1"
    assert flags["5"] == "0"


def test_flag_iqr_outliers_custom_out_column():
    result = list(flag_iqr_outliers(iter(_rows()), "val", out_column="is_out"))
    assert "is_out" in result[0]


def test_flag_iqr_outliers_custom_flags():
    result = list(
        flag_iqr_outliers(iter(_rows()), "val", flag_true="yes", flag_false="no")
    )
    flags = {r["val"]: r["val_iqr_outlier"] for r in result}
    assert flags["100"] == "yes"
    assert flags["1"] == "no"
