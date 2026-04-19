"""Tests for csv_surgeon.cli_outlier."""
import csv
import io
import textwrap
from pathlib import Path
from types import SimpleNamespace

import pytest

from csv_surgeon.cli_outlier import cmd_outlier


@pytest.fixture()
def sample_csv(tmp_path: Path) -> Path:
    p = tmp_path / "data.csv"
    p.write_text(
        textwrap.dedent("""\
        id,val
        1,1
        2,2
        3,3
        4,4
        5,5
        6,6
        7,7
        8,8
        9,9
        10,100
        """)
    )
    return p


def NS(input_path, output_path, **kw):
    return SimpleNamespace(
        input=str(input_path),
        output=str(output_path),
        column="val",
        mode=kw.get("mode", "remove"),
        out_column=kw.get("out_column", ""),
        flag_true=kw.get("flag_true", "1"),
        flag_false=kw.get("flag_false", "0"),
        delimiter=",",
    )


def _read(path: Path):
    return list(csv.DictReader(path.read_text().splitlines()))


def test_remove_mode(sample_csv, tmp_path):
    out = tmp_path / "out.csv"
    cmd_outlier(NS(sample_csv, out, mode="remove"))
    rows = _read(out)
    vals = [r["val"] for r in rows]
    assert "100" not in vals
    assert len(rows) == 9


def test_keep_mode(sample_csv, tmp_path):
    out = tmp_path / "out.csv"
    cmd_outlier(NS(sample_csv, out, mode="keep"))
    rows = _read(out)
    assert len(rows) == 1
    assert rows[0]["val"] == "100"


def test_flag_mode(sample_csv, tmp_path):
    out = tmp_path / "out.csv"
    cmd_outlier(NS(sample_csv, out, mode="flag"))
    rows = _read(out)
    assert len(rows) == 10
    assert "val_iqr_outlier" in rows[0]
    flagged = [r for r in rows if r["val_iqr_outlier"] == "1"]
    assert len(flagged) == 1
    assert flagged[0]["val"] == "100"
