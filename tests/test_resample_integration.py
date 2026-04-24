"""Integration tests: resample wired into the full CLI parser."""
import csv
import io
import sys
import pytest

from csv_surgeon.cli_resample import register_resample_parser, cmd_resample


@pytest.fixture()
def weekly_csv(tmp_path):
    p = tmp_path / "weekly.csv"
    lines = [
        "ts,revenue",
        "2024-03-04,100",  # week 10
        "2024-03-06,200",  # week 10
        "2024-03-11,50",   # week 11
        "2024-03-18,75",   # week 12
        "2024-03-19,25",   # week 12
    ]
    p.write_text("\n".join(lines) + "\n")
    return str(p)


def test_resample_by_week_count(weekly_csv, capsys):
    import argparse
    ns = argparse.Namespace(
        input=weekly_csv, date_col="ts", period="week",
        agg_col=None, agg_func="count", date_fmt="",
        out_col="value", delimiter=",", output=None,
    )
    cmd_resample(ns)
    out = capsys.readouterr().out
    rows = list(csv.DictReader(io.StringIO(out)))
    assert len(rows) == 3
    counts = [r["value"] for r in rows]
    assert counts == ["2", "1", "2"]


def test_resample_by_week_sum(weekly_csv, capsys):
    import argparse
    ns = argparse.Namespace(
        input=weekly_csv, date_col="ts", period="week",
        agg_col="revenue", agg_func="sum", date_fmt="",
        out_col="total", delimiter=",", output=None,
    )
    cmd_resample(ns)
    out = capsys.readouterr().out
    rows = list(csv.DictReader(io.StringIO(out)))
    assert rows[0]["total"] == "300.0"
    assert rows[1]["total"] == "50.0"
    assert rows[2]["total"] == "100.0"


def test_resample_custom_date_fmt(tmp_path, capsys):
    import argparse
    p = tmp_path / "us.csv"
    p.write_text("date,val\n01/15/2024,10\n01/20/2024,20\n02/01/2024,5\n")
    ns = argparse.Namespace(
        input=str(p), date_col="date", period="month",
        agg_col="val", agg_func="sum", date_fmt="%m/%d/%Y",
        out_col="value", delimiter=",", output=None,
    )
    cmd_resample(ns)
    out = capsys.readouterr().out
    rows = list(csv.DictReader(io.StringIO(out)))
    assert len(rows) == 2
    assert rows[0]["value"] == "30.0"
    assert rows[1]["value"] == "5.0"
