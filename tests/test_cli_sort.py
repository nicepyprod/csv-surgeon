"""Integration tests for the sort CLI sub-command."""
import csv
import io
import types
from pathlib import Path

import pytest

from csv_surgeon.cli_sort import cmd_sort


@pytest.fixture
def sample_csv(tmp_path):
    p = tmp_path / "data.csv"
    p.write_text("name,age,city\nCharlie,30,Berlin\nAlice,25,Amsterdam\nBob,35,Berlin\n")
    return str(p)


def NS(**kwargs):
    defaults = dict(delimiter=",", reverse=False, numeric=None, output=None)
    defaults.update(kwargs)
    return types.SimpleNamespace(**defaults)


def _read(path):
    with open(path, newline="") as f:
        return list(csv.DictReader(f))


def test_sort_alpha_asc(sample_csv):
    cmd_sort(NS(input=sample_csv, key=["name"]))
    rows = _read(sample_csv)
    assert [r["name"] for r in rows] == ["Alice", "Bob", "Charlie"]


def test_sort_alpha_desc(sample_csv):
    cmd_sort(NS(input=sample_csv, key=["name"], reverse=True))
    rows = _read(sample_csv)
    assert rows[0]["name"] == "Charlie"


def test_sort_numeric(sample_csv):
    cmd_sort(NS(input=sample_csv, key=["age"], numeric=["age"]))
    rows = _read(sample_csv)
    assert [r["age"] for r in rows] == ["25", "30", "35"]


def test_sort_to_output(sample_csv, tmp_path):
    out = str(tmp_path / "out.csv")
    cmd_sort(NS(input=sample_csv, key=["name"], output=out))
    rows = _read(out)
    assert rows[0]["name"] == "Alice"
    # original unchanged
    orig = _read(sample_csv)
    assert orig[0]["name"] == "Charlie"


def test_sort_multi_key(sample_csv):
    cmd_sort(NS(input=sample_csv, key=["city", "name"]))
    rows = _read(sample_csv)
    assert rows[0]["city"] == "Amsterdam"
