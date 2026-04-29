"""Tests for csv_surgeon.datetime_diff."""
import pytest
from csv_surgeon.datetime_diff import datetime_diff_column


def _rows():
    return [
        {"id": "1", "start": "2024-01-01", "end": "2024-01-11"},
        {"id": "2", "start": "2024-03-01", "end": "2024-03-01"},
        {"id": "3", "start": "",           "end": "2024-06-15"},
        {"id": "4", "start": "2024-01-01", "end": ""},
        {"id": "5", "start": "2024-06-15", "end": "2024-01-01"},
    ]


def _run(rows=None, **kwargs):
    return list(datetime_diff_column(iter(rows or _rows()), **kwargs))


def test_diff_days_basic():
    result = _run(col_a="start", col_b="end")
    assert result[0]["diff_days"] == "10"


def test_diff_zero_days():
    result = _run(col_a="start", col_b="end")
    assert result[1]["diff_days"] == "0"


def test_diff_empty_start_yields_empty():
    result = _run(col_a="start", col_b="end")
    assert result[2]["diff_days"] == ""


def test_diff_empty_end_yields_empty():
    result = _run(col_a="start", col_b="end")
    assert result[3]["diff_days"] == ""


def test_diff_negative_days():
    result = _run(col_a="start", col_b="end")
    assert result[4]["diff_days"] == "-166"


def test_diff_absolute_flag():
    result = _run(col_a="start", col_b="end", absolute=True)
    assert result[4]["diff_days"] == "166"


def test_diff_unit_hours():
    result = _run(col_a="start", col_b="end", unit="hours")
    assert result[0]["diff_days"] == "240"


def test_diff_custom_out_column():
    result = _run(col_a="start", col_b="end", out_column="duration")
    assert "duration" in result[0]
    assert "diff_days" not in result[0]


def test_diff_preserves_other_columns():
    result = _run(col_a="start", col_b="end")
    assert result[0]["id"] == "1"
    assert result[0]["start"] == "2024-01-01"


def test_diff_invalid_unit_raises():
    with pytest.raises(ValueError, match="unit must be one of"):
        _run(col_a="start", col_b="end", unit="weeks")


def test_diff_custom_fmt():
    rows = [{"a": "01/01/2024", "b": "11/01/2024"}]
    result = list(datetime_diff_column(iter(rows), col_a="a", col_b="b",
                                       fmt="%d/%m/%Y"))
    assert result[0]["diff_days"] == "10"


def test_diff_unit_minutes():
    rows = [
        {"a": "2024-01-01 00:00:00", "b": "2024-01-01 01:30:00"},
    ]
    result = list(datetime_diff_column(iter(rows), col_a="a", col_b="b",
                                       unit="minutes"))
    assert result[0]["diff_days"] == "90"
