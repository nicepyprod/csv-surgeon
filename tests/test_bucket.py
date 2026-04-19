"""Tests for csv_surgeon.bucket."""
import pytest
from csv_surgeon.bucket import bucket_column, equal_width_edges, _find_bucket


def _rows():
    return [
        {"name": "a", "score": "10"},
        {"name": "b", "score": "35"},
        {"name": "c", "score": "55"},
        {"name": "d", "score": "80"},
        {"name": "e", "score": ""},
    ]


EDGES = [0.0, 33.3, 66.6, 100.0]
LABELS = ["low", "mid", "high"]


def test_bucket_basic_labels():
    result = list(bucket_column(_rows(), "score", EDGES, LABELS))
    assert result[0]["score_bucket"] == "low"
    assert result[1]["score_bucket"] == "mid"
    assert result[2]["score_bucket"] == "mid"
    assert result[3]["score_bucket"] == "high"


def test_bucket_empty_value_yields_empty_string():
    result = list(bucket_column(_rows(), "score", EDGES, LABELS))
    assert result[4]["score_bucket"] == ""


def test_bucket_default_labels():
    result = list(bucket_column(_rows(), "score", EDGES))
    assert result[0]["score_bucket"] == "0.0-33.3"


def test_bucket_custom_out_column():
    result = list(bucket_column(_rows(), "score", EDGES, LABELS, out_column="tier"))
    assert "tier" in result[0]
    assert "score_bucket" not in result[0]


def test_bucket_preserves_other_columns():
    result = list(bucket_column(_rows(), "score", EDGES, LABELS))
    assert result[0]["name"] == "a"


def test_bucket_wrong_label_count_raises():
    with pytest.raises(ValueError, match="Expected 3 labels"):
        list(bucket_column(_rows(), "score", EDGES, ["only_one"]))


def test_bucket_too_few_edges_raises():
    with pytest.raises(ValueError, match="at least 2"):
        list(bucket_column(_rows(), "score", [0.0]))


def test_equal_width_edges_basic():
    edges = equal_width_edges(0.0, 100.0, 4)
    assert len(edges) == 5
    assert edges[0] == pytest.approx(0.0)
    assert edges[-1] == pytest.approx(100.0)
    assert edges[2] == pytest.approx(50.0)


def test_equal_width_edges_bins_lt_1_raises():
    with pytest.raises(ValueError):
        equal_width_edges(0, 10, 0)


def test_find_bucket_include_lowest():
    assert _find_bucket(0.0, [0.0, 50.0, 100.0], ["lo", "hi"], True) == "lo"


def test_find_bucket_out_of_range_returns_empty():
    assert _find_bucket(200.0, [0.0, 50.0, 100.0], ["lo", "hi"], True) == ""
