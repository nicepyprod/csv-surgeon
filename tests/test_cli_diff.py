import csv
import io
import json
import pytest
from pathlib import Path
from types import SimpleNamespace
from csv_surgeon.cli_diff import cmd_diff


@pytest.fixture
def left_csv(tmp_path):
    p = tmp_path / "left.csv"
    p.write_text("id,name,score\n1,Alice,90\n2,Bob,80\n3,Carol,70\n")
    return str(p)


@pytest.fixture
def right_csv(tmp_path):
    p = tmp_path / "right.csv"
    p.write_text("id,name,score\n1,Alice,95\n2,Bob,80\n4,Dave,60\n")
    return str(p)


def NS(left, right, key="id", summary=False, json_out=False):
    return SimpleNamespace(
        left=left, right=right, key=key,
        delimiter=",", summary=summary, json=json_out
    )


def _run(ns, capsys):
    cmd_diff(ns)
    return capsys.readouterr().out


def test_diff_csv_output(left_csv, right_csv, capsys):
    out = _run(NS(left_csv, right_csv), capsys)
    reader = csv.DictReader(io.StringIO(out))
    rows = list(reader)
    diffs = {r["_diff"] for r in rows}
    assert "added" in diffs
    assert "removed" in diffs
    assert "modified" in diffs


def test_diff_summary_text(left_csv, right_csv, capsys):
    out = _run(NS(left_csv, right_csv, summary=True), capsys)
    assert "added: 1" in out
    assert "removed: 1" in out
    assert "modified: 1" in out


def test_diff_summary_json(left_csv, right_csv, capsys):
    out = _run(NS(left_csv, right_csv, summary=True, json_out=True), capsys)
    data = json.loads(out)
    assert data["added"] == 1
    assert data["removed"] == 1
    assert data["unchanged"] == 1


def test_diff_identical_files_no_output(left_csv, capsys):
    out = _run(NS(left_csv, left_csv), capsys)
    assert out.strip() == ""
