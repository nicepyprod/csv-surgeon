"""Integration tests for cli_rename commands."""
import csv
import io
import pytest
from unittest.mock import patch
from pathlib import Path

from csv_surgeon.cli_rename import cmd_rename


@pytest.fixture
def sample_csv(tmp_path):
    p = tmp_path / "data.csv"
    p.write_text("id,name,age\n1,Alice,30\n2,Bob,25\n")
    return str(p)


def NS(subcommand, input_file, **kwargs):
    import argparse
    ns = argparse.Namespace(
        subcommand=subcommand, input=input_file, delimiter=",", **kwargs
    )
    return ns


def _capture(args):
    buf = io.StringIO()
    with patch("sys.stdout", buf):
        cmd_rename(args)
    buf.seek(0)
    return list(csv.DictReader(buf))


def test_rename_column(sample_csv):
    args = NS("rename", sample_csv, mapping=["name=full_name"])
    rows = _capture(args)
    assert "full_name" in rows[0]
    assert "name" not in rows[0]
    assert rows[0]["full_name"] == "Alice"


def test_reorder_columns(sample_csv):
    args = NS("reorder", sample_csv, columns=["name", "id"], fill="")
    rows = _capture(args)
    assert list(rows[0].keys()) == ["name", "id"]


def test_select_columns(sample_csv):
    args = NS("select", sample_csv, columns=["id", "name"])
    rows = _capture(args)
    assert "age" not in rows[0]
    assert rows[1]["name"] == "Bob"


def test_drop_columns(sample_csv):
    args = NS("drop", sample_csv, columns=["age"])
    rows = _capture(args)
    assert "age" not in rows[0]
    assert "id" in rows[0]
