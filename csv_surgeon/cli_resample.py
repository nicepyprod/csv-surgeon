"""CLI subcommand: resample — aggregate rows by time-period buckets."""
from __future__ import annotations

import argparse
import csv
import sys

from csv_surgeon.reader import stream_rows
from csv_surgeon.resample import resample_rows


def cmd_resample(args: argparse.Namespace) -> None:
    rows = stream_rows(args.input, delimiter=args.delimiter)
    resampled = resample_rows(
        rows,
        date_col=args.date_col,
        period=args.period,
        agg_col=args.agg_col,
        agg_func=args.agg_func,
        date_fmt=args.date_fmt or None,
        out_col=args.out_col,
    )
    writer = None
    out = open(args.output, "w", newline="") if args.output else sys.stdout
    try:
        for row in resampled:
            if writer is None:
                writer = csv.DictWriter(out, fieldnames=list(row.keys()),
                                        delimiter=args.delimiter)
                writer.writeheader()
            writer.writerow(row)
    finally:
        if args.output:
            out.close()


def register_resample_parser(subparsers) -> None:
    p = subparsers.add_parser("resample", help="Aggregate rows by time period")
    p.add_argument("input", help="Input CSV file")
    p.add_argument("--date-col", required=True, dest="date_col",
                   help="Column containing date/datetime values")
    p.add_argument("--period", default="month",
                   choices=["year", "month", "week", "day", "hour"],
                   help="Bucketing period (default: month)")
    p.add_argument("--agg-col", dest="agg_col", default=None,
                   help="Column to aggregate (required for sum/mean/min/max)")
    p.add_argument("--agg-func", dest="agg_func", default="count",
                   choices=["count", "sum", "mean", "min", "max"])
    p.add_argument("--date-fmt", dest="date_fmt", default="",
                   help="strptime format string for parsing dates")
    p.add_argument("--out-col", dest="out_col", default="value",
                   help="Name of the output value column (default: value)")
    p.add_argument("--delimiter", default=",")
    p.add_argument("--output", default=None, help="Output file (default: stdout)")
    p.set_defaults(func=cmd_resample)
