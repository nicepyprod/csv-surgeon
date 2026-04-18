"""CLI subcommand: window — rolling aggregations."""
import argparse
import csv
import sys

from csv_surgeon.reader import stream_rows
from csv_surgeon.window import rolling_mean, rolling_sum
from csv_surgeon.writer import write_rows


def cmd_window(args: argparse.Namespace) -> None:
    rows = stream_rows(args.input, delimiter=args.delimiter)

    if args.func == "mean":
        result = rolling_mean(rows, args.column, args.window, out_column=args.out_column or "")
    elif args.func == "sum":
        result = rolling_sum(rows, args.column, args.window, out_column=args.out_column or "")
    else:
        print(f"Unknown function: {args.func}", file=sys.stderr)
        sys.exit(1)

    rows_list = list(result)
    if not rows_list:
        return

    if args.output:
        write_rows(args.output, rows_list, fieldnames=list(rows_list[0].keys()))
    else:
        writer = csv.DictWriter(sys.stdout, fieldnames=list(rows_list[0].keys()))
        writer.writeheader()
        writer.writerows(rows_list)


def register_window_parser(subparsers) -> None:
    p = subparsers.add_parser("window", help="Rolling window aggregations")
    p.add_argument("input", help="Input CSV file")
    p.add_argument("--column", required=True, help="Column to aggregate")
    p.add_argument("--func", choices=["mean", "sum"], default="mean", help="Aggregation function")
    p.add_argument("--window", type=int, default=3, help="Window size (default: 3)")
    p.add_argument("--out-column", dest="out_column", default="", help="Output column name")
    p.add_argument("--output", default="", help="Output file (default: stdout)")
    p.add_argument("--delimiter", default=",", help="CSV delimiter")
    p.set_defaults(func=cmd_window)
