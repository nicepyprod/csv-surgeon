import pytest
from csv_surgeon.diff import diff_rows, diff_summary


@pytest.fixture
def left():
    return [
        {"id": "1", "name": "Alice", "score": "90"},
        {"id": "2", "name": "Bob",   "score": "80"},
        {"id": "3", "name": "Carol", "score": "70"},
    ]


@pytest.fixture
def right():
    return [
        {"id": "1", "name": "Alice", "score": "95"},  # modified
        {"id": "2", "name": "Bob",   "score": "80"},  # unchanged
        {"id": "4", "name": "Dave",  "score": "60"},  # added
    ]


def test_diff_rows_modified(left, right):
    result = list(diff_rows(iter(left), iter(right), ["id"]))
    modified = [r for r in result if r["_diff"] == "modified"]
    assert len(modified) == 1
    assert modified[0]["id"] == "1"
    assert modified[0]["score"] == "95"


def test_diff_rows_removed(left, right):
    result = list(diff_rows(iter(left), iter(right), ["id"]))
    removed = [r for r in result if r["_diff"] == "removed"]
    assert len(removed) == 1
    assert removed[0]["id"] == "3"


def test_diff_rows_added(left, right):
    result = list(diff_rows(iter(left), iter(right), ["id"]))
    added = [r for r in result if r["_diff"] == "added"]
    assert len(added) == 1
    assert added[0]["id"] == "4"


def test_diff_rows_no_diff():
    rows = [{"id": "1", "v": "a"}]
    result = list(diff_rows(iter(rows), iter(rows.copy()), ["id"]))
    assert result == []


def test_diff_summary(left, right):
    s = diff_summary(iter(left), iter(right), ["id"])
    assert s["added"] == 1
    assert s["removed"] == 1
    assert s["modified"] == 1
    assert s["unchanged"] == 1


def test_diff_summary_identical(left):
    import copy
    s = diff_summary(iter(left), iter(copy.deepcopy(left)), ["id"])
    assert s["added"] == 0
    assert s["removed"] == 0
    assert s["modified"] == 0
    assert s["unchanged"] == 3


def test_diff_rows_composite_key():
    left = [{"a": "1", "b": "x", "v": "old"}]
    right = [{"a": "1", "b": "x", "v": "new"}]
    result = list(diff_rows(iter(left), iter(right), ["a", "b"]))
    assert result[0]["_diff"] == "modified"
