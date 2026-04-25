"""Tests for csv_surgeon.cartesian."""
from __future__ import annotations

import pytest

from csv_surgeon.cartesian import cartesian_product, repeat_rows, zip_rows


# ---------------------------------------------------------------------------
# fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def left():
    return [{"id": "1", "name": "Alice"}, {"id": "2", "name": "Bob"}]


@pytest.fixture()
def right():
    return [{"color": "red"}, {"color": "blue"}]


# ---------------------------------------------------------------------------
# cartesian_product
# ---------------------------------------------------------------------------


def test_cartesian_product_row_count(left, right):
    result = list(cartesian_product(left, right))
    assert len(result) == 4  # 2 x 2


def test_cartesian_product_prefixes(left, right):
    result = list(cartesian_product(left, right))
    assert "l_id" in result[0]
    assert "r_color" in result[0]
    assert "id" not in result[0]


def test_cartesian_product_custom_prefixes(left, right):
    result = list(cartesian_product(left, right, left_prefix="a_", right_prefix="b_"))
    assert "a_name" in result[0]
    assert "b_color" in result[0]


def test_cartesian_product_empty_right(left):
    result = list(cartesian_product(left, []))
    assert result == []


def test_cartesian_product_empty_left(right):
    result = list(cartesian_product([], right))
    assert result == []


def test_cartesian_product_values(left, right):
    result = list(cartesian_product(left, right))
    names = [r["l_name"] for r in result]
    colors = [r["r_color"] for r in result]
    assert names == ["Alice", "Alice", "Bob", "Bob"]
    assert colors == ["red", "blue", "red", "blue"]


# ---------------------------------------------------------------------------
# zip_rows
# ---------------------------------------------------------------------------


def test_zip_rows_equal_length(left, right):
    result = list(zip_rows(left, right))
    assert len(result) == 2
    assert result[0]["color"] == "red"
    assert result[0]["name"] == "Alice"


def test_zip_rows_left_longer():
    l = [{"a": "1"}, {"a": "2"}, {"a": "3"}]
    r = [{"b": "x"}]
    result = list(zip_rows(l, r, fill_value="N/A"))
    assert len(result) == 3
    assert result[1]["b"] == "N/A"
    assert result[2]["b"] == "N/A"


def test_zip_rows_right_longer():
    l = [{"a": "1"}]
    r = [{"b": "x"}, {"b": "y"}]
    result = list(zip_rows(l, r))
    assert len(result) == 2
    assert result[1]["a"] == ""


def test_zip_rows_clash_renamed():
    l = [{"x": "1"}]
    r = [{"x": "2"}]
    result = list(zip_rows(l, r))
    assert result[0]["x"] == "1"
    assert result[0]["x_right"] == "2"


# ---------------------------------------------------------------------------
# repeat_rows
# ---------------------------------------------------------------------------


def test_repeat_rows_basic():
    rows = [{"v": "a"}, {"v": "b"}]
    result = list(repeat_rows(rows, times=3))
    assert len(result) == 6
    assert [r["v"] for r in result] == ["a", "a", "a", "b", "b", "b"]


def test_repeat_rows_does_not_mutate():
    rows = [{"v": "a"}]
    result = list(repeat_rows(rows, times=2))
    result[0]["v"] = "CHANGED"
    assert result[1]["v"] == "a"


def test_repeat_rows_zero_raises():
    with pytest.raises(ValueError):
        list(repeat_rows([{"v": "a"}], times=0))
