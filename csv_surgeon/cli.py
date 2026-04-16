"""CLI entry point for csv-surgeon."""

import argparse
import sys

from csv_surgeon.filter import filter_by_value, filter_by_contains, drop_empty
from csv_surgeon.reader import stream_rows
from csv_surgeon.writer import write_rows


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="csv-surgeon",
        description="Surgical in-place edits and transforms on large CSV files.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # filter sub-command
    f = sub.add_parser("filter", help="Filter rows from a CSV file.")
    f.add_argument("input", help="Input CSV file path.")
    f.add_argument("output", help="Output CSV file path.")
    f.add_argument("--delimiter", default=",", help="CSV delimiter (default: ,).")
    f.add_argument("--column", help="Column to filter on.")
    f.add_argument("--equals", help="Keep rows where column equals this value.")
    f.add_argument("--contains", help="Keep rows where column contains this substring.")
    f.add_argument(
        "--drop-empty",
        dest="drop_empty",
        action="store_true",
        help="Drop rows with empty values.",
    )
    f.add_argument(
        "--case-insensitive",
        dest="case_insensitive",
        action="store_true",
        help="Case-insensitive matching.",
    )
    return parser


def cmd_filter(args: argparse.Namespace) -> None:
    rows = stream_rows(args.input, delimiter=args.delimiter)

    if args.drop_empty:
        rows = drop_empty(rows, column=args.column)
    elif args.equals and args.column:
        rows = filter_by_value(
            rows, args.column, args.equals,
            case_sensitive=not args.case_insensitive,
        )
    elif args.contains and args.column:
        rows = filter_by_contains(
            rows, args.column, args.contains,
            case_sensitive=not args.case_insensitive,
        )

    write_rows(args.output, rows, delimiter=args.delimiter)


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    if args.command == "filter":
        cmd_filter(args)


if __name__ == "__main__":
    main()
