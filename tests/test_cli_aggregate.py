import io
import csv
import textwrap
import pytest
from types import SimpleNamespace
from csv_surgeon.cli_aggregate import cmd_aggregate


@pytest.fixture
def sample_csv(tmp_path):
    p = tmp_path / "data.csv"
    p.write_text(textwrap.dedent("""\
        dept,name,salary
        eng,alice,90000
        eng,bob,80000
        hr,carol,70000
        hr,dave,
        eng,eve,95000
    """))
    return str(p)


def NS(input_file, group_by, column, func="sum", delimiter=","):
    return SimpleNamespace(
        input=input_file,
        group_by=group_by,
        column=column,
        func=func,
        delimiter=delimiter,
    )


def _run(capsys, ns):
    cmd_aggregate(ns)
    captured = capsys.readouterr().out
    reader = csv.DictReader(io.StringIO(captured))
    return {r[list(r.keys())[0]]: r for r in reader}


def test_sum_by_dept(sample_csv, capsys):
    result = _run(capsys, NS(sample_csv, ["dept"], "salary", "sum"))
    assert float(result["eng"]["sum_salary"]) == 265000.0
    assert float(result["hr"]["sum_salary"]) == 70000.0


def test_count_by_dept(sample_csv, capsys):
    result = _run(capsys, NS(sample_csv, ["dept"], "salary", "count"))
    assert result["eng"]["count_salary"] == "3"
    assert result["hr"]["count_salary"] == "1"


def test_mean_by_dept(sample_csv, capsys):
    result = _run(capsys, NS(sample_csv, ["dept"], "salary", "mean"))
    assert float(result["eng"]["mean_salary"]) == pytest.approx(88333.333, rel=1e-3)


def test_max_by_dept(sample_csv, capsys):
    result = _run(capsys, NS(sample_csv, ["dept"], "salary", "max"))
    assert float(result["eng"]["max_salary"]) == 95000.0
