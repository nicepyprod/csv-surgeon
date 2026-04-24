"""Tests for csv_surgeon.entropy."""
from __future__ import annotations

import math
import pytest

from csv_surgeon.entropy import (
    entropy_column,
    mutual_information,
    shannon_entropy,
)


def _rows():
    return [
        {"name": "alice", "dept": "eng"},
        {"name": "bob", "dept": "eng"},
        {"name": "carol", "dept": "hr"},
        {"name": "dave", "dept": "hr"},
    ]


def test_shannon_entropy_uniform():
    # Four distinct values → entropy = log2(4) = 2.0
    vals = ["a", "b", "c", "d"]
    h = shannon_entropy(vals)
    assert h is not None
    assert abs(h - 2.0) < 1e-9


def test_shannon_entropy_constant():
    # Single value → entropy = 0
    h = shannon_entropy(["x", "x", "x"])
    assert h == 0.0


def test_shannon_entropy_empty_values_ignored():
    h = shannon_entropy(["", "", "a", "a"])
    assert h == 0.0


def test_shannon_entropy_all_empty_returns_none():
    assert shannon_entropy(["", ""]) is None


def test_shannon_entropy_two_equal_groups():
    h = shannon_entropy(["a", "a", "b", "b"])
    assert h is not None
    assert abs(h - 1.0) < 1e-9


def test_entropy_column_adds_field():
    rows = list(entropy_column(_rows(), "dept"))
    assert "dept_entropy" in rows[0]
    # All rows get the same value
    vals = {r["dept_entropy"] for r in rows}
    assert len(vals) == 1


def test_entropy_column_value_correct():
    rows = list(entropy_column(_rows(), "dept"))
    h = float(rows[0]["dept_entropy"])
    assert abs(h - 1.0) < 1e-4  # 50/50 split → 1 bit


def test_entropy_column_custom_out():
    rows = list(entropy_column(_rows(), "dept", out_column="h"))
    assert "h" in rows[0]
    assert "dept_entropy" not in rows[0]


def test_mutual_information_identical_columns():
    rows = [
        {"a": "x", "b": "x"},
        {"a": "y", "b": "y"},
        {"a": "x", "b": "x"},
        {"a": "y", "b": "y"},
    ]
    mi = mutual_information(rows, "a", "b")
    assert mi is not None
    assert mi > 0.99  # should be ≈ 1 bit


def test_mutual_information_independent_columns():
    # Columns are independent: MI ≈ 0
    rows = [
        {"a": "x", "b": "p"},
        {"a": "x", "b": "q"},
        {"a": "y", "b": "p"},
        {"a": "y", "b": "q"},
    ]
    mi = mutual_information(rows, "a", "b")
    assert mi is not None
    assert abs(mi) < 1e-9


def test_mutual_information_empty_returns_none():
    rows = [{"a": "", "b": ""}]
    assert mutual_information(rows, "a", "b") is None
