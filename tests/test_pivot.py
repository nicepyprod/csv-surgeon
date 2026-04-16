"""Tests for csv_surgeon.pivot."""
import pytest
from csv_surgeon.pivot import pivot_rows, melt_rows


@pytest.fixture
def sales_rows():
    return [
        {"region": "north", "product": "apple", "revenue": "100"},
        {"region": "north", "product": "banana", "revenue": "200"},
        {"region": "south", "product": "apple", "revenue": "150"},
        {"region": "south", "product": "banana", "revenue": "50"},
    ]


@pytest.fixture
def wide_rows():
    return [
        {"id": "1", "name": "alice", "jan": "10", "feb": "20"},
        {"id": "2", "name": "bob", "jan": "30", "feb": "40"},
    ]


def test_pivot_basic(sales_rows):
    result = pivot_rows(sales_rows, index="region", columns="product", values="revenue")
    by_region = {r["region"]: r for r in result}
    assert by_region["north"]["apple"] == "100"
    assert by_region["north"]["banana"] == "200"
    assert by_region["south"]["apple"] == "150"


def test_pivot_missing_value_is_empty(sales_rows):
    # remove one combination
    rows = [r for r in sales_rows if not (r["region"] == "south" and r["product"] == "banana")]
    result = pivot_rows(rows, index="region", columns="product", values="revenue")
    by_region = {r["region"]: r for r in result}
    assert by_region["south"]["banana"] == ""


def test_pivot_aggfunc_first():
    rows = [
        {"k": "a", "col": "x", "val": "first"},
        {"k": "a", "col": "x", "val": "second"},
    ]
    result = pivot_rows(rows, index="k", columns="col", values="val", aggfunc="first")
    assert result[0]["x"] == "first"


def test_pivot_aggfunc_last():
    rows = [
        {"k": "a", "col": "x", "val": "first"},
        {"k": "a", "col": "x", "val": "second"},
    ]
    result = pivot_rows(rows, index="k", columns="col", values="val", aggfunc="last")
    assert result[0]["x"] == "second"


def test_melt_basic(wide_rows):
    result = list(melt_rows(wide_rows, id_vars=["id", "name"], value_vars=["jan", "feb"]))
    assert len(result) == 4
    first = result[0]
    assert first["id"] == "1"
    assert first["variable"] == "jan"
    assert first["value"] == "10"


def test_melt_custom_names(wide_rows):
    result = list(
        melt_rows(wide_rows, id_vars=["id"], value_vars=["jan"], var_name="month", value_name="amount")
    )
    assert result[0]["month"] == "jan"
    assert result[0]["amount"] == "10"


def test_melt_preserves_id_vars(wide_rows):
    result = list(melt_rows(wide_rows, id_vars=["id", "name"], value_vars=["jan", "feb"]))
    names = [r["name"] for r in result]
    assert names.count("alice") == 2
    assert names.count("bob") == 2
