"""Integration tests: impute reads from a real file and writes back in-place."""
from __future__ import annotations

import csv
import textwrap
from pathlib import Path

import pytest

from csv_surgeon.reader import stream_rows
from csv_surgeon.writer import transform_inplace
from csv_surgeon.impute import impute_mean, impute_constant, impute_mode


@pytest.fixture()
def csv_path(tmp_path: Path) -> Path:
    p = tmp_path / "sales.csv"
    p.write_text(textwrap.dedent("""\
        product,revenue
        Widget,100
        Gadget,
        Doohickey,300
        Thingamajig,
        Whatchamacallit,200
    """))
    return p


def test_impute_mean_inplace(csv_path):
    out = csv_path.parent / "out.csv"
    transform_inplace(str(csv_path), str(out), lambda rows: impute_mean(rows, "revenue"))
    rows = list(csv.DictReader(out.open()))
    # mean of 100, 300, 200 = 200.0
    assert rows[1]["revenue"] == "200.0"
    assert rows[3]["revenue"] == "200.0"


def test_impute_constant_inplace(csv_path):
    out = csv_path.parent / "out.csv"
    transform_inplace(str(csv_path), str(out), lambda rows: impute_constant(rows, "revenue", "0"))
    rows = list(csv.DictReader(out.open()))
    assert rows[1]["revenue"] == "0"
    assert rows[3]["revenue"] == "0"


def test_impute_preserves_non_empty_values(csv_path):
    out = csv_path.parent / "out.csv"
    transform_inplace(str(csv_path), str(out), lambda rows: impute_mean(rows, "revenue"))
    rows = list(csv.DictReader(out.open()))
    assert rows[0]["revenue"] == "100"
    assert rows[2]["revenue"] == "300"


def test_impute_mode_inplace(tmp_path):
    p = tmp_path / "cats.csv"
    p.write_text("label\nA\nA\nB\n\nA\n")
    out = tmp_path / "out.csv"
    transform_inplace(str(p), str(out), lambda rows: impute_mode(rows, "label"))
    rows = list(csv.DictReader(out.open()))
    assert rows[3]["label"] == "A"


def test_impute_all_empty_column_does_not_crash(tmp_path):
    p = tmp_path / "empty.csv"
    p.write_text("x\n\n\n\n")
    out = tmp_path / "out.csv"
    transform_inplace(str(p), str(out), lambda rows: impute_mean(rows, "x"))
    rows = list(csv.DictReader(out.open()))
    assert all(r["x"] == "" for r in rows)
