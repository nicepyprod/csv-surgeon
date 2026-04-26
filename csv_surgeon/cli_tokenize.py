"""CLI sub-commands for tokenize operations."""
from __future__ import annotations

import argparse
import csv
import sys
from typing import List

from csv_surgeon.reader import stream_rows
from csv_surgeon.tokenize import ngram_column, tokenize_column, word_count_column
from csv_surgeon.writer import transform_inplace


def cmd_tokenize(args: argparse.Namespace) -> None:
    """Tokenize a column and write result to *out_column*."""
    rows = list(stream_rows(args.input, delimiter=args.delimiter))
    if not rows:
        return

    result = list(
        tokenize_column(
            rows,
            column=args.column,
            out_column=args.out_column or args.column,
            sep=args.sep,
        )
    )

    fieldnames = list(result[0].keys())
    writer = csv.DictWriter(
        open(args.output, "w", newline="") if args.output else sys.stdout,
        fieldnames=fieldnames,
    )
    writer.writeheader()
    writer.writerows(result)


def cmd_ngram(args: argparse.Namespace) -> None:
    """Add n-gram column derived from *column*."""
    rows = list(stream_rows(args.input, delimiter=args.delimiter))
    if not rows:
        return

    result = list(
        ngram_column(
            rows,
            column=args.column,
            n=args.n,
            out_column=args.out_column or f"{args.column}_ngrams",
            sep=args.sep,
        )
    )

    fieldnames = list(result[0].keys())
    out = open(args.output, "w", newline="") if args.output else sys.stdout
    writer = csv.DictWriter(out, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(result)


def register_tokenize_parser(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    # tokenize sub-command
    p_tok = subparsers.add_parser("tokenize", help="Tokenize a text column")
    p_tok.add_argument("input", help="Input CSV file")
    p_tok.add_argument("column", help="Column to tokenize")
    p_tok.add_argument("--out-column", default="", dest="out_column")
    p_tok.add_argument("--sep", default=" ", help="Token join separator")
    p_tok.add_argument("--output", default="", help="Output file (default: stdout)")
    p_tok.add_argument("--delimiter", default=",")
    p_tok.set_defaults(func=cmd_tokenize)

    # ngram sub-command
    p_ng = subparsers.add_parser("ngram", help="Add n-gram column from a text column")
    p_ng.add_argument("input", help="Input CSV file")
    p_ng.add_argument("column", help="Column to build n-grams from")
    p_ng.add_argument("--n", type=int, default=2, help="N-gram size")
    p_ng.add_argument("--out-column", default="", dest="out_column")
    p_ng.add_argument("--sep", default="|", help="N-gram separator")
    p_ng.add_argument("--output", default="", help="Output file (default: stdout)")
    p_ng.add_argument("--delimiter", default=",")
    p_ng.set_defaults(func=cmd_ngram)
