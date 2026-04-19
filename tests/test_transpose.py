"""Tests for csv_surgeon.transpose."""
import pytest
from csv_surgeon.transpose import transpose_rows, transposed_header


@pytest.fixture()
def _rows():
    return [
        {"name": "Alice", "age": "30", "city": "NY"},
        {"name": "Bob",   "age": "25", "city": "LA"},
        {"name": "Carol", "age": "35", "city": "SF"},
    ]


@pytest.fixture()
def _header():
    return ["name", "age", "city"]


def test_transpose_row_count(_rows, _header):
    result = list(transpose_rows(_rows, _header))
    assert len(result) == 3  # one per original column


def test_transpose_index_col_values(_rows, _header):
    result = list(transpose_rows(_rows, _header))
    assert [r["column"] for r in result] == ["name", "age", "city"]


def test_transpose_value_columns(_rows, _header):
    result = list(transpose_rows(_rows, _header))
    name_row = result[0]
    assert name_row["row0"] == "Alice"
    assert name_row["row1"] == "Bob"
    assert name_row["row2"] == "Carol"


def test_transpose_numeric_values(_rows, _header):
    result = list(transpose_rows(_rows, _header))
    age_row = result[1]
    assert age_row["row0"] == "30"
    assert age_row["row1"] == "25"
    assert age_row["row2"] == "35"


def test_transpose_custom_index_col(_rows, _header):
    result = list(transpose_rows(_rows, _header, index_col="field"))
    assert "field" in result[0]
    assert "column" not in result[0]


def test_transpose_custom_value_prefix(_rows, _header):
    result = list(transpose_rows(_rows, _header, value_col_prefix="v"))
    assert "v0" in result[0]
    assert "row0" not in result[0]


def test_transpose_missing_value_is_empty(_header):
    rows = [{"name": "Alice", "age": "30"}, {"name": "Bob", "age": "", "city": "LA"}]
    result = list(transpose_rows(rows, _header))
    city_row = result[2]  # city column
    assert city_row["row0"] == ""  # Alice had no city key
    assert city_row["row1"] == "LA"


def test_transposed_header_length():
    h = transposed_header(4)
    assert len(h) == 5  # index_col + 4 value cols


def test_transposed_header_names():
    h = transposed_header(3)
    assert h == ["column", "row0", "row1", "row2"]


def test_transposed_header_custom():
    h = transposed_header(2, index_col="col", value_col_prefix="r")
    assert h == ["col", "r0", "r1"]
