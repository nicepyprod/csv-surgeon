"""Integration tests: entropy_column streamed through writer."""
from __future__ import annotations

import csv
import io
import textwrap
from pathlib import Path

import pytest

from csv_surgeon.entropy import entropy_column, shannon_entropy
from csv_surgeon.reader import stream_rows
from csv_surgeon.writer import write_rows


@pytest.fixture()
def csv_path(tmp_path: Path) -> Path:
    p = tmp_path / "sales.csv"
    p.write_text(
        textwrap.dedent("""\
            product,region,revenue
            widget,north,100
            gadget,south,200
            widget,north,150
            gadget,south,250
            widget,east,90
        """)
    )
    return p


def test_entropy_column_written_to_file(tmp_path, csv_path):
    out_path = tmp_path / "out.csv"
    rows = stream_rows(str(csv_path))
    annotated = entropy_column(rows, "region")
    write_rows(str(out_path), annotated)

    result = list(stream_rows(str(out_path)))
    assert "region_entropy" in result[0]


def test_entropy_column_same_value_all_rows(tmp_path, csv_path):
    out_path = tmp_path / "out.csv"
    rows = stream_rows(str(csv_path))
    annotated = list(entropy_column(rows, "region"))
    write_rows(str(out_path), iter(annotated))

    values = {r["region_entropy"] for r in annotated}
    assert len(values) == 1, "All rows must share the same entropy value"


def test_entropy_column_value_reasonable(csv_path):
    rows = stream_rows(str(csv_path))
    annotated = list(entropy_column(rows, "region"))
    h = float(annotated[0]["region_entropy"])
    # 3 distinct regions out of 5 rows → entropy between 1 and 2 bits
    assert 1.0 < h < 2.0


def test_entropy_preserves_existing_columns(csv_path):
    rows = stream_rows(str(csv_path))
    annotated = list(entropy_column(rows, "product"))
    assert "revenue" in annotated[0]
    assert "product" in annotated[0]


def test_shannon_entropy_skips_empty_strings():
    vals = ["a", "", "b", "", "a"]
    h = shannon_entropy(vals)
    # Only 'a' and 'b' count: 2 values, 2/3 and 1/3 distribution
    assert h is not None
    import math
    expected = -(2 / 3 * math.log2(2 / 3) + 1 / 3 * math.log2(1 / 3))
    assert abs(h - expected) < 1e-9
