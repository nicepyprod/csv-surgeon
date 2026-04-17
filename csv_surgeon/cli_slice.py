"""CLI sub-commands for slicing: head, tail, slice."""
from __future__ import annotations
import argparse
import csv
import sys

from csv_surgeon.reader import stream_rows
from csv_surgeon.slice import head_rows, tail_rows, slice_rows
from csv_surgeon.writer import write_rows


def cmd_slice(args: argparse.Namespace) -> None:
    rows = stream_rows(args.file, delimiter=args.delimiter)

    if args.subcommand == "head":
        result = head_rows(rows, args.n)
    elif args.subcommand == "tail":
        result = iter(tail_rows(rows, args.n))
    else:  # slice
        result = slice_rows(
            rows,
            start=args.start,
            stop=args.stop,
            step=args.step,
        )

    writer = csv.DictWriter(
        sys.stdout, fieldnames=[], extrasaction="ignore"
    )
    first = True
    for row in result:
        if first:
            writer.fieldnames = list(row.keys())
            writer.writeheader()
            first = False
        writer.writerow(row)


def register_slice_parser(sub: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    p = sub.add_parser("slice", help="Extract a subset of rows")
    p.add_argument("file", help="Input CSV file")
    p.add_argument("--delimiter", default=",")
    sp = p.add_subparsers(dest="subcommand", required=True)

    ph = sp.add_parser("head", help="First N rows")
    ph.add_argument("n", type=int)

    pt = sp.add_parser("tail", help="Last N rows")
    pt.add_argument("n", type=int)

    ps = sp.add_parser("range", help="Row range [start:stop:step]")
    ps.add_argument("--start", type=int, default=0)
    ps.add_argument("--stop", type=int, default=None)
    ps.add_argument("--step", type=int, default=1)

    p.set_defaults(func=cmd_slice)
