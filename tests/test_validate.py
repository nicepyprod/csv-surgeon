"""Tests for csv_surgeon.validate."""
import pytest

from csv_surgeon.validate import (
    is_numeric,
    not_empty,
    max_length,
    one_of,
    validate_rows,
)


def _rows():
    return [
        {"name": "Alice", "age": "30", "role": "admin"},
        {"name": "Bob", "age": "25", "role": "user"},
        {"name": "Carol", "age": "40", "role": "admin"},
    ]


def test_validate_rows_all_pass():
    rules = {"age": [is_numeric], "name": [not_empty]}
    result = list(validate_rows(_rows(), rules))
    assert len(result) == 3


def test_validate_rows_skip_invalid():
    bad = [{"name": "", "age": "abc", "role": "x"}, {"name": "Eve", "age": "22", "role": "user"}]
    rules = {"name": [not_empty], "age": [is_numeric]}
    result = list(validate_rows(bad, rules, skip_invalid=True))
    assert len(result) == 1
    assert result[0]["name"] == "Eve"


def test_validate_rows_raises_on_invalid():
    bad = [{"name": "", "age": "abc", "role": "x"}]
    rules = {"name": [not_empty]}
    with pytest.raises(ValueError, match="Validation failed"):
        list(validate_rows(bad, rules))


def test_is_numeric_valid():
    assert is_numeric("3.14")
    assert is_numeric("-7")
    assert is_numeric("0")


def test_is_numeric_invalid():
    assert not is_numeric("abc")
    assert not is_numeric("")
    assert not is_numeric("1,000")


def test_not_empty():
    assert not_empty("hello")
    assert not not_empty("")
    assert not not_empty("   ")


def test_max_length_pass():
    rule = max_length(5)
    assert rule("hi")
    assert rule("hello")


def test_max_length_fail():
    rule = max_length(3)
    assert not rule("toolong")


def test_one_of_pass():
    rule = one_of("admin", "user")
    assert rule("admin")
    assert rule("user")


def test_one_of_fail():
    rule = one_of("admin", "user")
    assert not rule("superuser")


def test_one_of_case_insensitive():
    rule = one_of("Admin", "User", case_sensitive=False)
    assert rule("ADMIN")
    assert rule("user")
