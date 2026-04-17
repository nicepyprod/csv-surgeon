"""CLI sub-command: cast — coerce column types in a CSV file."""
from __future__ import annotations
import argparse
import csv
import sys
from csv_surgeon.cast import cast_columns


def cmd_cast(args: argparse.Namespace) -> None:
    """Execute the cast sub-command."""
    casts: dict[str, str] = {}
    for spec in args.cast:
        if ":" not in spec:
            print(f"Invalid cast spec '{spec}'. Expected column:type", file=sys.stderr)
            sys.exit(1)
        col, typename = spec.split(":", 1)
        casts[col.strip()] = typename.strip()

    with open(args.input, newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh, delimiter=args.delimiter)
        if reader.fieldnames is None:
            return
        fieldnames = list(reader.fieldnames)
        writer = csv.DictWriter(
            sys.stdout,
            fieldnames=fieldnames,
            delimiter=args.delimiter,
            lineterminator="\n",
        )
        writer.writeheader()
        for row in cast_columns(reader, casts, errors=args.errors):
            writer.writerow(row)


def register_cast_parser(subparsers: argparse._SubParsersAction) -> None:  # noqa: SLF001
    p = subparsers.add_parser("cast", help="Coerce column values to a target type")
    p.add_argument("input", help="Input CSV file")
    p.add_argument(
        "--cast",
        metavar="COL:TYPE",
        action="append",
        required=True,
        help="Column and target type, e.g. age:int (repeatable)",
    )
    p.add_argument(
        "--errors",
        choices=["raise", "ignore", "null"],
        default="raise",
        help="How to handle cast failures (default: raise)",
    )
    p.add_argument("--delimiter", default=",", help="Field delimiter (default: ,)")
    p.set_defaults(func=cmd_cast)
