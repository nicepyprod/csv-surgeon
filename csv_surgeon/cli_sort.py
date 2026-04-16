"""CLI sub-command for sorting CSV files."""
import argparse
import csv
import sys

from csv_surgeon.reader import stream_rows
from csv_surgeon.sort import sort_rows, sort_rows_multi
from csv_surgeon.writer import write_rows


def cmd_sort(args: argparse.Namespace) -> None:
    keys = args.key  # list of column names
    numeric_keys = args.numeric or []
    rows = list(stream_rows(args.input, delimiter=args.delimiter))
    if not rows:
        return

    if len(keys) == 1:
        sorted_rows = list(
            sort_rows(rows, key=keys[0], reverse=args.reverse,
                      numeric=keys[0] in numeric_keys)
        )
    else:
        sorted_rows = list(
            sort_rows_multi(rows, keys=keys, reverse=args.reverse,
                            numeric_keys=numeric_keys)
        )

    fieldnames = list(rows[0].keys())
    out = args.output or args.input
    write_rows(out, sorted_rows, fieldnames=fieldnames, delimiter=args.delimiter)


def register_sort_parser(subparsers) -> None:
    p = subparsers.add_parser("sort", help="Sort CSV rows by one or more columns")
    p.add_argument("input", help="Input CSV file")
    p.add_argument("-k", "--key", nargs="+", required=True,
                   help="Column name(s) to sort by")
    p.add_argument("-r", "--reverse", action="store_true",
                   help="Sort in descending order")
    p.add_argument("-n", "--numeric", nargs="*", metavar="COL",
                   help="Treat these columns as numeric")
    p.add_argument("-o", "--output", default=None,
                   help="Output file (default: overwrite input)")
    p.add_argument("--delimiter", default=",", help="CSV delimiter (default: ,)")
    p.set_defaults(func=cmd_sort)
