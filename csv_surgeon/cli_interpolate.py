"""CLI sub-commands for interpolate: linear and constant fill."""
from __future__ import annotations
import argparse
import csv
import sys

from csv_surgeon.interpolate import interpolate_linear, interpolate_constant


def cmd_interpolate(args: argparse.Namespace) -> None:
    reader = csv.DictReader(args.infile)
    if not reader.fieldnames:
        return
    fieldnames = list(reader.fieldnames)
    rows = list(reader)

    columns = args.columns if args.columns else fieldnames

    for col in columns:
        if args.method == "linear":
            rows = interpolate_linear(rows, col)
        else:
            rows = list(interpolate_constant(rows, col, fill=args.fill))

    writer = csv.DictWriter(args.outfile, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)


def register_interpolate_parser(sub: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    p = sub.add_parser(
        "interpolate",
        help="Fill missing numeric values via linear or constant interpolation",
    )
    p.add_argument("infile", nargs="?", type=argparse.FileType("r"), default=sys.stdin)
    p.add_argument("outfile", nargs="?", type=argparse.FileType("w"), default=sys.stdout)
    p.add_argument(
        "--columns", "-c",
        nargs="+",
        metavar="COL",
        default=None,
        help="Columns to interpolate (default: all)",
    )
    p.add_argument(
        "--method", "-m",
        choices=["linear", "constant"],
        default="linear",
        help="Interpolation method (default: linear)",
    )
    p.add_argument(
        "--fill", "-f",
        default="0",
        help="Constant fill value when --method=constant (default: 0)",
    )
    p.set_defaults(func=cmd_interpolate)
