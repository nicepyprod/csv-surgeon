"""Tests for csv_surgeon.writer module."""

import csv
import pytest
from pathlib import Path

from csv_surgeon.writer import transform_inplace, write_rows


@pytest.fixture()
def sample_csv(tmp_path: Path) -> Path:
    path = tmp_path / "data.csv"
    rows = [
        ["id", "name", "score"],
        ["1", "Alice", "95"],
        ["2", "Bob", "82"],
    ]
    with path.open("w", newline="") as fh:
        csv.writer(fh).writerows(rows)
    return path


def test_write_rows_creates_file(tmp_path: Path):
    out = tmp_path / "out.csv"
    write_rows(out, [["x", "y"], ["1", "2"]])
    rows = list(csv.reader(out.open(newline="")))
    assert rows == [["x", "y"], ["1", "2"]]


def test_write_rows_overwrites(tmp_path: Path):
    out = tmp_path / "out.csv"
    write_rows(out, [["a", "b"]])
    write_rows(out, [["c", "d"]])
    rows = list(csv.reader(out.open(newline="")))
    assert rows == [["c", "d"]]


def test_transform_inplace_uppercase(sample_csv: Path):
    def upper(row):
        return [cell.upper() for cell in row]

    count = transform_inplace(sample_csv, upper)
    assert count == 3
    rows = list(csv.reader(sample_csv.open(newline="")))
    assert rows[0] == ["ID", "NAME", "SCORE"]
    assert rows[1] == ["1", "ALICE", "95"]


def test_transform_inplace_drop_rows(sample_csv: Path):
    def drop_bob(row):
        if "Bob" in row:
            return None
        return row

    count = transform_inplace(sample_csv, drop_bob)
    assert count == 2
    rows = list(csv.reader(sample_csv.open(newline="")))
    names = [r[1] for r in rows]
    assert "Bob" not in names


def test_transform_inplace_original_preserved_on_error(sample_csv: Path):
    original = sample_csv.read_text(encoding="utf-8")

    def bad_transform(row):
        raise RuntimeError("boom")

    with pytest.raises(RuntimeError):
        transform_inplace(sample_csv, bad_transform)

    assert sample_csv.read_text(encoding="utf-8") == original
