import pytest
from csv_surgeon.rank import rank_rows


@pytest.fixture
def _rows():
    return [
        {"name": "Alice", "score": "90"},
        {"name": "Bob",   "score": "70"},
        {"name": "Carol", "score": "90"},
        {"name": "Dave",  "score": "80"},
    ]


def test_rank_dense_ascending(_rows):
    result = list(rank_rows(_rows, "score", ascending=True, method="dense"))
    by_name = {r["name"]: r["rank"] for r in result}
    assert by_name["Bob"] == "1"
    assert by_name["Dave"] == "2"
    assert by_name["Alice"] == by_name["Carol"] == "3"


def test_rank_dense_descending(_rows):
    result = list(rank_rows(_rows, "score", ascending=False, method="dense"))
    by_name = {r["name"]: r["rank"] for r in result}
    assert by_name["Alice"] == "1"
    assert by_name["Carol"] == "1"
    assert by_name["Dave"] == "2"
    assert by_name["Bob"] == "3"


def test_rank_row_number_unique(_rows):
    result = list(rank_rows(_rows, "score", method="row_number"))
    ranks = sorted(int(r["rank"]) for r in result)
    assert ranks == [1, 2, 3, 4]


def test_rank_percent(_rows):
    result = list(rank_rows(_rows, "score", ascending=True, method="percent"))
    pcts = [float(r["rank"]) for r in result]
    assert all(0.0 <= p <= 1.0 for p in pcts)


def test_rank_custom_out_column(_rows):
    result = list(rank_rows(_rows, "score", out_column="position"))
    assert "position" in result[0]
    assert "rank" not in result[0]


def test_rank_does_not_mutate_original(_rows):
    original = [{**r} for r in _rows]
    list(rank_rows(_rows, "score"))
    assert _rows == original


def test_rank_empty_rows():
    assert list(rank_rows([], "score")) == []


def test_rank_invalid_method(_rows):
    with pytest.raises(ValueError, match="Unknown rank method"):
        list(rank_rows(_rows, "score", method="min"))


def test_rank_missing_column(_rows):
    result = list(rank_rows(_rows, "nonexistent", method="row_number"))
    # NaN values still produce ranks
    assert all("rank" in r for r in result)
