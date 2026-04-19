"""Tests for csv_surgeon.typecast_detect."""
import pytest
from csv_surgeon.typecast_detect import detect_column_types, type_report


def _rows(*dicts):
    return iter(dicts)


def test_detect_int_column():
    rows = _rows({'age': '25'}, {'age': '30'}, {'age': '17'})
    result = detect_column_types(rows)
    assert result['age'] == 'int'


def test_detect_float_column():
    rows = _rows({'score': '9.5'}, {'score': '7.0'}, {'score': '.5'})
    result = detect_column_types(rows)
    assert result['score'] == 'float'


def test_detect_bool_column():
    rows = _rows({'active': 'true'}, {'active': 'false'}, {'active': 'yes'})
    result = detect_column_types(rows)
    assert result['active'] == 'bool'


def test_detect_str_column():
    rows = _rows({'name': 'Alice'}, {'name': 'Bob'})
    result = detect_column_types(rows)
    assert result['name'] == 'str'


def test_detect_all_empty():
    rows = _rows({'col': ''}, {'col': ''}, {'col': ''})
    result = detect_column_types(rows)
    assert result['col'] == 'empty'


def test_detect_mixed_prefers_majority():
    rows = _rows(
        {'x': '1'}, {'x': '2'}, {'x': '3'}, {'x': 'hello'}
    )
    result = detect_column_types(rows)
    assert result['x'] == 'int'


def test_detect_respects_sample_limit():
    rows = iter([{'v': str(i)} for i in range(1000)])
    result = detect_column_types(rows, sample=10)
    assert result['v'] == 'int'


def test_detect_multiple_columns():
    """Each column should be inferred independently."""
    rows = _rows(
        {'id': '1', 'score': '9.5', 'name': 'Alice', 'active': 'true'},
        {'id': '2', 'score': '8.0', 'name': 'Bob',   'active': 'false'},
    )
    result = detect_column_types(rows)
    assert result['id'] == 'int'
    assert result['score'] == 'float'
    assert result['name'] == 'str'
    assert result['active'] == 'bool'


def test_type_report_structure():
    rows = _rows({'a': '1', 'b': 'hello'}, {'a': '2', 'b': 'world'})
    report = type_report(rows)
    assert isinstance(report, list)
    assert all('column' in r and 'inferred_type' in r for r in report)
    cols = {r['column']: r['inferred_type'] for r in report}
    assert cols['a'] == 'int'
    assert cols['b'] == 'str'


def test_type_report_empty_input():
    rows = iter([])
    report = type_report(rows)
    assert report == []
