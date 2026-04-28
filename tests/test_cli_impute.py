"""CLI tests for the impute sub-command."""
from __future__ import annotations

import argparse
import csv
import io
import sys
import textwrap
from pathlib import Path

import pytest

from csv_surgeon.cli_impute import cmd_impute, register_impute_parser


@pytest.fixture()
def sample_csv(tmp_path: Path) -> Path:
    p = tmp_path / "data.csv"
    p.write_text(textwrap.dedent("""\
        name,score
        Alice,10
        Bob,
        Carol,20
        Dave,
        Eve,30
    """))
    return p


def NS(**kwargs) -> argparse.Namespace:
    defaults = dict(column="score", strategy="mean", value="", out_column="", output="")
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


def _run(ns: argparse.Namespace, capsys) -> list[dict]:
    cmd_impute(ns)
    captured = capsys.readouterr().out
    reader = csv.DictReader(io.StringIO(captured))
    return list(reader)


def test_impute_mean_stdout(sample_csv, capsys):
    rows = _run(NS(input=str(sample_csv)), capsys)
    filled = [r["score"] for r in rows if r["name"] in ("Bob", "Dave")]
    assert all(f == "20.0" for f in filled)


def test_impute_constant_stdout(sample_csv, capsys):
    rows = _run(NS(input=str(sample_csv), strategy="constant", value="-1"), capsys)
    assert rows[1]["score"] == "-1"


def test_impute_median_stdout(sample_csv, capsys):
    rows = _run(NS(input=str(sample_csv), strategy="median"), capsys)
    assert rows[1]["score"] == "20"


def test_impute_mode_stdout(sample_csv, capsys):
    rows = _run(NS(input=str(sample_csv), strategy="mode"), capsys)
    # mode of 10,20,30 — all equal frequency; any one of them is acceptable
    assert rows[1]["score"] != ""


def test_impute_to_output_file(sample_csv, tmp_path):
    out = tmp_path / "out.csv"
    ns = NS(input=str(sample_csv), strategy="constant", value="0", output=str(out))
    cmd_impute(ns)
    rows = list(csv.DictReader(out.open()))
    assert rows[1]["score"] == "0"


def test_register_impute_parser():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers()
    register_impute_parser(sub)
    args = parser.parse_args(["impute", "data.csv", "--column", "x", "--strategy", "median"])
    assert args.strategy == "median"
    assert args.column == "x"
