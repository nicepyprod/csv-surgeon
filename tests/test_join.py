import pytest
from csv_surgeon.join import inner_join, left_join


@pytest.fixture
def left_rows():
    return [
        {"id": "1", "name": "Alice"},
        {"id": "2", "name": "Bob"},
        {"id": "3", "name": "Carol"},
    ]


@pytest.fixture
def right_rows():
    return [
        {"id": "1", "dept": "Eng"},
        {"id": "2", "dept": "HR"},
        {"id": "2", "dept": "Finance"},
    ]


def test_inner_join_basic(left_rows, right_rows):
    result = list(inner_join(iter(left_rows), iter(right_rows), "id"))
    assert len(result) == 3
    assert result[0] == {"id": "1", "name": "Alice", "dept": "Eng"}


def test_inner_join_excludes_unmatched(left_rows, right_rows):
    result = list(inner_join(iter(left_rows), iter(right_rows), "id"))
    ids = [r["id"] for r in result]
    assert "3" not in ids


def test_inner_join_multi_match(left_rows, right_rows):
    result = list(inner_join(iter(left_rows), iter(right_rows), "id"))
    bob_rows = [r for r in result if r["name"] == "Bob"]
    assert len(bob_rows) == 2
    depts = {r["dept"] for r in bob_rows}
    assert depts == {"HR", "Finance"}


def test_left_join_keeps_unmatched(left_rows, right_rows):
    result = list(left_join(iter(left_rows), iter(right_rows), "id"))
    ids = [r["id"] for r in result]
    assert "3" in ids


def test_left_join_unmatched_has_no_right_keys(left_rows, right_rows):
    result = list(left_join(iter(left_rows), iter(right_rows), "id"))
    carol = next(r for r in result if r["name"] == "Carol")
    assert "dept" not in carol or carol.get("dept") is None


def test_inner_join_different_keys():
    left = [{"uid": "1", "val": "x"}]
    right = [{"ref": "1", "extra": "y"}]
    result = list(inner_join(iter(left), iter(right), "uid", "ref"))
    assert len(result) == 1
    assert result[0]["extra"] == "y"
