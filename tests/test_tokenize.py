"""Tests for csv_surgeon.tokenize."""
from __future__ import annotations

import pytest

from csv_surgeon.tokenize import (
    _default_tokenize,
    ngram_column,
    tokenize_column,
    top_tokens,
    word_count_column,
)


@pytest.fixture()
def _rows():
    return [
        {"id": "1", "text": "Hello World"},
        {"id": "2", "text": "  foo BAR baz  "},
        {"id": "3", "text": ""},
        {"id": "4", "text": "one two three four"},
    ]


# ---------------------------------------------------------------------------
# _default_tokenize
# ---------------------------------------------------------------------------

def test_default_tokenize_lowercases():
    assert _default_tokenize("Hello World") == ["hello", "world"]


def test_default_tokenize_strips_punctuation():
    assert _default_tokenize("it's great!") == ["its", "great"]


def test_default_tokenize_empty_string():
    assert _default_tokenize("") == []


# ---------------------------------------------------------------------------
# tokenize_column
# ---------------------------------------------------------------------------

def test_tokenize_column_basic(_rows):
    result = list(tokenize_column(_rows, column="text"))
    assert result[0]["text"] == "hello world"
    assert result[1]["text"] == "foo bar baz"


def test_tokenize_column_empty_value_yields_empty_string(_rows):
    result = list(tokenize_column(_rows, column="text"))
    assert result[2]["text"] == ""


def test_tokenize_column_out_column(_rows):
    result = list(tokenize_column(_rows, column="text", out_column="tokens"))
    assert "tokens" in result[0]
    assert result[0]["text"] == "Hello World"  # original unchanged
    assert result[0]["tokens"] == "hello world"


def test_tokenize_column_custom_sep(_rows):
    result = list(tokenize_column(_rows, column="text", sep="|"))
    assert result[0]["text"] == "hello|world"


def test_tokenize_column_does_not_mutate_original(_rows):
    original_text = _rows[0]["text"]
    list(tokenize_column(_rows, column="text"))
    assert _rows[0]["text"] == original_text


# ---------------------------------------------------------------------------
# ngram_column
# ---------------------------------------------------------------------------

def test_ngram_column_bigrams(_rows):
    result = list(ngram_column(_rows, column="text", n=2))
    # "Hello World" -> tokens ["hello", "world"] -> 1 bigram: "hello world"
    assert result[0]["text_ngrams"] == "hello world"


def test_ngram_column_trigrams(_rows):
    result = list(ngram_column(_rows, column="text", n=3))
    # "one two three four" -> ["one","two","three","four"] -> 2 trigrams
    grams = result[3]["text_ngrams"].split("|")
    assert len(grams) == 2
    assert grams[0] == "one two three"


def test_ngram_column_empty_value_yields_empty_string(_rows):
    result = list(ngram_column(_rows, column="text", n=2))
    assert result[2]["text_ngrams"] == ""


def test_ngram_column_out_column(_rows):
    result = list(ngram_column(_rows, column="text", n=2, out_column="bg"))
    assert "bg" in result[0]


# ---------------------------------------------------------------------------
# word_count_column
# ---------------------------------------------------------------------------

def test_word_count_column_basic(_rows):
    result = list(word_count_column(_rows, column="text"))
    assert result[0]["text_word_count"] == "2"
    assert result[1]["text_word_count"] == "3"


def test_word_count_column_empty_value(_rows):
    result = list(word_count_column(_rows, column="text"))
    assert result[2]["text_word_count"] == "0"


def test_word_count_column_custom_out(_rows):
    result = list(word_count_column(_rows, column="text", out_column="wc"))
    assert "wc" in result[0]


# ---------------------------------------------------------------------------
# top_tokens
# ---------------------------------------------------------------------------

def test_top_tokens_returns_most_common(_rows):
    # "Hello World", "foo BAR baz", "", "one two three four"
    results = top_tokens(_rows, column="text", n=5)
    tokens = [t for t, _ in results]
    # every token appears exactly once; just verify we get tokens back
    assert len(results) <= 5
    assert all(isinstance(t, str) for t, _ in results)


def test_top_tokens_n_larger_than_vocab(_rows):
    results = top_tokens(_rows, column="text", n=100)
    # 2 + 3 + 0 + 4 = 9 unique tokens
    assert len(results) <= 9
