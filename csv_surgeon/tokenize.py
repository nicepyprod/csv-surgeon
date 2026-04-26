"""Tokenize text columns into word-count or n-gram representations."""
from __future__ import annotations

import re
from collections import Counter
from typing import Callable, Dict, Iterable, Iterator, List, Optional


def _default_tokenize(text: str) -> List[str]:
    """Lowercase, strip punctuation, split on whitespace."""
    text = text.lower()
    text = re.sub(r"[^\w\s]", "", text)
    return text.split()


def tokenize_column(
    rows: Iterable[Dict[str, str]],
    column: str,
    out_column: str = "",
    sep: str = " ",
    tokenizer: Optional[Callable[[str], List[str]]] = None,
) -> Iterator[Dict[str, str]]:
    """Replace *column* value with its whitespace-joined tokens.

    Args:
        rows: iterable of row dicts.
        column: source column to tokenize.
        out_column: destination column name; defaults to ``column``.
        sep: separator used to join tokens back into a string.
        tokenizer: custom callable; defaults to :func:`_default_tokenize`.
    """
    _tok = tokenizer or _default_tokenize
    _out = out_column or column
    for row in rows:
        new_row = dict(row)
        val = row.get(column, "")
        if val.strip():
            new_row[_out] = sep.join(_tok(val))
        else:
            new_row[_out] = ""
        yield new_row


def ngram_column(
    rows: Iterable[Dict[str, str]],
    column: str,
    n: int = 2,
    out_column: str = "",
    sep: str = "|",
    token_sep: str = " ",
    tokenizer: Optional[Callable[[str], List[str]]] = None,
) -> Iterator[Dict[str, str]]:
    """Produce character or word n-grams from *column* and store in *out_column*.

    Each n-gram is joined with *token_sep*; n-grams are separated by *sep*.
    """
    _tok = tokenizer or _default_tokenize
    _out = out_column or f"{column}_ngrams"
    for row in rows:
        new_row = dict(row)
        val = row.get(column, "")
        tokens = _tok(val) if val.strip() else []
        grams = [
            token_sep.join(tokens[i : i + n])
            for i in range(max(0, len(tokens) - n + 1))
        ]
        new_row[_out] = sep.join(grams)
        yield new_row


def word_count_column(
    rows: Iterable[Dict[str, str]],
    column: str,
    out_column: str = "",
    tokenizer: Optional[Callable[[str], List[str]]] = None,
) -> Iterator[Dict[str, str]]:
    """Add a column with the number of tokens in *column*."""
    _tok = tokenizer or _default_tokenize
    _out = out_column or f"{column}_word_count"
    for row in rows:
        new_row = dict(row)
        val = row.get(column, "")
        count = len(_tok(val)) if val.strip() else 0
        new_row[_out] = str(count)
        yield new_row


def top_tokens(
    rows: Iterable[Dict[str, str]],
    column: str,
    n: int = 10,
    tokenizer: Optional[Callable[[str], List[str]]] = None,
) -> List[tuple]:
    """Return the top-*n* tokens across all rows in *column* as (token, count) pairs."""
    _tok = tokenizer or _default_tokenize
    counter: Counter = Counter()
    for row in rows:
        val = row.get(column, "")
        if val.strip():
            counter.update(_tok(val))
    return counter.most_common(n)
