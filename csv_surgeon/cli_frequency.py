"""CLI subcommands for frequency / value-count operations."""
from __future__ import annotations
import argparse
import csv
import json
import sys

from csv_surgeon.reader import stream_rows
from csv_surgeon.frequency import value_counts, top_n


def cmd_frequency(args: argparse.Namespace) -> None:
    rows = list(stream_rows(args.input, delimiter=args.delimiter))
    if args.top:
        result = top_n(rows, args.column, n=args.top)
    else:
        result = value_counts(
            rows, args.column, normalize=args.normalize, sort=not args.no_sort
        )
    if args.json:
        print(json.dumps(result, indent=2))
        return
    if not result:
        return
    writer = csv.DictWriter(
        sys.stdout, fieldnames=list(result[0].keys()), lineterminator="\n"
    )
    writer.writeheader()
    writer.writerows(result)


def register_frequency_parser(subparsers) -> None:
    p = subparsers.add_parser("frequency", help="Count value frequencies in a column")
    p.add_argument("input", help="Input CSV file")
    p.add_argument("column", help="Column to analyse")
    p.add_argument("--delimiter", default=",")
    p.add_argument("--normalize", action="store_true", help="Add percent column")
    p.add_argument("--no-sort", action="store_true", help="Preserve insertion order")
    p.add_argument("--top", type=int, default=0, help="Return only top-N values")
    p.add_argument("--json", action="store_true", help="Output as JSON")
    p.set_defaults(func=cmd_frequency)
