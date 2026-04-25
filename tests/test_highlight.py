"""Tests for csv_surgeon/highlight.py."""
from __future__ import annotations

import re
from typing import Dict, List

import pytest

from csv_surgeon.highlight import (
    highlight_rows,
    highlight_by_value,
    highlight_by_regex,
    highlight_top_n,
)

Row = Dict[str, str]


def _rows() -> List[Row]:
    return [
        {"name": "Alice", "dept": "Eng",  "score": "92"},
        {"name": "Bob",   "dept": "HR",   "score": "78"},
        {"name": "Carol", "dept": "Eng",  "score": "85"},
        {"name": "Dave",  "dept": "Sales", "score": ""},
    ]


# ── highlight_rows ────────────────────────────────────────────────────────────

def test_highlight_rows_adds_column():
    result = list(highlight_rows(_rows(), lambda r: r["dept"] == "Eng"))
    assert all("_highlight" in r for r in result)


def test_highlight_rows_true_value():
    result = list(highlight_rows(_rows(), lambda r: r["dept"] == "Eng"))
    assert result[0]["_highlight"] == "1"
    assert result[1]["_highlight"] == "0"


def test_highlight_rows_custom_marker():
    result = list(
        highlight_rows(
            _rows(),
            lambda r: r["name"] == "Bob",
            out_column="flag",
            true_value="yes",
            false_value="no",
        )
    )
    assert result[1]["flag"] == "yes"
    assert result[0]["flag"] == "no"


def test_highlight_rows_does_not_mutate_original():
    original = _rows()
    _ = list(highlight_rows(original, lambda r: True))
    assert "_highlight" not in original[0]


# ── highlight_by_value ────────────────────────────────────────────────────────

def test_highlight_by_value_exact():
    result = list(highlight_by_value(_rows(), "dept", "Eng"))
    flagged = [r["name"] for r in result if r["_highlight"] == "1"]
    assert flagged == ["Alice", "Carol"]


def test_highlight_by_value_case_insensitive():
    result = list(
        highlight_by_value(_rows(), "dept", "eng", case_sensitive=False)
    )
    flagged = [r["name"] for r in result if r["_highlight"] == "1"]
    assert flagged == ["Alice", "Carol"]


def test_highlight_by_value_no_match():
    result = list(highlight_by_value(_rows(), "dept", "Finance"))
    assert all(r["_highlight"] == "0" for r in result)


# ── highlight_by_regex ────────────────────────────────────────────────────────

def test_highlight_by_regex_basic():
    result = list(highlight_by_regex(_rows(), "name", r"^A"))
    flagged = [r["name"] for r in result if r["_highlight"] == "1"]
    assert flagged == ["Alice"]


def test_highlight_by_regex_case_insensitive_flag():
    result = list(
        highlight_by_regex(_rows(), "name", r"alice", flags=re.IGNORECASE)
    )
    flagged = [r["name"] for r in result if r["_highlight"] == "1"]
    assert flagged == ["Alice"]


def test_highlight_by_regex_no_match():
    result = list(highlight_by_regex(_rows(), "name", r"^Z"))
    assert all(r["_highlight"] == "0" for r in result)


# ── highlight_top_n ───────────────────────────────────────────────────────────

def test_highlight_top_n_basic():
    result = list(highlight_top_n(_rows(), "score", 2))
    flagged = [r["name"] for r in result if r["_highlight"] == "1"]
    assert set(flagged) == {"Alice", "Carol"}


def test_highlight_top_n_non_numeric_treated_as_lowest():
    result = list(highlight_top_n(_rows(), "score", 3))
    # Dave has empty score → should NOT be in top 3 unless n >= 4
    flagged = [r["name"] for r in result if r["_highlight"] == "1"]
    assert "Dave" not in flagged


def test_highlight_top_n_all_rows_when_n_large():
    result = list(highlight_top_n(_rows(), "score", 10))
    assert all(r["_highlight"] == "1" for r in result)
