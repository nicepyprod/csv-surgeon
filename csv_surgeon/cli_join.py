"""CLI subcommand: join two CSV files."""
import argparse
import csv
import sys
from csv_surgeon.join import inner_join, left_join


def cmd_join(args: argparse.Namespace) -> None:
    with open(args.left, newline="") as lf, open(args.right, newline="") as rf:
        left_reader = csv.DictReader(lf, delimiter=args.delimiter)
        right_reader = csv.DictReader(rf, delimiter=args.delimiter)

        right_key = args.right_key or args.key

        if args.how == "inner":
            rows = inner_join(left_reader, right_reader, args.key, right_key)
        else:
            rows = left_join(left_reader, right_reader, args.key, right_key)

        rows = list(rows)
        if not rows:
            return

        writer = csv.DictWriter(
            sys.stdout,
            fieldnames=list(rows[0].keys()),
            delimiter=args.delimiter,
            lineterminator="\n",
        )
        writer.writeheader()
        writer.writerows(rows)


def register_join_parser(subparsers) -> None:
    p = subparsers.add_parser("join", help="Join two CSV files on a key column")
    p.add_argument("left", help="Left CSV file")
    p.add_argument("right", help="Right CSV file")
    p.add_argument("-k", "--key", required=True, help="Join key column (left side)")
    p.add_argument("--right-key", dest="right_key", default=None,
                   help="Join key column on right side (default: same as --key)")
    p.add_argument("--how", choices=["inner", "left"], default="inner",
                   help="Join type (default: inner)")
    p.add_argument("-d", "--delimiter", default=",", help="CSV delimiter")
    p.set_defaults(func=cmd_join)
