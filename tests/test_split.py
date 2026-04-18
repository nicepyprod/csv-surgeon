"""Tests for csv_surgeon.split."""
import pytest
from csv_surgeon.split import split_rows, split_to_buffers, split_evenly


@pytest.fixture()
def _rows():
    return [
        {"dept": "eng", "name": "alice"},
        {"dept": "hr", "name": "bob"},
        {"dept": "eng", "name": "carol"},
        {"dept": "hr", "name": "dave"},
        {"dept": "finance", "name": "eve"},
    ]


def test_split_rows_basic(_rows):
    groups = split_rows(_rows, "dept")
    assert set(groups.keys()) == {"eng", "hr", "finance"}
    assert len(groups["eng"]) == 2
    assert len(groups["hr"]) == 2
    assert len(groups["finance"]) == 1


def test_split_rows_preserves_content(_rows):
    groups = split_rows(_rows, "dept")
    names = [r["name"] for r in groups["eng"]]
    assert names == ["alice", "carol"]


def test_split_rows_missing_column(_rows):
    groups = split_rows(_rows, "nonexistent")
    assert list(groups.keys()) == [""]
    assert len(groups[""]) == 5


def test_split_rows_max_groups_exceeded(_rows):
    with pytest.raises(ValueError, match="max_groups"):
        split_rows(_rows, "dept", max_groups=2)


def test_split_rows_max_groups_ok(_rows):
    groups = split_rows(_rows, "dept", max_groups=3)
    assert len(groups) == 3


def test_split_to_buffers(_rows):
    fieldnames = ["dept", "name"]
    buffers = split_to_buffers(_rows, "dept", fieldnames)
    assert "eng" in buffers
    content = buffers["eng"].read()
    assert "alice" in content
    assert "carol" in content
    assert "bob" not in content


def test_split_evenly_basic(_rows):
    chunks = list(split_evenly(_rows, 2))
    assert len(chunks) == 3
    assert len(chunks[0]) == 2
    assert len(chunks[1]) == 2
    assert len(chunks[2]) == 1


def test_split_evenly_exact(_rows):
    rows = _rows[:4]
    chunks = list(split_evenly(rows, 2))
    assert len(chunks) == 2
    assert all(len(c) == 2 for c in chunks)


def test_split_evenly_invalid_chunk_size(_rows):
    with pytest.raises(ValueError, match="chunk_size"):
        list(split_evenly(_rows, 0))
