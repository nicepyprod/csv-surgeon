import argparse
import csv
import io
import os
import pytest
from unittest.mock import patch
from csv_surgeon.cli_join import cmd_join, register_join_parser


@pytest.fixture
def left_csv(tmp_path):
    p = tmp_path / "left.csv"
    p.write_text("id,name\n1,Alice\n2,Bob\n3,Carol\n")
    return str(p)


@pytest.fixture
def right_csv(tmp_path):
    p = tmp_path / "right.csv"
    p.write_text("id,dept\n1,Eng\n2,HR\n")
    return str(p)


def NS(left, right, key="id", how="inner", right_key=None, delimiter=","):
    return argparse.Namespace(
        left=left, right=right, key=key, how=how,
        right_key=right_key, delimiter=delimiter
    )


def _run(ns):
    buf = io.StringIO()
    with patch("sys.stdout", buf):
        cmd_join(ns)
    buf.seek(0)
    return list(csv.DictReader(buf))


def test_inner_join_cli(left_csv, right_csv):
    rows = _run(NS(left_csv, right_csv))
    assert len(rows) == 2
    names = {r["name"] for r in rows}
    assert names == {"Alice", "Bob"}


def test_left_join_cli(left_csv, right_csv):
    rows = _run(NS(left_csv, right_csv, how="left"))
    names = {r["name"] for r in rows}
    assert "Carol" in names


def test_register_join_parser():
    parser = argparse.ArgumentParser()
    subs = parser.add_subparsers()
    register_join_parser(subs)
    args = parser.parse_args(["join", "l.csv", "r.csv", "-k", "id"])
    assert args.key == "id"
    assert args.how == "inner"
