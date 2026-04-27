"""CLI sub-command: pivot-table

Usage example:
  csv-surgeon pivot-table input.csv --index region --pivot product \\
      --value revenue --aggfunc sum --output out.csv
"""
from __future__ import annotations

import argparse
import sys

from csv_surgeon.pivot_table import pivot_table
from csv_surgeon.reader import stream_rows
from csv_surgeon.writer import write_rows


def cmd_pivot_table(args: argparse.Namespace) -> None:
    index_cols = [c.strip() for c in args.index.split(",")]
    rows = list(stream_rows(args.input, delimiter=args.delimiter))

    if not rows:
        return

    result = list(
        pivot_table(
            rows,
            index=index_cols,
            pivot_col=args.pivot,
            value_col=args.value,
            aggfunc=args.aggfunc,
            fill_value=args.fill_value,
        )
    )

    if not result:
        return

    fieldnames = list(result[0].keys())

    if args.output:
        write_rows(args.output, fieldnames, result, delimiter=args.delimiter)
    else:
        import csv
        writer = csv.DictWriter(
            sys.stdout, fieldnames=fieldnames,
            delimiter=args.delimiter, lineterminator="\n"
        )
        writer.writeheader()
        writer.writerows(result)


def register_pivot_table_parser(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser(
        "pivot-table",
        help="Aggregate rows into a wide pivot table",
    )
    p.add_argument("input", help="Input CSV file")
    p.add_argument(
        "--index", required=True,
        help="Comma-separated column(s) to use as row index",
    )
    p.add_argument("--pivot", required=True, help="Column whose values become new columns")
    p.add_argument("--value", required=True, help="Column to aggregate")
    p.add_argument(
        "--aggfunc", default="sum",
        choices=["sum", "mean", "count", "min", "max", "first", "last"],
        help="Aggregation function (default: sum)",
    )
    p.add_argument("--fill-value", default="", dest="fill_value",
                   help="Value for missing pivot combinations (default: empty)")
    p.add_argument("--output", "-o", default=None, help="Output CSV file (default: stdout)")
    p.add_argument("--delimiter", "-d", default=",", help="CSV delimiter (default: ,)")
    p.set_defaults(func=cmd_pivot_table)
