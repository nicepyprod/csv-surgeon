"""CLI sub-command for sorting CSV files."""
import argparse
import csv

from csv_surgeon.sort import sort_rows, sort_rows_multi


def cmd_sort(args: argparse.Namespace) -> None:
    keys = args.key  # list of column names
    numeric_keys = args.numeric or []
    with open(args.input, newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh, delimiter=args.delimiter)
        fieldnames = list(reader.fieldnames or [])
        rows = list(reader)
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

    out = args.output or args.input
    with open(out, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames, delimiter=args.delimiter)
        writer.writeheader()
        writer.writerows(sorted_rows)


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
