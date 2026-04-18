"""Tests for csv_surgeon.conditional."""
import pytest
from csv_surgeon.conditional import if_then, if_then_else_column, coalesce, map_values


def _rows():
    return [
        {"name": "Alice", "score": "90", "dept": "eng"},
        {"name": "Bob",   "score": "55", "dept": "hr"},
        {"name": "Carol", "score": "70", "dept": "eng"},
    ]


def test_if_then_sets_true_value():
    result = list(if_then(_rows(), lambda r: int(r["score"]) >= 70, "grade", "pass", "fail"))
    assert result[0]["grade"] == "pass"
    assert result[1]["grade"] == "fail"
    assert result[2]["grade"] == "pass"


def test_if_then_default_false_value_empty():
    result = list(if_then(_rows(), lambda r: r["dept"] == "eng", "flag", "yes"))
    assert result[0]["flag"] == "yes"
    assert result[1]["flag"] == ""


def test_if_then_does_not_mutate_original():
    rows = _rows()
    list(if_then(rows, lambda r: True, "new_col", "x"))
    assert "new_col" not in rows[0]


def test_if_then_else_column_case_sensitive():
    result = list(if_then_else_column(_rows(), "dept", "eng", "label", "engineer", "other"))
    assert result[0]["label"] == "engineer"
    assert result[1]["label"] == "other"


def test_if_then_else_column_case_insensitive():
    rows = [{"dept": "ENG"}, {"dept": "hr"}]
    result = list(if_then_else_column(rows, "dept", "eng", "label", "yes", "no", case_sensitive=False))
    assert result[0]["label"] == "yes"
    assert result[1]["label"] == "no"


def test_coalesce_picks_first_nonempty():
    rows = [
        {"a": "",  "b": "",  "c": "val"},
        {"a": "first", "b": "second", "c": "third"},
        {"a": "",  "b": "mid", "c": "last"},
    ]
    result = list(coalesce(rows, ["a", "b", "c"], "out"))
    assert result[0]["out"] == "val"
    assert result[1]["out"] == "first"
    assert result[2]["out"] == "mid"


def test_coalesce_all_empty_gives_empty():
    rows = [{"a": "", "b": ""}]
    result = list(coalesce(rows, ["a", "b"], "out"))
    assert result[0]["out"] == ""


def test_map_values_replaces_known():
    result = list(map_values(_rows(), "dept", {"eng": "Engineering", "hr": "Human Resources"}))
    assert result[0]["dept"] == "Engineering"
    assert result[1]["dept"] == "Human Resources"


def test_map_values_unknown_keeps_original_when_no_default():
    rows = [{"dept": "finance"}]
    result = list(map_values(rows, "dept", {"eng": "Engineering"}))
    assert result[0]["dept"] == "finance"


def test_map_values_unknown_uses_explicit_default():
    rows = [{"dept": "finance"}]
    result = list(map_values(rows, "dept", {"eng": "Engineering"}, default="Other"))
    assert result[0]["dept"] == "Other"
