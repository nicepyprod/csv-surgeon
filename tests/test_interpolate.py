import pytest
from csv_surgeon.interpolate import interpolate_linear, interpolate_constant, interpolate_columns


def _rows(*vals):
    return [{"x": v, "y": "1"} for v in vals]


def test_linear_fills_middle_gap():
    rows = _rows("0", "", "10")
    result = interpolate_linear(rows, "x")
    assert result[1]["x"] == "5"


def test_linear_fills_multiple_gap():
    rows = _rows("0", "", "", "9")
    result = interpolate_linear(rows, "x")
    assert result[1]["x"] == "3"
    assert result[2]["x"] == "6"


def test_linear_leading_gap_uses_right():
    rows = _rows("", "", "7")
    result = interpolate_linear(rows, "x")
    assert result[0]["x"] == "7"
    assert result[1]["x"] == "7"


def test_linear_trailing_gap_uses_left():
    rows = _rows("3", "", "")
    result = interpolate_linear(rows, "x")
    assert result[1]["x"] == "3"
    assert result[2]["x"] == "3"


def test_linear_no_gaps_unchanged():
    rows = _rows("1", "2", "3")
    result = interpolate_linear(rows, "x")
    assert [r["x"] for r in result] == ["1", "2", "3"]


def test_linear_unknown_column_passthrough():
    rows = _rows("1", "", "3")
    result = interpolate_linear(rows, "z")
    assert result == rows


def test_constant_fills_empty():
    rows = [{"a": "", "b": "x"}, {"a": "5", "b": ""}]
    result = list(interpolate_constant(rows, "a", fill="99"))
    assert result[0]["a"] == "99"
    assert result[1]["a"] == "5"


def test_constant_default_fill_zero():
    rows = [{"a": ""}]
    result = list(interpolate_constant(rows, "a"))
    assert result[0]["a"] == "0"


def test_constant_unknown_column_passthrough():
    rows = [{"a": "1"}]
    result = list(interpolate_constant(rows, "z"))
    assert result[0]["a"] == "1"


def test_interpolate_columns_linear_multi():
    rows = [
        {"a": "0", "b": "10"},
        {"a": "",  "b": ""},
        {"a": "4", "b": "20"},
    ]
    result = interpolate_columns(rows, ["a", "b"], method="linear")
    assert result[1]["a"] == "2"
    assert result[1]["b"] == "15"


def test_interpolate_columns_constant_multi():
    rows = [{"a": "", "b": ""}]
    result = interpolate_columns(rows, ["a", "b"], method="constant", fill="-1")
    assert result[0]["a"] == "-1"
    assert result[0]["b"] == "-1"
