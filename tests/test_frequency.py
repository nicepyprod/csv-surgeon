"""Tests for csv_surgeon.frequency."""
import pytest
from csv_surgeon.frequency import value_counts, top_n, frequency_filter


@pytest.fixture()
def _rows():
    return [
        {"dept": "eng", "name": "alice"},
        {"dept": "eng", "name": "bob"},
        {"dept": "hr", "name": "carol"},
        {"dept": "eng", "name": "dave"},
        {"dept": "hr", "name": "eve"},
        {"dept": "finance", "name": "frank"},
    ]


def test_value_counts_sorted(_rows):
    result = value_counts(_rows, "dept")
    assert result[0]["value"] == "eng"
    assert result[0]["count"] == "3"


def test_value_counts_all_values(_rows):
    result = value_counts(_rows, "dept")
    assert len(result) == 3


def test_value_counts_normalize(_rows):
    result = value_counts(_rows, "dept", normalize=True)
    eng = next(r for r in result if r["value"] == "eng")
    assert float(eng["percent"]) == pytest.approx(50.0)


def test_value_counts_no_sort(_rows):
    result = value_counts(_rows, "dept", sort=False)
    assert {r["value"] for r in result} == {"eng", "hr", "finance"}


def test_top_n(_rows):
    result = top_n(_rows, "dept", n=2)
    assert len(result) == 2
    assert result[0]["value"] == "eng"


def test_top_n_larger_than_population(_rows):
    result = top_n(_rows, "dept", n=100)
    assert len(result) == 3


def test_frequency_filter_basic(_rows):
    result = list(frequency_filter(_rows, "dept", min_count=2))
    depts = {r["dept"] for r in result}
    assert "finance" not in depts
    assert "eng" in depts
    assert "hr" in depts


def test_frequency_filter_min_count_1(_rows):
    result = list(frequency_filter(_rows, "dept", min_count=1))
    assert len(result) == len(_rows)


def test_frequency_filter_high_threshold(_rows):
    result = list(frequency_filter(_rows, "dept", min_count=10))
    assert result == []


def test_value_counts_missing_column(_rows):
    result = value_counts(_rows, "nonexistent")
    assert len(result) == 1
    assert result[0]["value"] == ""
    assert result[0]["count"] == str(len(_rows))
