"""Tests for csv_surgeon.slice."""
import pytest
from csv_surgeon.slice import head_rows, tail_rows, slice_rows


def _rows():
    return [
        {"id": str(i), "val": str(i * 10)}
        for i in range(1, 9)  # 1-8
    ]


def test_head_returns_first_n():
    result = list(head_rows(iter(_rows()), 3))
    assert len(result) == 3
    assert result[0]["id"] == "1"
    assert result[-1]["id"] == "3"


def test_head_n_larger_than_population():
    result = list(head_rows(iter(_rows()), 100))
    assert len(result) == 8


def test_head_zero():
    result = list(head_rows(iter(_rows()), 0))
    assert result == []


def test_tail_returns_last_n():
    result = tail_rows(iter(_rows()), 3)
    assert len(result) == 3
    assert result[-1]["id"] == "8"
    assert result[0]["id"] == "6"


def test_tail_n_larger_than_population():
    result = tail_rows(iter(_rows()), 100)
    assert len(result) == 8


def test_slice_basic_range():
    result = list(slice_rows(iter(_rows()), start=2, stop=5))
    ids = [r["id"] for r in result]
    assert ids == ["3", "4", "5"]


def test_slice_with_step():
    result = list(slice_rows(iter(_rows()), start=0, stop=8, step=2))
    ids = [r["id"] for r in result]
    assert ids == ["1", "3", "5", "7"]


def test_slice_no_stop():
    result = list(slice_rows(iter(_rows()), start=5))
    ids = [r["id"] for r in result]
    assert ids == ["6", "7", "8"]


def test_slice_invalid_step():
    with pytest.raises(ValueError):
        list(slice_rows(iter(_rows()), step=0))
