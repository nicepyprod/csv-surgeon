"""CLI commands for date parsing and formatting."""
from __future__ import annotations
import argparse
import csv
import sys
from csv_surgeon.dateparse import format_date_column, extract_date_part


def cmd_dateformat(args: argparse.Namespace) -> None:
    reader = csv.DictReader(args.infile)
    rows = format_date_column(
        reader,
        column=args.column,
        out_fmt=args.out_fmt,
        out_column=args.out_column,
        in_fmt=args.in_fmt,
    )
    first = next(rows, None)
    if first is None:
        return
    writer = csv.DictWriter(args.outfile, fieldnames=list(first.keys()))
    writer.writeheader()
    writer.writerow(first)
    writer.writerows(rows)


def cmd_datepart(args: argparse.Namespace) -> None:
    reader = csv.DictReader(args.infile)
    rows = extract_date_part(
        reader,
        column=args.column,
        part=args.part,
        out_column=args.out_column,
        in_fmt=args.in_fmt,
    )
    first = next(rows, None)
    if first is None:
        return
    writer = csv.DictWriter(args.outfile, fieldnames=list(first.keys()))
    writer.writeheader()
    writer.writerow(first)
    writer.writerows(rows)


def register_dateparse_parser(sub: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    # date-format sub-command
    p_fmt = sub.add_parser("date-format", help="Re-format a date column")
    p_fmt.add_argument("column")
    p_fmt.add_argument("out_fmt", metavar="OUT_FMT")
    p_fmt.add_argument("--in-fmt", dest="in_fmt", default=None)
    p_fmt.add_argument("--out-column", dest="out_column", default=None)
    p_fmt.add_argument("--infile", type=argparse.FileType("r"), default=sys.stdin)
    p_fmt.add_argument("--outfile", type=argparse.FileType("w"), default=sys.stdout)
    p_fmt.set_defaults(func=cmd_dateformat)

    # date-part sub-command
    p_part = sub.add_parser("date-part", help="Extract part of a date column")
    p_part.add_argument("column")
    p_part.add_argument("part", choices=["year", "month", "day", "weekday", "hour", "minute", "second"])
    p_part.add_argument("--in-fmt", dest="in_fmt", default=None)
    p_part.add_argument("--out-column", dest="out_column", default=None)
    p_part.add_argument("--infile", type=argparse.FileType("r"), default=sys.stdin)
    p_part.add_argument("--outfile", type=argparse.FileType("w"), default=sys.stdout)
    p_part.set_defaults(func=cmd_datepart)
