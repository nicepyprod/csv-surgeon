"""CLI sub-commands: flatten and collapse."""
from __future__ import annotations
import argparse, csv, sys
from csv_surgeon.flatten import flatten_column, collapse_column


def cmd_flatten(args: argparse.Namespace) -> None:
    reader = csv.DictReader(args.input)
    writer: csv.DictWriter | None = None
    for row in flatten_column(reader, args.column, sep=args.sep):
        if writer is None:
            writer = csv.DictWriter(
                args.output, fieldnames=list(row.keys()), lineterminator="\n"
            )
            writer.writeheader()
        writer.writerow(row)


def cmd_collapse(args: argparse.Namespace) -> None:
    reader = csv.DictReader(args.input)
    writer: csv.DictWriter | None = None
    for row in collapse_column(reader, args.column, key_column=args.key, sep=args.sep):
        if writer is None:
            writer = csv.DictWriter(
                args.output, fieldnames=list(row.keys()), lineterminator="\n"
            )
            writer.writeheader()
        writer.writerow(row)


def register_flatten_parser(sub: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    p_flat = sub.add_parser("flatten", help="Explode a multi-value column into rows")
    p_flat.add_argument("column", help="Column to flatten")
    p_flat.add_argument("--sep", default="|", help="Separator (default: |)")
    p_flat.add_argument(
        "--input", type=argparse.FileType("r"), default=sys.stdin
    )
    p_flat.add_argument(
        "--output", type=argparse.FileType("w"), default=sys.stdout
    )
    p_flat.set_defaults(func=cmd_flatten)

    p_col = sub.add_parser("collapse", help="Collapse flattened rows back into one row")
    p_col.add_argument("column", help="Column whose values are joined")
    p_col.add_argument("--key", required=True, help="Column that identifies the group")
    p_col.add_argument("--sep", default="|", help="Separator (default: |)")
    p_col.add_argument(
        "--input", type=argparse.FileType("r"), default=sys.stdin
    )
    p_col.add_argument(
        "--output", type=argparse.FileType("w"), default=sys.stdout
    )
    p_col.set_defaults(func=cmd_collapse)
