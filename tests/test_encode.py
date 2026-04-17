"""Tests for csv_surgeon.encode."""
import base64
import pytest
from csv_surgeon.encode import encode_columns, decode_columns


def _rows():
    return [
        {"id": "1", "name": "Alice", "city": "Rome"},
        {"id": "2", "name": "Bob", "city": ""},
        {"id": "3", "name": "Carol", "city": "Paris"},
    ]


def test_encode_base64_single_column():
    result = list(encode_columns(_rows(), ["name"]))
    assert result[0]["name"] == base64.b64encode(b"Alice").decode()
    assert result[0]["id"] == "1"  # untouched


def test_encode_base64_multiple_columns():
    result = list(encode_columns(_rows(), ["name", "city"]))
    assert result[0]["city"] == base64.b64encode(b"Rome").decode()
    # empty value left untouched
    assert result[1]["city"] == ""


def test_decode_base64_roundtrip():
    encoded = list(encode_columns(_rows(), ["name", "city"]))
    decoded = list(decode_columns(encoded, ["name", "city"]))
    orig = _rows()
    for d, o in zip(decoded, orig):
        assert d["name"] == o["name"]
        assert d["city"] == o["city"]


def test_encode_upper():
    result = list(encode_columns(_rows(), ["name"], encoding="upper"))
    assert result[0]["name"] == "ALICE"


def test_encode_reverse():
    result = list(encode_columns(_rows(), ["name"], encoding="reverse"))
    assert result[0]["name"] == "ecilA"


def test_decode_reverse_roundtrip():
    encoded = list(encode_columns(_rows(), ["name"], encoding="reverse"))
    decoded = list(decode_columns(encoded, ["name"], encoding="reverse"))
    assert decoded[0]["name"] == "Alice"


def test_unknown_encoding_raises():
    with pytest.raises(ValueError, match="Unknown encoding"):
        list(encode_columns(_rows(), ["name"], encoding="rot13"))


def test_unknown_column_passthrough():
    result = list(encode_columns(_rows(), ["nonexistent"]))
    assert result[0] == _rows()[0]
