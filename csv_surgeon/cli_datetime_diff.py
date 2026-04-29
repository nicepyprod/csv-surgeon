"""CLI sub-command: datetime-diff."""
from __future__ import annotations

import argparse
import csv
import sys

from csv_surgeon.datetime_diff import datetime_diff_column
from csv_surgeon.writer import transform_inplace


def cmd_datetime_diff(args: argparse.Namespace) -> None:
    if args.inplace:
        def _transform(rows):
            return datetime_diff_column(
                rows,
                col_a=args.col_a,
                col_b=args.col_b,
                out_column=args.out_column,
                unit=args.unit,
                fmt=args.fmt or None,
                absolute=args.absolute,
            )
        transform_inplace(args.file, _transform)
        return

    with open(args.file, newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        rows = datetime_diff_column(
            iter(reader),
            col_a=args.col_a,
            col_b=args.col_b,
            out_column=args.out_column,
            unit=args.unit,
            fmt=args.fmt or None,
            absolute=args.absolute,
        )
        first = next(rows, None)
        if first is None:
            return
        writer = csv.DictWriter(sys.stdout, fieldnames=list(first.keys()),
                                lineterminator="\n")
        writer.writeheader()
        writer.writerow(first)
        writer.writerows(rows)


def register_datetime_diff_parser(sub: argparse._SubParsersAction) -> None:  # noqa: SLF001
    p = sub.add_parser("datetime-diff",
                       help="Add a column with the difference between two date columns")
    p.add_argument("file", help="Input CSV file")
    p.add_argument("--col-a", required=True, dest="col_a",
                   help="Start date column")
    p.add_argument("--col-b", required=True, dest="col_b",
                   help="End date column")
    p.add_argument("--out-column", default="diff_days", dest="out_column")
    p.add_argument("--unit", default="days",
                   choices=["days", "hours", "minutes", "seconds"])
    p.add_argument("--fmt", default="", help="strptime format string (optional)")
    p.add_argument("--absolute", action="store_true",
                   help="Use absolute value of difference")
    p.add_argument("--inplace", action="store_true",
                   help="Edit the file in place")
    p.set_defaults(func=cmd_datetime_diff)
