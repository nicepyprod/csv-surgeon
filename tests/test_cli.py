"""Tests for csv_surgeon.cli module."""

import csv
import os
import textwrap

import pytest

from csv_surgeon.cli import main


@pytest.fixture
def sample_csv(tmp_path):
    path = tmp_path / "input.csv"
    path.write_text(
        textwrap.dedent("""\
        name,city,score
        Alice,New York,90
        Bob,Boston,75
        Charlie,new york,
        """
        )
    )
    return str(path)


def test_filter_equals(sample_csv, tmp_path):
    out = str(tmp_path / "out.csv")
    main.__module__  # ensure importable
    import sys
    sys.argv = ["csv-surgeon", "filter", sample_csv, out, "--column", "city", "--equals", "Boston"]
    main()
    with open(out) as f:
        rows = list(csv.DictReader(f))
    assert len(rows) == 1
    assert rows[0]["name"] == "Bob"


def test_filter_contains(sample_csv, tmp_path):
    out = str(tmp_path / "out.csv")
    import sys
    sys.argv = ["csv-surgeon", "filter", sample_csv, out,
                "--column", "city", "--contains", "York"]
    main()
    with open(out) as f:
        rows = list(csv.DictReader(f))
    assert len(rows) == 1
    assert rows[0]["name"] == "Alice"


def test_filter_contains_case_insensitive(sample_csv, tmp_path):
    out = str(tmp_path / "out.csv")
    import sys
    sys.argv = ["csv-surgeon", "filter", sample_csv, out,
                "--column", "city", "--contains", "york", "--case-insensitive"]
    main()
    with open(out) as f:
        rows = list(csv.DictReader(f))
    assert len(rows) == 2


def test_filter_drop_empty(sample_csv, tmp_path):
    out = str(tmp_path / "out.csv")
    import sys
    sys.argv = ["csv-surgeon", "filter", sample_csv, out,
                "--column", "score", "--drop-empty"]
    main()
    with open(out) as f:
        rows = list(csv.DictReader(f))
    assert all(r["score"] for r in rows)
