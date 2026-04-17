"""CLI subcommand: fill — impute missing values in a CSV column."""
from __future__ import annotations
import argparse
import csv
import sys

from csv_surgeon.reader import stream_rows
from csv_surgeon.fill import fill_value, fill_forward, fill_backward, fill_mean
from csv_surgeon.writer import write_rows


def cmd_fill(args: argparse.Namespace) -> None:
    rows = stream_rows(args.input, delimiter=args.delimiter)

    if args.method == "value":
        if args.fill_with is None:
            print("--with is required for method=value", file=sys.stderr)
            sys.exit(1)
        result = fill_value(rows, args.column, args.fill_with)
    elif args.method == "forward":
        result = fill_forward(rows, args.column)
    elif args.method == "backward":
        result = fill_backward(rows, args.column)
    elif args.method == "mean":
        result = fill_mean(rows, args.column)
    else:
        print(f"Unknown method: {args.method}", file=sys.stderr)
        sys.exit(1)

    out = args.output or args.input
    write_rows(result, out, delimiter=args.delimiter)


def register_fill_parser(subparsers) -> None:
    p = subparsers.add_parser("fill", help="Impute missing values in a column")
    p.add_argument("input", help="Input CSV file")
    p.add_argument("--column", required=True, help="Column to fill")
    p.add_argument(
        "--method",
        choices=["value", "forward", "backward", "mean"],
        default="value",
        help="Fill strategy (default: value)",
    )
    p.add_argument("--with", dest="fill_with", default=None, help="Literal fill value")
    p.add_argument("--output", default=None, help="Output file (default: in-place)")
    p.add_argument("--delimiter", default=",", help="CSV delimiter")
    p.set_defaults(func=cmd_fill)
