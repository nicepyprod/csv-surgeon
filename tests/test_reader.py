"""Tests for csv_surgeon.reader module."""

import csv
import pytest
from pathlib import Path

from csv_surgeon.reader import read_header, stream_rows


@pytest.fixture()
def sample_csv(tmp_path: Path) -> Path:
    path = tmp_path / "sample.csv"
    rows = [
        ["id", "name", "score"],
        ["1", "Alice", "95"],
        ["2", "Bob", "82"],
        ["3", "Carol", "78"],
    ]
    with path.open("w", newline="") as fh:
        csv.writer(fh).writerows(rows)
    return path


def test_stream_rows_all(sample_csv: Path):
    rows = list(stream_rows(sample_csv))
    assert len(rows) == 4
    assert rows[0] == ["id", "name", "score"]


def test_stream_rows_skip_header(sample_csv: Path):
    rows = list(stream_rows(sample_csv, skip_header=True))
    assert len(rows) == 3
    assert rows[0] == ["1", "Alice", "95"]


def test_stream_rows_custom_delimiter(tmp_path: Path):
    path = tmp_path / "pipe.csv"
    path.write_text("a|b|c\n1|2|3\n", encoding="utf-8")
    rows = list(stream_rows(path, delimiter="|"))
    assert rows[0] == ["a", "b", "c"]
    assert rows[1] == ["1", "2", "3"]


def test_stream_rows_file_not_found():
    with pytest.raises(FileNotFoundError):
        list(stream_rows("/nonexistent/path.csv"))


def test_read_header(sample_csv: Path):
    header = read_header(sample_csv)
    assert header == ["id", "name", "score"]


def test_read_header_empty_file(tmp_path: Path):
    empty = tmp_path / "empty.csv"
    empty.write_text("", encoding="utf-8")
    assert read_header(empty) is None


def test_read_header_file_not_found():
    with pytest.raises(FileNotFoundError):
        read_header("/nonexistent/path.csv")
