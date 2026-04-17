import pytest
from csv_surgeon.aggregate import aggregate_rows


@pytest.fixture
def _rows():
    return [
        {"dept": "eng", "name": "alice", "salary": "90000"},
        {"dept": "eng", "name": "bob",   "salary": "80000"},
        {"dept": "hr",  "name": "carol", "salary": "70000"},
        {"dept": "hr",  "name": "dave",  "salary": ""},
        {"dept": "eng", "name": "eve",   "salary": "95000"},
    ]


def test_sum(_rows):
    result = list(aggregate_rows(_rows, ["dept"], "salary", "sum"))
    by_dept = {r["dept"]: r for r in result}
    assert by_dept["eng"]["sum_salary"] == "265000.0"
    assert by_dept["hr"]["sum_salary"] == "70000.0"


def test_count(_rows):
    result = list(aggregate_rows(_rows, ["dept"], "salary", "count"))
    by_dept = {r["dept"]: r for r in result}
    assert by_dept["eng"]["count_salary"] == "3"
    assert by_dept["hr"]["count_salary"] == "1"  # empty string skipped


def test_mean(_rows):
    result = list(aggregate_rows(_rows, ["dept"], "salary", "mean"))
    by_dept = {r["dept"]: r for r in result}
    assert float(by_dept["eng"]["mean_salary"]) == pytest.approx(88333.333, rel=1e-3)


def test_min_max(_rows):
    result_min = list(aggregate_rows(_rows, ["dept"], "salary", "min"))
    result_max = list(aggregate_rows(_rows, ["dept"], "salary", "max"))
    by_min = {r["dept"]: r for r in result_min}
    by_max = {r["dept"]: r for r in result_max}
    assert float(by_min["eng"]["min_salary"]) == 80000.0
    assert float(by_max["eng"]["max_salary"]) == 95000.0


def test_multi_group_by():
    rows = [
        {"dept": "eng", "level": "senior", "bonus": "10000"},
        {"dept": "eng", "level": "junior", "bonus": "5000"},
        {"dept": "eng", "level": "senior", "bonus": "12000"},
    ]
    result = list(aggregate_rows(rows, ["dept", "level"], "bonus", "sum"))
    assert len(result) == 2
    by_level = {r["level"]: r for r in result}
    assert float(by_level["senior"]["sum_bonus"]) == 22000.0


def test_unknown_func(_rows):
    with pytest.raises(ValueError, match="Unknown aggregation"):
        list(aggregate_rows(_rows, ["dept"], "salary", "median"))


def test_all_empty_values():
    rows = [{"dept": "eng", "salary": ""}, {"dept": "eng", "salary": ""}]
    result = list(aggregate_rows(rows, ["dept"], "salary", "min"))
    assert result[0]["min_salary"] == ""
