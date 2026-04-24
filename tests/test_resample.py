"""Tests for csv_surgeon.resample."""
import pytest
from csv_surgeon.resample import resample_rows, _aggregate


def _rows():
    return [
        {"date": "2024-01-05", "sales": "10"},
        {"date": "2024-01-20", "sales": "20"},
        {"date": "2024-02-03", "sales": "15"},
        {"date": "2024-02-14", "sales": "5"},
        {"date": "2024-03-01", "sales": "30"},
    ]


def test_resample_count_by_month():
    result = list(resample_rows(_rows(), date_col="date", period="month", agg_func="count"))
    assert len(result) == 3
    assert result[0] == {"date": "2024-01", "value": "2"}
    assert result[1] == {"date": "2024-02", "value": "2"}
    assert result[2] == {"date": "2024-03", "value": "1"}


def test_resample_sum_by_month():
    result = list(resample_rows(_rows(), date_col="date", period="month",
                                agg_col="sales", agg_func="sum"))
    assert result[0]["value"] == "30.0"
    assert result[1]["value"] == "20.0"
    assert result[2]["value"] == "30.0"


def test_resample_mean_by_month():
    result = list(resample_rows(_rows(), date_col="date", period="month",
                                agg_col="sales", agg_func="mean"))
    assert result[0]["value"] == "15.0"


def test_resample_by_year():
    result = list(resample_rows(_rows(), date_col="date", period="year", agg_func="count"))
    assert len(result) == 1
    assert result[0]["date"] == "2024"
    assert result[0]["value"] == "5"


def test_resample_by_day():
    result = list(resample_rows(_rows(), date_col="date", period="day", agg_func="count"))
    assert len(result) == 5
    assert result[0]["date"] == "2024-01-05"


def test_resample_skips_empty_dates():
    rows = [{"date": "", "sales": "5"}, {"date": "2024-06-01", "sales": "9"}]
    result = list(resample_rows(rows, date_col="date", period="month", agg_func="count"))
    assert len(result) == 1


def test_resample_custom_out_col():
    result = list(resample_rows(_rows(), date_col="date", period="month",
                                agg_func="count", out_col="total"))
    assert "total" in result[0]
    assert "value" not in result[0]


def test_resample_invalid_period():
    with pytest.raises(ValueError, match="period must be"):
        list(resample_rows(_rows(), date_col="date", period="decade"))


def test_aggregate_count():
    assert _aggregate(["a", "b", "c"], "count") == "3"


def test_aggregate_no_numeric_returns_empty():
    assert _aggregate(["x", "y"], "sum") == ""


def test_aggregate_min_max():
    vals = ["3", "1", "4", "1", "5"]
    assert _aggregate(vals, "min") == "1.0"
    assert _aggregate(vals, "max") == "5.0"
