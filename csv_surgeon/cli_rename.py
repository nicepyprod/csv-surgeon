"""CLI sub-commands for column rename / reorder operations."""
import argparse
import csv
import sys

from csv_surgeon.reader import stream_rows
from csv_surgeon.rename import rename_headers, reorder_columns, select_columns, drop_columns


def cmd_rename(args: argparse.Namespace) -> None:
    rows = stream_rows(args.input, delimiter=args.delimiter)

    if args.subcommand == "rename":
        mapping = dict(pair.split("=", 1) for pair in args.mapping)
        rows = rename_headers(rows, mapping)
    elif args.subcommand == "reorder":
        rows = reorder_columns(rows, args.columns, fill=args.fill)
    elif args.subcommand == "select":
        rows = select_columns(rows, args.columns)
    elif args.subcommand == "drop":
        rows = drop_columns(rows, args.columns)

    rows = list(rows)
    if not rows:
        return

    writer = csv.DictWriter(
        sys.stdout, fieldnames=list(rows[0].keys()),
        delimiter=args.delimiter, lineterminator="\n"
    )
    writer.writeheader()
    writer.writerows(rows)


def register_rename_parser(subparsers: argparse._SubParsersAction) -> None:
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("input", help="Input CSV file")
    common.add_argument("-d", "--delimiter", default=",")

    p = subparsers.add_parser("rename", help="Rename a column", parents=[common])
    p.add_argument("mapping", nargs="+", metavar="OLD=NEW")
    p.set_defaults(func=cmd_rename, subcommand="rename")

    p2 = subparsers.add_parser("reorder", help="Reorder columns", parents=[common])
    p2.add_argument("columns", nargs="+")
    p2.add_argument("--fill", default="")
    p2.set_defaults(func=cmd_rename, subcommand="reorder")

    p3 = subparsers.add_parser("select", help="Select columns", parents=[common])
    p3.add_argument("columns", nargs="+")
    p3.set_defaults(func=cmd_rename, subcommand="select")

    p4 = subparsers.add_parser("drop", help="Drop columns", parents=[common])
    p4.add_argument("columns", nargs="+")
    p4.set_defaults(func=cmd_rename, subcommand="drop")
