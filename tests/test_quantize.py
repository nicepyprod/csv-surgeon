"""Tests for csv_surgeon.quantize."""
import pytest
from csv_surgeon.quantize import quantize_column, equal_width_quantize


@pytest.fixture
def _rows():
    return [
        {"name": "a", "score": "5"},
        {"name": "b", "score": "15"},
        {"name": "c", "score": "25"},
        {"name": "d", "score": ""},
        {"name": "e", "score": "10"},
    ]


def test_quantize_column_basic_labels(_rows):
    edges = [0, 10, 20, 30]
    labels = ["low", "mid", "high"]
    result = list(quantize_column(_rows, "score", edges, labels=labels))
    assert result[0]["score_bin"] == "low"
    assert result[1]["score_bin"] == "mid"
    assert result[2]["score_bin"] == "high"


def test_quantize_column_empty_value_yields_empty(_rows):
    edges = [0, 10, 20, 30]
    result = list(quantize_column(_rows, "score", edges))
    assert result[3]["score_bin"] == ""


def test_quantize_column_default_out_column(_rows):
    result = list(quantize_column(_rows, "score", [0, 30]))
    assert "score_bin" in result[0]


def test_quantize_column_custom_out_column(_rows):
    result = list(quantize_column(_rows, "score", [0, 30], out_column="bucket"))
    assert "bucket" in result[0]


def test_quantize_column_boundary_include_lowest(_rows):
    # value == lower edge of first bin should be included when include_lowest=True
    rows = [{"v": "0"}]
    result = list(quantize_column(rows, "v", [0, 10, 20]))
    assert result[0]["v_bin"] != ""


def test_quantize_column_value_outside_edges(_rows):
    rows = [{"v": "99"}]
    result = list(quantize_column(rows, "v", [0, 10, 20]))
    assert result[0]["v_bin"] == ""


def test_quantize_column_invalid_edges_raises():
    with pytest.raises(ValueError, match="at least 2"):
        list(quantize_column([], "v", [5]))


def test_quantize_column_labels_mismatch_raises():
    with pytest.raises(ValueError, match="labels length"):
        list(quantize_column([], "v", [0, 10, 20], labels=["only_one"]))


def test_equal_width_quantize_basic(_rows):
    result = list(equal_width_quantize(_rows, "score", n_bins=2))
    bins = [r["score_bin"] for r in result if r["score"] != ""]
    assert all(b != "" for b in bins)


def test_equal_width_quantize_all_empty():
    rows = [{"v": ""}, {"v": ""}]
    result = list(equal_width_quantize(rows, "v", n_bins=3))
    assert all(r["v_bin"] == "" for r in result)


def test_equal_width_quantize_single_value():
    rows = [{"v": "7"}, {"v": "7"}]
    result = list(equal_width_quantize(rows, "v", n_bins=2))
    assert all(r["v_bin"] != "" for r in result)


def test_equal_width_quantize_invalid_bins_raises():
    with pytest.raises(ValueError, match="n_bins"):
        list(equal_width_quantize([], "v", n_bins=0))
