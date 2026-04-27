"""Tests for csv_surgeon.pivot_table."""
import pytest
from csv_surgeon.pivot_table import pivot_table, _agg


@pytest.fixture()
def sales():
    return [
        {"region": "East", "product": "Apple",  "revenue": "10"},
        {"region": "East", "product": "Banana", "revenue": "20"},
        {"region": "West", "product": "Apple",  "revenue": "30"},
        {"region": "West", "product": "Banana", "revenue": "40"},
        {"region": "East", "product": "Apple",  "revenue": "5"},
    ]


def _pt(rows, **kw):
    return list(pivot_table(rows, **kw))


# --- _agg unit tests ---

def test_agg_sum():
    assert _agg(["1", "2", "3"], "sum") == "6.0"


def test_agg_count():
    assert _agg(["a", "b", "c"], "count") == "3"


def test_agg_mean():
    assert _agg(["10", "20"], "mean") == "15.0"


def test_agg_min_max():
    assert _agg(["3", "1", "2"], "min") == "1.0"
    assert _agg(["3", "1", "2"], "max") == "3.0"


def test_agg_first_last():
    assert _agg(["x", "y", "z"], "first") == "x"
    assert _agg(["x", "y", "z"], "last") == "z"


def test_agg_empty_non_count_returns_empty():
    assert _agg([], "sum") == ""


def test_agg_unknown_raises():
    with pytest.raises(ValueError, match="Unknown aggfunc"):
        _agg(["1"], "median")


# --- pivot_table integration tests ---

def test_pivot_table_row_count(sales):
    result = _pt(sales, index=["region"], pivot_col="product",
                 value_col="revenue", aggfunc="sum")
    assert len(result) == 2


def test_pivot_table_column_names(sales):
    result = _pt(sales, index=["region"], pivot_col="product",
                 value_col="revenue", aggfunc="sum")
    cols = set(result[0].keys())
    assert "region" in cols
    assert "Apple" in cols
    assert "Banana" in cols


def test_pivot_table_sum_values(sales):
    result = _pt(sales, index=["region"], pivot_col="product",
                 value_col="revenue", aggfunc="sum")
    east = next(r for r in result if r["region"] == "East")
    assert east["Apple"] == "15.0"   # 10 + 5
    assert east["Banana"] == "20.0"


def test_pivot_table_fill_value(sales):
    # Add a row that makes North have only Apple
    rows = list(sales) + [{"region": "North", "product": "Apple", "revenue": "7"}]
    result = _pt(rows, index=["region"], pivot_col="product",
                 value_col="revenue", aggfunc="sum", fill_value="0")
    north = next(r for r in result if r["region"] == "North")
    assert north["Banana"] == "0"


def test_pivot_table_count_aggfunc(sales):
    result = _pt(sales, index=["region"], pivot_col="product",
                 value_col="revenue", aggfunc="count")
    east = next(r for r in result if r["region"] == "East")
    assert east["Apple"] == "2"


def test_pivot_table_multi_index():
    rows = [
        {"dept": "A", "year": "2023", "month": "Jan", "sales": "100"},
        {"dept": "A", "year": "2023", "month": "Feb", "sales": "200"},
        {"dept": "B", "year": "2023", "month": "Jan", "sales": "50"},
    ]
    result = _pt(rows, index=["dept", "year"], pivot_col="month",
                 value_col="sales", aggfunc="sum")
    assert len(result) == 2
    a = next(r for r in result if r["dept"] == "A")
    assert a["Jan"] == "100.0"
    assert a["Feb"] == "200.0"
