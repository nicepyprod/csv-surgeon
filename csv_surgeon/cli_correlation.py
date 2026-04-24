"""CLI sub-command: correlation — print Pearson correlation matrix."""
from __future__ import annotations

import argparse
import csv
import json
import sys
from typing import List

from csv_surgeon.reader import stream_rows
from csv_surgeon.correlation import correlation_rows, correlation_matrix


def cmd_correlation(args: argparse.Namespace) -> None:
    rows = list(stream_rows(args.input, delimiter=args.delimiter))
    columns: List[str] = (
        [c.strip() for c in args.columns.split(",")] if args.columns else []
    )
    if not columns:
        print("error: --columns is required", file=sys.stderr)
        sys.exit(1)

    if args.format == "json":
        matrix = correlation_matrix(rows, columns)
        out = {}
        for col_a in columns:
            out[col_a] = {}
            for col_b in columns:
                val = matrix.get((col_a, col_b))
                out[col_a][col_b] = None if val is None else round(val, 6)
        print(json.dumps(out, indent=2))
        return

    # default: CSV table
    header = ["column"] + columns
    writer = csv.DictWriter(
        sys.stdout, fieldnames=header, lineterminator="\n", extrasaction="ignore"
    )
    writer.writeheader()
    for row in correlation_rows(rows, columns):
        writer.writerow(row)


def register_correlation_parser(sub: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    p = sub.add_parser("correlation", help="Compute Pearson correlation matrix")
    p.add_argument("input", help="Input CSV file")
    p.add_argument(
        "--columns", required=True, help="Comma-separated list of numeric columns"
    )
    p.add_argument("--delimiter", default=",", help="Field delimiter (default: ,)")
    p.add_argument(
        "--format",
        choices=["csv", "json"],
        default="csv",
        help="Output format (default: csv)",
    )
    p.set_defaults(func=cmd_correlation)
