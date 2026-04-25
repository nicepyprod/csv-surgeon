"""TF-IDF scoring utilities for text columns in CSV rows."""
from __future__ import annotations

import math
import re
from collections import Counter
from typing import Dict, Iterable, Iterator, List, Optional


def _tokenize(text: str) -> List[str]:
    """Lowercase and split on non-alphanumeric characters."""
    return re.findall(r"[a-z0-9]+", text.lower())


def _idf(doc_count: int, df: int) -> float:
    """Smooth inverse document frequency."""
    return math.log((1 + doc_count) / (1 + df)) + 1.0


def build_idf(
    rows: Iterable[Dict[str, str]],
    column: str,
) -> Dict[str, float]:
    """Compute IDF weights from a corpus of rows.

    Returns a mapping of term -> IDF score.
    """
    doc_count = 0
    df: Counter = Counter()
    for row in rows:
        text = row.get(column, "")
        tokens = set(_tokenize(text))
        if tokens:
            df.update(tokens)
        doc_count += 1
    return {term: _idf(doc_count, freq) for term, freq in df.items()}


def tfidf_score(
    text: str,
    idf: Dict[str, float],
) -> Dict[str, float]:
    """Compute TF-IDF scores for all terms in *text* given pre-built IDF."""
    tokens = _tokenize(text)
    if not tokens:
        return {}
    tf = Counter(tokens)
    total = len(tokens)
    return {term: (count / total) * idf.get(term, 1.0) for term, count in tf.items()}


def top_terms(
    text: str,
    idf: Dict[str, float],
    n: int = 5,
) -> List[str]:
    """Return the top-n terms by TF-IDF score for a single document."""
    scores = tfidf_score(text, idf)
    return [t for t, _ in sorted(scores.items(), key=lambda x: x[1], reverse=True)[:n]]


def add_tfidf_column(
    rows: Iterable[Dict[str, str]],
    column: str,
    idf: Dict[str, float],
    out_column: Optional[str] = None,
    n: int = 5,
    sep: str = "|",
) -> Iterator[Dict[str, str]]:
    """Yield rows with a new column containing the top-n TF-IDF terms.

    Parameters
    ----------
    rows:       input row dicts
    column:     source text column
    idf:        pre-built IDF mapping (from :func:`build_idf`)
    out_column: name for the new column (default: ``<column>_tfidf``)
    n:          number of top terms to include
    sep:        separator used to join terms in the output cell
    """
    out = out_column or f"{column}_tfidf"
    for row in rows:
        new_row = dict(row)
        text = row.get(column, "")
        terms = top_terms(text, idf, n=n)
        new_row[out] = sep.join(terms)
        yield new_row
