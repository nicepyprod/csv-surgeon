"""CLI integration tests for window-context and window-diff subcommands."""
from __future__ import annotations

import argparse
import csv
import io
import os
import tempfile

import pytest

from csv_surgeon.cli_rolling_window import cmd_window_context, cmd_window_diff, register_rolling_window_parser
from csv_surgeon.writer import write_rows


@pytest.fixture()
def sample_csv(tmp_path):
    p = tmp_path / "data.csv"
    rows = [
        {"id": "1", "score": "100"},
        {"id": "2", "score": "200"},
        {"id": "3", "score": "300"},
    ]
    write_rows(str(p), rows)
    return str(p)


def _read(path: str):
    with open(path, newline="") as fh:
        return list(csv.DictReader(fh))


def NS(**kwargs):
    return argparse.Namespace(**kwargs)


def test_window_context_cli_adds_columns(sample_csv, tmp_path):
    out = str(tmp_path / "out.csv")
    args = NS(input=sample_csv, output=out, before=1, after=1,
              prefix_before="prev_", prefix_after="next_", fill="")
    cmd_window_context(args)
    rows = _read(out)
    assert "prev_id" in rows[0]
    assert "next_id" in rows[0]


def test_window_context_cli_inplace(sample_csv):
    args = NS(input=sample_csv, output=None, before=1, after=0,
              prefix_before="prev_", prefix_after="next_", fill="")
    cmd_window_context(args)
    rows = _read(sample_csv)
    assert "prev_id" in rows[1]


def test_window_diff_cli_adds_diff_column(sample_csv, tmp_path):
    out = str(tmp_path / "diff.csv")
    args = NS(input=sample_csv, output=out, column="score", out_column=None, fill="")
    cmd_window_diff(args)
    rows = _read(out)
    assert "score_diff" in rows[0]
    assert rows[1]["score_diff"] == "100.0"


def test_window_diff_cli_custom_out_column(sample_csv, tmp_path):
    out = str(tmp_path / "diff2.csv")
    args = NS(input=sample_csv, output=out, column="score", out_column="delta", fill="")
    cmd_window_diff(args)
    rows = _read(out)
    assert "delta" in rows[0]


def test_register_rolling_window_parser():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers()
    register_rolling_window_parser(sub)
    ns = parser.parse_args(["window-diff", "data.csv", "--column", "price"])
    assert ns.column == "price"
    ns2 = parser.parse_args(["window-context", "data.csv", "--before", "2"])
    assert ns2.before == 2
