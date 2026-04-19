"""Tests for csv_surgeon.dateparse."""
from __future__ import annotations
import pytest
from csv_surgeon.dateparse import parse_date_column, format_date_column, extract_date_part


def _rows():
    return [
        {"id": "1", "date": "2024-01-15"},
        {"id": "2", "date": "31/12/2023"},
        {"id": "3", "date": ""},
        {"id": "4", "date": "2022/06/30"},
    ]


def test_parse_date_column_returns_datetime():
    result = list(parse_date_column(_rows(), "date"))
    from datetime import datetime
    assert result[0]["date"] == datetime(2024, 1, 15)
    assert result[1]["date"] == datetime(2023, 12, 31)


def test_parse_date_column_empty_value_is_none():
    result = list(parse_date_column(_rows(), "date"))
    assert result[2]["date"] is None


def test_parse_date_column_out_column():
    result = list(parse_date_column(_rows(), "date", out_column="parsed"))
    assert "parsed" in result[0]
    assert "date" in result[0]  # original preserved


def test_format_date_column_iso_to_us():
    rows = [{"d": "2024-03-07"}]
    result = list(format_date_column(rows, "d", out_fmt="%m/%d/%Y"))
    assert result[0]["d"] == "03/07/2024"


def test_format_date_column_empty_passthrough():
    rows = [{"d": ""}]
    result = list(format_date_column(rows, "d", out_fmt="%Y-%m-%d"))
    assert result[0]["d"] == ""


def test_format_date_column_unknown_format_yields_empty():
    rows = [{"d": "not-a-date"}]
    result = list(format_date_column(rows, "d", out_fmt="%Y-%m-%d"))
    assert result[0]["d"] == ""


def test_format_date_column_out_column():
    rows = [{"d": "2024-01-01"}]
    result = list(format_date_column(rows, "d", out_fmt="%d/%m/%Y", out_column="formatted"))
    assert result[0]["formatted"] == "01/01/2024"
    assert result[0]["d"] == "2024-01-01"


def test_extract_date_part_year():
    result = list(extract_date_part(_rows(), "date", "year"))
    assert result[0]["date_year"] == "2024"
    assert result[1]["date_year"] == "2023"


def test_extract_date_part_month():
    result = list(extract_date_part(_rows(), "date", "month"))
    assert result[0]["date_month"] == "1"


def test_extract_date_part_weekday():
    result = list(extract_date_part(_rows(), "date", "weekday"))
    # 2024-01-15 is Monday => weekday() == 0
    assert result[0]["date_weekday"] == "0"


def test_extract_date_part_empty_yields_empty():
    result = list(extract_date_part(_rows(), "date", "year"))
    assert result[2]["date_year"] == ""


def test_extract_date_part_custom_out_column():
    result = list(extract_date_part(_rows(), "date", "day", out_column="day_num"))
    assert "day_num" in result[0]


def test_extract_date_part_invalid_part_raises():
    with pytest.raises(ValueError):
        list(extract_date_part(_rows(), "date", "quarter"))
