"""Integration tests for the transform CLI sub-command."""
import csv
import io
import os
import tempfile

import pytest

from csv_surgeon.cli_transform import cmd_transform


@pytest.fixture
def sample_csv(tmp_path):
    p = tmp_path / "data.csv"
    p.write_text("name,age,city\nalice,30,berlin\nbob,25,paris\n")
    return str(p)


def _run(args_dict, sample_csv, tmp_path):
    out = str(tmp_path / "out.csv")

    class NS:
        pass

    ns = NS()
    ns.__dict__.update(
        {"input": sample_csv, "output": out, "delimiter": ",", "upper": None,
         "lower": None, "strip": False, "rename": None}
    )
    ns.__dict__.update(args_dict)
    cmd_transform(ns)
    with open(out, newline="") as f:
        return list(csv.DictReader(f))


def test_transform_upper(sample_csv, tmp_path):
    rows = _run({"upper": ["name"]}, sample_csv, tmp_path)
    assert rows[0]["name"] == "ALICE"
    assert rows[1]["name"] == "BOB"
    assert rows[0]["age"] == "30"


def test_transform_lower(sample_csv, tmp_path):
    rows = _run({"upper": ["city"], "lower": ["city"]}, sample_csv, tmp_path)
    # lower applied after upper via separate passes — city ends lowercase
    assert rows[0]["city"] == "berlin"


def test_transform_strip(tmp_path):
    p = tmp_path / "dirty.csv"
    p.write_text("name,age\n  alice ,  30\n")
    rows = _run({"input": str(p), "strip": True}, str(p), tmp_path)
    assert rows[0]["name"] == "alice"
    assert rows[0]["age"] == "30"


def test_transform_rename(sample_csv, tmp_path):
    rows = _run({"rename": ["name=full_name"]}, sample_csv, tmp_path)
    assert "full_name" in rows[0]
    assert "name" not in rows[0]


def test_transform_no_ops_passthrough(sample_csv, tmp_path):
    rows = _run({}, sample_csv, tmp_path)
    assert rows[0]["name"] == "alice"
    assert len(rows) == 2
