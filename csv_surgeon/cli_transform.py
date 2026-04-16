"""CLI sub-commands for transform operations."""
from __future__ import annotations

import argparse
import sys

from csv_surgeon.reader import stream_rows
from csv_surgeon.transform import add_column, apply_transforms, rename_columns, strip_whitespace
from csv_surgeon.writer import write_rows


def cmd_transform(args: argparse.Namespace) -> None:
    """Apply column transforms and write result to output."""
    transforms = {}
    for spec in args.upper or []:
        transforms[spec] = str.upper
    for spec in args.lower or []:
        transforms[spec] = str.lower

    rows = stream_rows(args.input, delimiter=args.delimiter)
    if transforms:
        rows = apply_transforms(rows, transforms)
    if args.strip:
        rows = strip_whitespace(rows)
    if args.rename:
        mapping = {}
        for pair in args.rename:
            old, new = pair.split("=", 1)
            mapping[old] = new
        rows = rename_columns(rows, mapping)

    write_rows(rows, args.output, delimiter=args.delimiter)


def register_transform_parser(subparsers) -> None:
    p = subparsers.add_parser("transform", help="Apply column transforms")
    p.add_argument("input", help="Input CSV file")
    p.add_argument("output", help="Output CSV file")
    p.add_argument("-d", "--delimiter", default=",", help="CSV delimiter (default: ,)")
    p.add_argument("--upper", nargs="+", metavar="COL", help="Uppercase these columns")
    p.add_argument("--lower", nargs="+", metavar="COL", help="Lowercase these columns")
    p.add_argument("--strip", action="store_true", help="Strip whitespace from all values")
    p.add_argument(
        "--rename",
        nargs="+",
        metavar="OLD=NEW",
        help="Rename columns, e.g. --rename name=full_name",
    )
    p.set_defaults(func=cmd_transform)
