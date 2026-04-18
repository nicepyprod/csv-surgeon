import csv, io, argparse
import pytest
from csv_surgeon.cli_flatten import cmd_flatten, cmd_collapse

CSV_DATA = """id,name,tags
1,Alice,python|csv|cli
2,Bob,csv
3,Carol,
"""


@pytest.fixture
def sample_csv(tmp_path):
    p = tmp_path / "data.csv"
    p.write_text(CSV_DATA)
    return p


def NS(**kwargs):
    return argparse.Namespace(**kwargs)


def _run_flatten(csv_text: str, column: str, sep: str = "|") -> list[dict]:
    inp = io.StringIO(csv_text)
    out = io.StringIO()
    cmd_flatten(NS(input=inp, output=out, column=column, sep=sep))
    out.seek(0)
    return list(csv.DictReader(out))


def _run_collapse(csv_text: str, column: str, key: str, sep: str = "|") -> list[dict]:
    inp = io.StringIO(csv_text)
    out = io.StringIO()
    cmd_collapse(NS(input=inp, output=out, column=column, key=key, sep=sep))
    out.seek(0)
    return list(csv.DictReader(out))


def test_flatten_cli_row_count():
    rows = _run_flatten(CSV_DATA, "tags")
    assert len(rows) == 5  # 3+1+1(empty passthrough)


def test_flatten_cli_values():
    rows = _run_flatten(CSV_DATA, "tags")
    tags = [r["tags"] for r in rows]
    assert "python" in tags
    assert "cli" in tags


def test_flatten_cli_custom_sep():
    data = "id,vals\n1,a:b:c\n"
    rows = _run_flatten(data, "vals", sep=":")
    assert [r["vals"] for r in rows] == ["a", "b", "c"]


def test_collapse_cli_roundtrip():
    flat = _run_flatten(CSV_DATA, "tags")
    flat_text = "id,name,tags\n" + "\n".join(
        f"{r['id']},{r['name']},{r['tags']}" for r in flat
    ) + "\n"
    collapsed = _run_collapse(flat_text, "tags", key="id")
    by_id = {r["id"]: r for r in collapsed}
    assert by_id["1"]["tags"] == "python|csv|cli"
    assert by_id["2"]["tags"] == "csv"
