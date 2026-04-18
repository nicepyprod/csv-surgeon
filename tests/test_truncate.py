import pytest
from csv_surgeon.truncate import truncate_column, truncate_columns, pad_column


def _rows():
    return [
        {"name": "Alexander", "city": "San Francisco", "code": "XY"},
        {"name": "Jo", "city": "LA", "code": "ABCDEF"},
        {"name": "", "city": "Portland", "code": "123"},
    ]


def test_truncate_column_basic():
    result = list(truncate_column(iter(_rows()), "name", 5))
    assert result[0]["name"] == "Alexa"
    assert result[1]["name"] == "Jo"
    assert result[2]["name"] == ""


def test_truncate_column_with_suffix():
    result = list(truncate_column(iter(_rows()), "name", 6, suffix="..."))
    assert result[0]["name"] == "Ale..."
    assert result[1]["name"] == "Jo"


def test_truncate_column_suffix_longer_than_max():
    # suffix longer than max_length: core becomes 0, only suffix prefix used
    result = list(truncate_column(iter(_rows()), "name", 2, suffix="..."))
    assert len(result[0]["name"]) <= 2 or result[0]["name"] == "..."


def test_truncate_column_unknown_column_passthrough():
    result = list(truncate_column(iter(_rows()), "nonexistent", 3))
    assert result[0]["name"] == "Alexander"


def test_truncate_column_invalid_max_length():
    with pytest.raises(ValueError):
        list(truncate_column(iter(_rows()), "name", -1))


def test_truncate_columns_multiple():
    result = list(truncate_columns(iter(_rows()), ["name", "city"], 4))
    assert result[0]["name"] == "Alex"
    assert result[0]["city"] == "San "
    assert result[0]["code"] == "XY"  # untouched


def test_truncate_columns_invalid_max_length():
    with pytest.raises(ValueError):
        list(truncate_columns(iter(_rows()), ["name"], -5))


def test_pad_column_left():
    result = list(pad_column(iter(_rows()), "code", 6))
    assert result[0]["code"] == "XY    "
    assert result[1]["code"] == "ABCDEF"


def test_pad_column_right():
    result = list(pad_column(iter(_rows()), "code", 6, align="right"))
    assert result[0]["code"] == "    XY"


def test_pad_column_center():
    result = list(pad_column(iter(_rows()), "code", 6, align="center"))
    assert result[0]["code"] == "  XY  "


def test_pad_column_custom_fillchar():
    result = list(pad_column(iter(_rows()), "code", 5, fillchar="0", align="right"))
    assert result[0]["code"] == "000XY"


def test_pad_column_invalid_fillchar():
    with pytest.raises(ValueError):
        list(pad_column(iter(_rows()), "code", 5, fillchar="ab"))


def test_pad_column_invalid_align():
    with pytest.raises(ValueError):
        list(pad_column(iter(_rows()), "code", 5, align="middle"))
