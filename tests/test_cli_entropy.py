"""Tests for csv_surgeon.cli_entropy."""
from __future__ import annotations

import csv
import io
import json
import textwrap
import types
from pathlib import Path
from unittest.mock import patch

import pytest

from csv_surgeon.cli_entropy import cmd_entropy, cmd_mutual_info


@pytest.fixture()
def sample_csv(tmp_path: Path) -> Path:
    p = tmp_path / "data.csv"
    p.write_text(
        textwrap.dedent("""\
            name,dept,score
            alice,eng,10
            bob,eng,20
            carol,hr,30
            dave,hr,40
        """)
    )
    return p


def NS(**kwargs) -> types.SimpleNamespace:
    defaults = {"delimiter": ",", "format": "csv"}
    defaults.update(kwargs)
    return types.SimpleNamespace(**defaults)


def _run_entropy(capsys, sample_csv, columns, fmt="csv"):
    cmd_entropy(NS(input=str(sample_csv), columns=columns, format=fmt))
    return capsys.readouterr().out


def _run_mi(capsys, sample_csv, col_a, col_b, fmt="csv"):
    cmd_mutual_info(NS(input=str(sample_csv), col_a=col_a, col_b=col_b, format=fmt))
    return capsys.readouterr().out


def test_entropy_csv_output_has_header(capsys, sample_csv):
    out = _run_entropy(capsys, sample_csv, ["dept"])
    rows = list(csv.reader(io.StringIO(out)))
    assert rows[0] == ["column", "entropy_bits"]


def test_entropy_csv_correct_column_name(capsys, sample_csv):
    out = _run_entropy(capsys, sample_csv, ["dept"])
    rows = list(csv.reader(io.StringIO(out)))
    assert rows[1][0] == "dept"


def test_entropy_value_is_one_bit(capsys, sample_csv):
    out = _run_entropy(capsys, sample_csv, ["dept"])
    rows = list(csv.reader(io.StringIO(out)))
    assert abs(float(rows[1][1]) - 1.0) < 1e-4


def test_entropy_multiple_columns(capsys, sample_csv):
    out = _run_entropy(capsys, sample_csv, ["dept", "name"])
    rows = list(csv.reader(io.StringIO(out)))
    assert len(rows) == 3  # header + 2 data rows


def test_entropy_json_output(capsys, sample_csv):
    out = _run_entropy(capsys, sample_csv, ["dept"], fmt="json")
    data = json.loads(out)
    assert "dept" in data
    assert abs(data["dept"] - 1.0) < 1e-4


def test_mutual_info_csv_output(capsys, sample_csv):
    out = _run_mi(capsys, sample_csv, "dept", "dept")
    rows = list(csv.reader(io.StringIO(out)))
    assert rows[0] == ["col_a", "col_b", "mutual_information_bits"]
    assert float(rows[1][2]) > 0.99


def test_mutual_info_json_output(capsys, sample_csv):
    out = _run_mi(capsys, sample_csv, "dept", "dept", fmt="json")
    data = json.loads(out)
    assert data["col_a"] == "dept"
    assert data["mutual_information_bits"] is not None
