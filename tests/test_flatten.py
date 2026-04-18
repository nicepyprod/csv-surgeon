import pytest
from csv_surgeon.flatten import flatten_column, collapse_column


@pytest.fixture
def _rows():
    return [
        {"id": "1", "name": "Alice", "tags": "python|csv|cli"},
        {"id": "2", "name": "Bob",   "tags": "csv"},
        {"id": "3", "name": "Carol", "tags": ""},
        {"id": "4", "name": "Dan",   "tags": "python|data"},
    ]


def test_flatten_basic(_rows):
    out = list(flatten_column(_rows, "tags"))
    assert len(out) == 6  # 3+1+0(pass)+2
    assert out[0] == {"id": "1", "name": "Alice", "tags": "python"}
    assert out[1]["tags"] == "csv"
    assert out[2]["tags"] == "cli"


def test_flatten_empty_passthrough(_rows):
    out = list(flatten_column(_rows, "tags"))
    carol = [r for r in out if r["name"] == "Carol"]
    assert len(carol) == 1
    assert carol[0]["tags"] == ""


def test_flatten_custom_sep():
    rows = [{"id": "1", "vals": "a,b,c"}]
    out = list(flatten_column(rows, "vals", sep=","))
    assert [r["vals"] for r in out] == ["a", "b", "c"]


def test_flatten_missing_column():
    rows = [{"id": "1", "name": "X"}]
    out = list(flatten_column(rows, "tags"))
    assert out == [{"id": "1", "name": "X"}]


def test_collapse_roundtrip(_rows):
    flat = list(flatten_column(_rows, "tags"))
    collapsed = list(collapse_column(flat, "tags", key_column="id"))
    by_id = {r["id"]: r for r in collapsed}
    assert by_id["1"]["tags"] == "python|csv|cli"
    assert by_id["2"]["tags"] == "csv"
    assert by_id["3"]["tags"] == ""
    assert by_id["4"]["tags"] == "python|data"


def test_collapse_preserves_order(_rows):
    flat = list(flatten_column(_rows, "tags"))
    collapsed = list(collapse_column(flat, "tags", key_column="id"))
    assert [r["id"] for r in collapsed] == ["1", "2", "3", "4"]
