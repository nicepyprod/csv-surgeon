"""Tests for csv_surgeon.cli_correlation."""
import argparse
import csv
import io
import json
import textwrap
from unittest.mock import patch
import pytest

from csv_surgeon.cli_correlation import cmd_correlation, register_correlation_parser


@pytest.fixture()
def sample_csv(tmp_path):
    p = tmp_path / "data.csv"
    p.write_text(
        textwrap.dedent("""\
        x,y,z
        1,2,10
        2,4,8
        3,6,6
        4,8,4
        5,10,2
        """)
    )
    return str(p)


def NS(**kwargs):
    defaults = dict(delimiter=",", columns="x,y,z", format="csv")
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


def _run(args, capsys):
    cmd_correlation(args)
    return capsys.readouterr().out


def test_csv_output_has_header(sample_csv, capsys):
    out = _run(NS(input=sample_csv), capsys)
    reader = csv.DictReader(io.StringIO(out))
    rows = list(reader)
    assert reader.fieldnames == ["column", "x", "y", "z"]
    assert len(rows) == 3


def test_csv_diagonal_is_one(sample_csv, capsys):
    out = _run(NS(input=sample_csv), capsys)
    reader = csv.DictReader(io.StringIO(out))
    for row in reader:
        col = row["column"]
        assert abs(float(row[col]) - 1.0) < 1e-5


def test_json_output_format(sample_csv, capsys):
    out = _run(NS(input=sample_csv, format="json"), capsys)
    data = json.loads(out)
    assert "x" in data
    assert "y" in data["x"]
    assert abs(data["x"]["x"] - 1.0) < 1e-5


def test_json_x_z_negative_correlation(sample_csv, capsys):
    out = _run(NS(input=sample_csv, format="json"), capsys)
    data = json.loads(out)
    assert abs(data["x"]["z"] - (-1.0)) < 1e-5


def test_missing_columns_exits(sample_csv, capsys):
    with pytest.raises(SystemExit):
        cmd_correlation(NS(input=sample_csv, columns=""))


def test_register_parser_adds_subcommand():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers()
    register_correlation_parser(sub)
    args = parser.parse_args(["correlation", "data.csv", "--columns", "a,b"])
    assert args.columns == "a,b"
    assert args.format == "csv"
