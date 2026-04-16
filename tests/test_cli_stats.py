"""Tests for cli_stats sub-command."""
import argparse
import json
import io
import pytest
from pathlib import Path
from csv_surgeon.cli_stats import cmd_stats


@pytest.fixture
def sample_csv(tmp_path):
    p = tmp_path / "data.csv"
    p.write_text("name,score,age\nalice,90,30\nbob,80,\ncarol,70,25\ndave,,40\neve,100,35\n")
    return str(p)


def NS(**kwargs):
    defaults = {"delimiter": ",", "format": "table"}
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


def test_stats_table_output(sample_csv, capsys):
    cmd_stats(NS(input=sample_csv, columns="score"))
    out = capsys.readouterr().out
    assert "score" in out
    assert "count" in out


def test_stats_json_output(sample_csv, capsys):
    cmd_stats(NS(input=sample_csv, columns="score", format="json"))
    out = capsys.readouterr().out
    data = json.loads(out)
    assert len(data) == 1
    assert data[0]["column"] == "score"
    assert data[0]["count"] == 4
    assert data[0]["null_count"] == 1


def test_stats_multi_column_json(sample_csv, capsys):
    cmd_stats(NS(input=sample_csv, columns="score,age", format="json"))
    out = capsys.readouterr().out
    data = json.loads(out)
    assert len(data) == 2
    cols = {r["column"] for r in data}
    assert cols == {"score", "age"}


def test_stats_null_column_json(sample_csv, capsys):
    cmd_stats(NS(input=sample_csv, columns="age", format="json"))
    out = capsys.readouterr().out
    data = json.loads(out)
    age = data[0]
    assert age["null_count"] == 1
    assert age["min"] == 25.0
    assert age["max"] == 40.0


def test_stats_mean_stddev(sample_csv, capsys):
    cmd_stats(NS(input=sample_csv, columns="score", format="json"))
    out = capsys.readouterr().out
    data = json.loads(out)
    assert data[0]["mean"] == pytest.approx(85.0)
    assert data[0]["stddev"] > 0
