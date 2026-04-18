import pytest
from csv_surgeon.crossjoin import cross_join, semi_join, anti_join


@pytest.fixture
def left():
    return [
        {"id": "1", "name": "Alice"},
        {"id": "2", "name": "Bob"},
    ]


@pytest.fixture
def right():
    return [
        {"color": "red"},
        {"color": "blue"},
    ]


def test_cross_join_row_count(left, right):
    rows = list(cross_join(left, right))
    assert len(rows) == 4


def test_cross_join_keys_prefixed(left, right):
    rows = list(cross_join(left, right))
    assert "l_id" in rows[0]
    assert "r_color" in rows[0]
    assert "id" not in rows[0]


def test_cross_join_custom_prefix(left, right):
    rows = list(cross_join(left, right, left_prefix="a_", right_prefix="b_"))
    assert "a_name" in rows[0]
    assert "b_color" in rows[0]


def test_cross_join_empty_right(left):
    rows = list(cross_join(left, []))
    assert rows == []


def test_semi_join_basic():
    left = [{"dept": "eng", "emp": "Alice"}, {"dept": "hr", "emp": "Bob"}]
    right = [{"dept": "eng"}]
    rows = list(semi_join(left, right, key="dept"))
    assert len(rows) == 1
    assert rows[0]["emp"] == "Alice"


def test_semi_join_different_right_key():
    left = [{"id": "1"}, {"id": "2"}, {"id": "3"}]
    right = [{"ref": "1"}, {"ref": "3"}]
    rows = list(semi_join(left, right, key="id", right_key="ref"))
    assert [r["id"] for r in rows] == ["1", "3"]


def test_anti_join_basic():
    left = [{"dept": "eng", "emp": "Alice"}, {"dept": "hr", "emp": "Bob"}]
    right = [{"dept": "eng"}]
    rows = list(anti_join(left, right, key="dept"))
    assert len(rows) == 1
    assert rows[0]["emp"] == "Bob"


def test_anti_join_all_excluded():
    left = [{"id": "1"}, {"id": "2"}]
    right = [{"id": "1"}, {"id": "2"}]
    rows = list(anti_join(left, right, key="id"))
    assert rows == []


def test_anti_join_none_excluded():
    left = [{"id": "1"}, {"id": "2"}]
    right = [{"id": "9"}]
    rows = list(anti_join(left, right, key="id"))
    assert len(rows) == 2
