"""CLI tests for the resample subcommand."""
import argparse
import csv
import io
import tempfile
import os
import pytest

from csv_surgeon.cli_resample import cmd_resample, register_resample_parser


@pytest.fixture()
def sample_csv(tmp_path):
    p = tmp_path / "sales.csv"
    p.write_text(
        "date,amount,dept\n"
        "2024-01-10,100,eng\n"
        "2024-01-25,200,eng\n"
        "2024-02-05,150,mkt\n"
        "2024-02-18,50,eng\n"
        "2024-03-03,300,mkt\n"
    )
    return str(p)


def NS(**kwargs):
    defaults = dict(
        period="month", agg_col=None, agg_func="count",
        date_fmt="", out_col="value", delimiter=",", output=None,
    )
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


def _run(ns, capsys):
    cmd_resample(ns)
    return capsys.readouterr().out


def test_resample_count_by_month(sample_csv, capsys):
    ns = NS(input=sample_csv, date_col="date")
    out = _run(ns, capsys)
    reader = csv.DictReader(io.StringIO(out))
    rows = list(reader)
    assert len(rows) == 3
    assert rows[0]["date"] == "2024-01"
    assert rows[0]["value"] == "2"


def test_resample_sum_to_file(sample_csv, tmp_path):
    out_path = str(tmp_path / "out.csv")
    ns = NS(input=sample_csv, date_col="date", agg_col="amount",
            agg_func="sum", output=out_path)
    cmd_resample(ns)
    reader = csv.DictReader(open(out_path))
    rows = list(reader)
    assert rows[0]["value"] == "300.0"


def test_resample_by_year(sample_csv, capsys):
    ns = NS(input=sample_csv, date_col="date", period="year")
    out = _run(ns, capsys)
    reader = csv.DictReader(io.StringIO(out))
    rows = list(reader)
    assert len(rows) == 1
    assert rows[0]["date"] == "2024"
    assert rows[0]["value"] == "5"


def test_register_resample_parser():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers()
    register_resample_parser(sub)
    args = parser.parse_args(["resample", "data.csv", "--date-col", "ts",
                               "--period", "day", "--agg-func", "mean"])
    assert args.date_col == "ts"
    assert args.period == "day"
    assert args.agg_func == "mean"
