"""Tests for csv_surgeon.correlation."""
import math
import pytest
from csv_surgeon.correlation import correlation_matrix, correlation_rows, _pearson


def _rows():
    return [
        {"x": "1", "y": "2", "z": "10"},
        {"x": "2", "y": "4", "z": "8"},
        {"x": "3", "y": "6", "z": "6"},
        {"x": "4", "y": "8", "z": "4"},
        {"x": "5", "y": "10", "z": "2"},
    ]


def test_pearson_perfect_positive():
    xs = [1.0, 2.0, 3.0, 4.0, 5.0]
    ys = [2.0, 4.0, 6.0, 8.0, 10.0]
    assert abs(_pearson(xs, ys) - 1.0) < 1e-9


def test_pearson_perfect_negative():
    xs = [1.0, 2.0, 3.0]
    ys = [6.0, 4.0, 2.0]
    assert abs(_pearson(xs, ys) - (-1.0)) < 1e-9


def test_pearson_returns_none_for_constant():
    xs = [3.0, 3.0, 3.0]
    ys = [1.0, 2.0, 3.0]
    assert _pearson(xs, ys) is None


def test_pearson_too_few_points():
    assert _pearson([1.0], [2.0]) is None


def test_correlation_matrix_diagonal_is_one():
    matrix = correlation_matrix(_rows(), ["x", "y", "z"])
    assert matrix[("x", "x")] == 1.0
    assert matrix[("y", "y")] == 1.0
    assert matrix[("z", "z")] == 1.0


def test_correlation_matrix_x_y_perfect_positive():
    matrix = correlation_matrix(_rows(), ["x", "y"])
    assert abs(matrix[("x", "y")] - 1.0) < 1e-6


def test_correlation_matrix_x_z_perfect_negative():
    matrix = correlation_matrix(_rows(), ["x", "z"])
    assert abs(matrix[("x", "z")] - (-1.0)) < 1e-6


def test_correlation_matrix_is_symmetric():
    matrix = correlation_matrix(_rows(), ["x", "y", "z"])
    assert matrix[("x", "y")] == matrix[("y", "x")]
    assert matrix[("x", "z")] == matrix[("z", "x")]


def test_correlation_rows_yields_correct_keys():
    result = list(correlation_rows(_rows(), ["x", "y"]))
    assert len(result) == 2
    assert result[0]["column"] == "x"
    assert "x" in result[0]
    assert "y" in result[0]


def test_correlation_matrix_skips_non_numeric_rows():
    rows = [
        {"a": "1", "b": "2"},
        {"a": "bad", "b": "3"},
        {"a": "3", "b": "4"},
        {"a": "5", "b": "6"},
    ]
    matrix = correlation_matrix(rows, ["a", "b"])
    # Should still produce a value based on valid rows
    assert matrix[("a", "b")] is not None
