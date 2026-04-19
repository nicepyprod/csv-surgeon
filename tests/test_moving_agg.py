import pytest
from csv_surgeon.moving_agg import group_aggregate


def _rows():
    return [
        {"dept": "eng", "salary": "100"},
        {"dept": "eng", "salary": "200"},
        {"dept": "hr", "salary": "150"},
        {"dept": "hr", "salary": "50"},
        {"dept": "eng", "salary": "300"},
    ]


def test_group_sum():
    result = list(group_aggregate(_rows(), "dept", "salary", func="sum"))
    eng = [r for r in result if r["dept"] == "eng"]
    hr = [r for r in result if r["dept"] == "hr"]
    assert all(r["salary_sum"] == "600.0" for r in eng)
    assert all(r["salary_sum"] == "200.0" for r in hr)


def test_group_mean():
    result = list(group_aggregate(_rows(), "dept", "salary", func="mean"))
    eng = next(r for r in result if r["dept"] == "eng")
    assert eng["salary_mean"] == "200.0"


def test_group_min_max():
    result = list(group_aggregate(_rows(), "dept", "salary", func="min"))
    hr = next(r for r in result if r["dept"] == "hr")
    assert hr["salary_min"] == "50.0"

    result2 = list(group_aggregate(_rows(), "dept", "salary", func="max"))
    hr2 = next(r for r in result2 if r["dept"] == "hr")
    assert hr2["salary_max"] == "150.0"


def test_group_count():
    result = list(group_aggregate(_rows(), "dept", "salary", func="count"))
    eng = [r for r in result if r["dept"] == "eng"]
    assert all(r["salary_count"] == "3" for r in eng)


def test_custom_out_col():
    result = list(group_aggregate(_rows(), "dept", "salary", func="sum", out_col="total"))
    assert "total" in result[0]


def test_empty_value_skipped():
    rows = [{"dept": "a", "salary": ""}, {"dept": "a", "salary": "10"}]
    result = list(group_aggregate(rows, "dept", "salary", func="sum"))
    assert result[0]["salary_sum"] == "10.0"


def test_all_empty_values():
    rows = [{"dept": "a", "salary": ""}, {"dept": "a", "salary": ""}]
    result = list(group_aggregate(rows, "dept", "salary", func="mean"))
    assert result[0]["salary_mean"] == ""


def test_invalid_func():
    with pytest.raises(ValueError, match="Unsupported func"):
        list(group_aggregate(_rows(), "dept", "salary", func="median"))


def test_missing_group_col_uses_empty_string():
    rows = [{"salary": "10"}, {"salary": "20"}]
    result = list(group_aggregate(rows, "dept", "salary", func="sum"))
    assert result[0]["salary_sum"] == "30.0"
