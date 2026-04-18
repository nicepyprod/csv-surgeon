import csv
import io
import sys
import pytest
from types import SimpleNamespace
from csv_surgeon.cli_crossjoin import cmd_crossjoin, cmd_semijoin, register_crossjoin_parser


@pytest.fixture
def left_csv(tmp_path):
    p = tmp_path / "left.csv"
    p.write_text("id,name\n1,Alice\n2,Bob\n")
    return str(p)


@pytest.fixture
def right_csv(tmp_path):
    p = tmp_path / "right.csv"
    p.write_text("id,score\n1,90\n3,70\n")
    return str(p)


def _capture(func, args, capsys):
    func(args)
    return capsys.readouterr().out


def test_crossjoin_row_count(left_csv, right_csv, capsys):
    args = SimpleNamespace(left=left_csv, right=right_csv,
                           left_prefix="l_", right_prefix="r_")
    out = _capture(cmd_crossjoin, args, capsys)
    rows = list(csv.DictReader(io.StringIO(out)))
    assert len(rows) == 4


def test_crossjoin_prefixes(left_csv, right_csv, capsys):
    args = SimpleNamespace(left=left_csv, right=right_csv,
                           left_prefix="l_", right_prefix="r_")
    out = _capture(cmd_crossjoin, args, capsys)
    rows = list(csv.DictReader(io.StringIO(out)))
    assert "l_name" in rows[0]
    assert "r_score" in rows[0]


def test_semijoin_keeps_matching(left_csv, right_csv, capsys):
    args = SimpleNamespace(left=left_csv, right=right_csv,
                           key="id", right_key="", anti=False)
    out = _capture(cmd_semijoin, args, capsys)
    rows = list(csv.DictReader(io.StringIO(out)))
    assert len(rows) == 1
    assert rows[0]["name"] == "Alice"


def test_antijoin_excludes_matching(left_csv, right_csv, capsys):
    args = SimpleNamespace(left=left_csv, right=right_csv,
                           key="id", right_key="", anti=True)
    out = _capture(cmd_semijoin, args, capsys)
    rows = list(csv.DictReader(io.StringIO(out)))
    assert len(rows) == 1
    assert rows[0]["name"] == "Bob"


def test_register_crossjoin_parser():
    import argparse
    p = argparse.ArgumentParser()
    sub = p.add_subparsers()
    register_crossjoin_parser(sub)
    args = p.parse_args(["crossjoin", "a.csv", "b.csv"])
    assert args.left == "a.csv"
    assert args.left_prefix == "l_"
