"""CLI-level tests for the quantize sub-command."""
import csv
import io
import types
import pytest

from csv_surgeon.cli_quantize import cmd_quantize


@pytest.fixture
def sample_csv(tmp_path):
    p = tmp_path / "data.csv"
    p.write_text("name,score\nalice,5\nbob,15\ncarol,25\ndave,\n")
    return str(p)


def NS(**kwargs):
    defaults = dict(
        edges="",
        bins=0,
        labels="",
        out_column="",
        output="",
        inplace=False,
        delimiter=",",
    )
    defaults.update(kwargs)
    return types.SimpleNamespace(**defaults)


def _read(path):
    with open(path, newline="") as f:
        return list(csv.DictReader(f))


def test_quantize_edges_labels(sample_csv, capsys):
    ns = NS(input=sample_csv, column="score", edges="0,10,20,30", labels="low,mid,high")
    cmd_quantize(ns)
    out = capsys.readouterr().out
    rows = list(csv.DictReader(io.StringIO(out)))
    assert rows[0]["score_bin"] == "low"
    assert rows[1]["score_bin"] == "mid"
    assert rows[2]["score_bin"] == "high"


def test_quantize_empty_value_gives_empty_bin(sample_csv, capsys):
    ns = NS(input=sample_csv, column="score", edges="0,10,20,30")
    cmd_quantize(ns)
    out = capsys.readouterr().out
    rows = list(csv.DictReader(io.StringIO(out)))
    dave = next(r for r in rows if r["name"] == "dave")
    assert dave["score_bin"] == ""


def test_quantize_equal_width_bins(sample_csv, capsys):
    ns = NS(input=sample_csv, column="score", bins=3)
    cmd_quantize(ns)
    out = capsys.readouterr().out
    rows = list(csv.DictReader(io.StringIO(out)))
    assert "score_bin" in rows[0]
    assert all(r["score_bin"] != "" for r in rows if r["score"] != "")


def test_quantize_custom_out_column(sample_csv, capsys):
    ns = NS(input=sample_csv, column="score", edges="0,30", out_column="tier")
    cmd_quantize(ns)
    out = capsys.readouterr().out
    rows = list(csv.DictReader(io.StringIO(out)))
    assert "tier" in rows[0]
