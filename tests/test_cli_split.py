"""CLI tests for split-by and split-chunk commands."""
import argparse
import csv
import textwrap
from pathlib import Path

import pytest

from csv_surgeon.cli_split import cmd_split_by, cmd_split_chunk


@pytest.fixture()
def sample_csv(tmp_path):
    p = tmp_path / "data.csv"
    p.write_text(
        textwrap.dedent("""\
            dept,name,salary
            eng,alice,90000
            hr,bob,70000
            eng,carol,95000
            hr,dave,72000
            finance,eve,80000
        """)
    )
    return str(p)


def NS(**kwargs):
    defaults = {"delimiter": ",", "max_groups": 0}
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


def test_split_by_creates_files(sample_csv, tmp_path):
    out = tmp_path / "out"
    args = NS(input=sample_csv, column="dept", outdir=str(out))
    cmd_split_by(args)
    files = {p.stem for p in out.iterdir()}
    assert files == {"eng", "hr", "finance"}


def test_split_by_file_content(sample_csv, tmp_path):
    out = tmp_path / "out"
    args = NS(input=sample_csv, column="dept", outdir=str(out))
    cmd_split_by(args)
    rows = list(csv.DictReader(open(out / "eng.csv")))
    assert len(rows) == 2
    assert {r["name"] for r in rows} == {"alice", "carol"}


def test_split_by_max_groups_raises(sample_csv, tmp_path):
    out = tmp_path / "out"
    args = NS(input=sample_csv, column="dept", outdir=str(out), max_groups=2)
    with pytest.raises(ValueError, match="max_groups"):
        cmd_split_by(args)


def test_split_chunk_creates_files(sample_csv, tmp_path):
    out = tmp_path / "chunks"
    args = NS(input=sample_csv, outdir=str(out), size=2)
    cmd_split_chunk(args)
    files = sorted(out.iterdir())
    assert len(files) == 3  # 2+2+1


def test_split_chunk_content(sample_csv, tmp_path):
    out = tmp_path / "chunks"
    args = NS(input=sample_csv, outdir=str(out), size=2)
    cmd_split_chunk(args)
    first = list(csv.DictReader(open(out / "chunk_0001.csv")))
    assert len(first) == 2
    assert first[0]["name"] == "alice"
