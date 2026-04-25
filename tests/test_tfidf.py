"""Tests for csv_surgeon.tfidf."""
from __future__ import annotations

import pytest

from csv_surgeon.tfidf import (
    _tokenize,
    add_tfidf_column,
    build_idf,
    tfidf_score,
    top_terms,
)


@pytest.fixture()
def corpus():
    return [
        {"id": "1", "text": "the quick brown fox"},
        {"id": "2", "text": "the fox jumped over the lazy dog"},
        {"id": "3", "text": "a quick brown dog"},
    ]


def test_tokenize_lowercases_and_splits():
    assert _tokenize("Hello World!") == ["hello", "world"]


def test_tokenize_empty_string():
    assert _tokenize("") == []


def test_build_idf_returns_all_terms(corpus):
    idf = build_idf(corpus, "text")
    assert "fox" in idf
    assert "quick" in idf
    assert "the" in idf


def test_build_idf_common_term_lower_score(corpus):
    idf = build_idf(corpus, "text")
    # "the" appears in 2/3 docs; "jumped" in 1/3 — jumped should score higher
    assert idf["jumped"] > idf["the"]


def test_build_idf_missing_column_graceful():
    rows = [{"other": "hello"}, {"other": "world"}]
    idf = build_idf(rows, "text")
    assert idf == {}


def test_tfidf_score_empty_text(corpus):
    idf = build_idf(corpus, "text")
    assert tfidf_score("", idf) == {}


def test_tfidf_score_returns_positive_values(corpus):
    idf = build_idf(corpus, "text")
    scores = tfidf_score("quick brown fox", idf)
    assert all(v > 0 for v in scores.values())


def test_tfidf_score_repeated_term_higher(corpus):
    idf = build_idf(corpus, "text")
    scores = tfidf_score("fox fox fox dog", idf)
    assert scores["fox"] > scores["dog"]


def test_top_terms_length(corpus):
    idf = build_idf(corpus, "text")
    terms = top_terms("quick brown fox", idf, n=2)
    assert len(terms) == 2


def test_top_terms_empty_text(corpus):
    idf = build_idf(corpus, "text")
    assert top_terms("", idf) == []


def test_add_tfidf_column_adds_new_key(corpus):
    idf = build_idf(corpus, "text")
    result = list(add_tfidf_column(corpus, "text", idf, n=3))
    assert all("text_tfidf" in row for row in result)


def test_add_tfidf_column_custom_out(corpus):
    idf = build_idf(corpus, "text")
    result = list(add_tfidf_column(corpus, "text", idf, out_column="keywords", n=2))
    assert all("keywords" in row for row in result)


def test_add_tfidf_column_sep(corpus):
    idf = build_idf(corpus, "text")
    result = list(add_tfidf_column(corpus, "text", idf, n=2, sep=","))
    for row in result:
        val = row["text_tfidf"]
        if val:
            assert "|" not in val


def test_add_tfidf_column_does_not_mutate(corpus):
    original_texts = [row["text"] for row in corpus]
    idf = build_idf(corpus, "text")
    list(add_tfidf_column(corpus, "text", idf))
    assert [row["text"] for row in corpus] == original_texts
