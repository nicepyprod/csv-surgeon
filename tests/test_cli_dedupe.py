"""Integration tests for the dedupe CLI sub-command."""
import csv
import io
import types
import pytest
from csv_surgeon.cli_dedupe import cmd_dedupe


@pytest.fixture()
def sample_csv(tmp_path):
    p = tmp_path / "data.csv"
    p.write_text("name,city\nAlice,NY\nBob,LA\nAlice,NY\nBob,SF\nAlice,NY\n")
    return str(p)


def NS(**kwargs):
    defaults = dict(delimiter=",", keys=None, keep="first", output=None, verbose=False)
    defaults.update(kwargs)
    return types.SimpleNamespace(**defaults)


def _read(path):
    with open(path, newline="") as f:
        return list(csv.DictReader(f))


def test_dedupe_keep_first_all_columns(sample_csv):
    cmd_dedupe(NS(input=sample_csv))
    rows = _read(sample_csv)
    assert rows == [
        {"name": "Alice", "city": "NY"},
        {"name": "Bob",   "city": "LA"},
        {"name": "Bob",   "city": "SF"},
    ]


def test_dedupe_keep_first_by_key(sample_csv):
    cmd_dedupe(NS(input=sample_csv, keys="name"))
    rows = _read(sample_csv)
    assert [r["name"] for r in rows] == ["Alice", "Bob"]


def test_dedupe_keep_last_by_key(sample_csv):
    cmd_dedupe(NS(input=sample_csv, keys="name", keep="last"))
    rows = _read(sample_csv)
    assert rows == [
        {"name": "Alice", "city": "NY"},
        {"name": "Bob",   "city": "SF"},
    ]


def test_dedupe_output_separate_file(sample_csv, tmp_path):
    out = str(tmp_path / "out.csv")
    cmd_dedupe(NS(input=sample_csv, output=out))
    rows = _read(out)
    assert len(rows) == 3
    # original untouched
    assert len(_read(sample_csv)) == 5
