"""CLI sub-commands for group aggregation."""
from __future__ import annotations
import argparse
import csv
import sys

from csv_surgeon.moving_agg import group_aggregate
from csv_surgeon.reader import stream_rows
from csv_surgeon.writer import write_rows


def cmd_group_agg(args: argparse.Namespace) -> None:
    rows = stream_rows(args.input, delimiter=args.delimiter)
    result = group_aggregate(
        rows,
        group_col=args.group,
        value_col=args.value,
        func=args.func,
        out_col=args.out_col,
    )
    if args.output == "-":
        writer = None
        first = True
        for row in result:
            if first:
                writer = csv.DictWriter(sys.stdout, fieldnames=list(row.keys()),
                                        delimiter=args.delimiter)
                writer.writeheader()
                first = False
            writer.writerow(row)  # type: ignore[union-attr]
    else:
        write_rows(args.output, result, delimiter=args.delimiter)


def register_group_agg_parser(subparsers) -> None:
    p = subparsers.add_parser("group-agg", help="Append group aggregation column to each row")
    p.add_argument("input", help="Input CSV file")
    p.add_argument("--group", required=True, help="Column to group by")
    p.add_argument("--value", required=True, help="Column to aggregate")
    p.add_argument(
        "--func",
        default="sum",
        choices=["sum", "mean", "min", "max", "count"],
        help="Aggregation function (default: sum)",
    )
    p.add_argument("--out-col", default=None, dest="out_col",
                   help="Output column name (default: <value>_<func>)")
    p.add_argument("--output", default="-", help="Output file (default: stdout)")
    p.add_argument("--delimiter", default=",", help="CSV delimiter (default: ,)")
    p.set_defaults(func=cmd_group_agg)
