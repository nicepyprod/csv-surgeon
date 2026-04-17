"""CLI sub-command: aggregate."""
import argparse
import csv
import sys

from csv_surgeon.aggregate import aggregate_rows
from csv_surgeon.reader import stream_rows


def cmd_aggregate(args: argparse.Namespace) -> None:
    rows = stream_rows(args.input, delimiter=args.delimiter)
    results = list(aggregate_rows(rows, args.group_by, args.column, args.func))

    if not results:
        return

    writer = csv.DictWriter(
        sys.stdout,
        fieldnames=list(results[0].keys()),
        lineterminator="\n",
    )
    writer.writeheader()
    writer.writerows(results)


def register_aggregate_parser(subparsers) -> None:
    p = subparsers.add_parser(
        "aggregate",
        help="Group rows and compute sum/count/min/max/mean on a column.",
    )
    p.add_argument("input", help="Input CSV file")
    p.add_argument("-g", "--group-by", nargs="+", required=True, metavar="COL",
                   help="One or more columns to group by")
    p.add_argument("-c", "--column", required=True,
                   help="Column to aggregate")
    p.add_argument("-f", "--func", default="sum",
                   choices=["sum", "count", "min", "max", "mean"],
                   help="Aggregation function (default: sum)")
    p.add_argument("--delimiter", default=",", help="Field delimiter (default: ,)")
    p.set_defaults(func_cmd=cmd_aggregate)
