"""CLI sub-command: dedupe."""
from __future__ import annotations
import argparse
import csv
import sys
from csv_surgeon.reader import stream_rows
from csv_surgeon.writer import write_rows
from csv_surgeon.dedupe import dedupe_rows


def cmd_dedupe(args: argparse.Namespace) -> None:
    """Execute the dedupe sub-command."""
    keys = args.keys.split(",") if args.keys else None
    rows = stream_rows(args.input, delimiter=args.delimiter)

    deduped = dedupe_rows(rows, keys=keys, keep=args.keep)

    output = args.output or args.input
    write_rows(deduped, output, delimiter=args.delimiter)

    if args.verbose:
        print(f"Deduplicated '{args.input}' -> '{output}'")


def register_dedupe_parser(subparsers) -> None:
    """Register the 'dedupe' sub-command."""
    p: argparse.ArgumentParser = subparsers.add_parser(
        "dedupe",
        help="Remove duplicate rows from a CSV file.",
    )
    p.add_argument("input", help="Input CSV file path.")
    p.add_argument("-o", "--output", default=None, help="Output file (default: in-place).")
    p.add_argument("-d", "--delimiter", default=",", help="CSV delimiter (default: ',').")
    p.add_argument(
        "-k", "--keys",
        default=None,
        help="Comma-separated column names to use as uniqueness key (default: all columns).",
    )
    p.add_argument(
        "--keep",
        choices=["first", "last"],
        default="first",
        help="Which occurrence to keep (default: first).",
    )
    p.add_argument("-v", "--verbose", action="store_true")
    p.set_defaults(func=cmd_dedupe)
