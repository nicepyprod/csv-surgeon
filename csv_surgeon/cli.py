"""Main CLI entry point for csv-surgeon."""
import argparse
import sys

from csv_surgeon.reader import stream_rows
from csv_surgeon.filter import filter_by_value, filter_by_contains, drop_empty
from csv_surgeon.writer import write_rows
from csv_surgeon.cli_transform import register_transform_parser
from csv_surgeon.cli_sort import register_sort_parser


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="csv-surgeon",
        description="Surgical in-place edits and transforms on CSV files.",
    )
    sub = parser.add_subparsers(dest="command")

    # filter sub-command
    fp = sub.add_parser("filter", help="Filter rows from a CSV file")
    fp.add_argument("input", help="Input CSV file")
    fp.add_argument("-o", "--output", required=True, help="Output CSV file")
    fp.add_argument("--delimiter", default=",")
    fp.add_argument("--equals", nargs=2, metavar=("COL", "VAL"),
                    help="Keep rows where COL equals VAL")
    fp.add_argument("--contains", nargs=2, metavar=("COL", "VAL"),
                    help="Keep rows where COL contains VAL")
    fp.add_argument("--ignore-case", action="store_true")
    fp.add_argument("--drop-empty", metavar="COL",
                    help="Drop rows where COL is empty")
    fp.set_defaults(func=cmd_filter)

    register_transform_parser(sub)
    register_sort_parser(sub)
    return parser


def cmd_filter(args: argparse.Namespace) -> None:
    rows = stream_rows(args.input, delimiter=args.delimiter)
    if args.equals:
        col, val = args.equals
        rows = filter_by_value(rows, col, val, case_sensitive=not args.ignore_case)
    if args.contains:
        col, val = args.contains
        rows = filter_by_contains(rows, col, val, case_sensitive=not args.ignore_case)
    if args.drop_empty:
        rows = drop_empty(rows, args.drop_empty)
    consumed = list(rows)
    if consumed:
        write_rows(args.output, consumed, fieldnames=list(consumed[0].keys()),
                   delimiter=args.delimiter)
    else:
        open(args.output, "w").close()


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(1)
    args.func(args)


if __name__ == "__main__":
    main()
