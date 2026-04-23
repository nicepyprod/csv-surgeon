"""Tests for csv_surgeon.percentile."""
import pytest
from csv_surgeon.percentile import percentile_column, quantile_summary, _percentile


def _rows():
    return [
        {"name": "a", "score": "10"},
        {"name": "b", "score": "20"},
        {"name": "c", "score": "30"},
        {"name": "d", "score": "40"},
        {"name": "e", "score": "50"},
    ]


# --- _percentile unit tests ---

def test_percentile_min():
    assert _percentile([1.0, 2.0, 3.0], 0) == 1.0


def test_percentile_max():
    assert _percentile([1.0, 2.0, 3.0], 100) == 3.0


def test_percentile_median():
    assert _percentile([1.0, 2.0, 3.0], 50) == 2.0


def test_percentile_interpolated():
    result = _percentile([0.0, 10.0], 25)
    assert result == pytest.approx(2.5)


def test_percentile_single_element():
    assert _percentile([42.0], 75) == 42.0


def test_percentile_empty_raises():
    with pytest.raises(ValueError, match="empty"):
        _percentile([], 50)


# --- percentile_column tests ---

def test_percentile_column_adds_output_columns():
    result = list(percentile_column(_rows(), "score", [50], ["above_median"]))
    assert all("above_median" in r for r in result)


def test_percentile_column_default_out_names():
    result = list(percentile_column(_rows(), "score", [25, 75]))
    assert "p25" in result[0]
    assert "p75" in result[0]


def test_percentile_column_flag_at_or_below():
    result = list(percentile_column(_rows(), "score", [50]))
    # scores 10, 20, 30 are <= 30 (p50 of [10,20,30,40,50])
    at_or_below = [r for r in result if r["p50"] == "1"]
    assert len(at_or_below) == 3


def test_percentile_column_empty_value_yields_empty_string():
    rows = [{"score": ""}, {"score": "10"}, {"score": "20"}]
    result = list(percentile_column(rows, "score", [50]))
    assert result[0]["p50"] == ""


def test_percentile_column_all_empty_passthrough():
    rows = [{"score": ""}, {"score": "n/a"}]
    result = list(percentile_column(rows, "score", [50]))
    assert result == [{"score": "", "p50": ""}, {"score": "n/a", "p50": ""}]


def test_percentile_column_mismatched_out_columns_raises():
    with pytest.raises(ValueError, match="length"):
        list(percentile_column(_rows(), "score", [25, 75], out_columns=["only_one"]))


# --- quantile_summary tests ---

def test_quantile_summary_quartiles():
    summary = quantile_summary(_rows(), "score", q=4)
    assert summary["min"] == pytest.approx(10.0)
    assert summary["max"] == pytest.approx(50.0)
    assert "Q1" in summary
    assert "Q2" in summary
    assert "Q3" in summary


def test_quantile_summary_empty_returns_empty_dict():
    assert quantile_summary([], "score") == {}


def test_quantile_summary_tertiles():
    summary = quantile_summary(_rows(), "score", q=3)
    assert "Q1" in summary
    assert "Q2" in summary
    assert "Q3" not in summary
