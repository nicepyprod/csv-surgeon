"""CLI sub-command: stats — print column statistics."""
from __future__ import annotations
import argparse
import json
import sys

from csv_surgeon.reader import stream_rows
from csv_surgeon.stats import multi_column_stats


def cmd_stats(args: argparse.Namespace) -> None:
    columns = [c.strip() for c in args.columns.split(",")]
    rows = stream_rows(args.input, delimiter=args.delimiter)
    results = multi_column_stats(rows, columns)

    if args.format == "json":
        print(json.dumps(results, indent=2))
    else:
        # simple table
        headers = ["column", "total", "count", "null_count",
                   "min", "max", "mean", "stddev"]
        fmt = "{:<15}" + "{:>10}" * (len(headers) - 1)
        print(fmt.format(*headers))
        print("-" * (15 + 10 * (len(headers) - 1)))
        for r in results:
            def _f(v):
                if v is None:
                    return "N/A"
                if isinstance(v, float):
                    return f"{v:.4f}"
                return str(v)
            print(fmt.format(r["column"], _f(r["total"]), _f(r["count"]),
                             _f(r["null_count"]), _f(r["min"]), _f(r["max"]),
                             _f(r["mean"]), _f(r["stddev"])))


def register_stats_parser(subparsers) -> None:
    p = subparsers.add_parser("stats", help="Print column statistics")
    p.add_argument("input", help="Input CSV file")
    p.add_argument("--columns", required=True,
                   help="Comma-separated column names")
    p.add_argument("--delimiter", default=",", help="CSV delimiter")
    p.add_argument("--format", choices=["table", "json"], default="table",
                   help="Output format")
    p.set_defaults(func=cmd_stats)
