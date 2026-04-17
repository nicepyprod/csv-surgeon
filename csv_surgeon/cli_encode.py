"""CLI sub-commands: encode / decode columns."""
from __future__ import annotations
import sys
import csv
from argparse import ArgumentParser, Namespace
from csv_surgeon.encode import encode_columns, decode_columns


def cmd_encode(args: Namespace) -> None:
    reader = csv.DictReader(args.infile)
    if not reader.fieldnames:
        return
    columns = [c.strip() for c in args.columns.split(",")]
    fn = encode_columns if args.action == "encode" else decode_columns
    rows = fn(reader, columns, encoding=args.encoding)
    writer = csv.DictWriter(
        args.outfile, fieldnames=reader.fieldnames, lineterminator="\n"
    )
    writer.writeheader()
    for row in rows:
        writer.writerow(row)


def register_encode_parser(sub) -> None:
    p: ArgumentParser = sub.add_parser(
        "encode", help="Encode or decode column values."
    )
    p.add_argument("infile", type=open, help="Input CSV file.")
    p.add_argument(
        "outfile",
        nargs="?",
        type=lambda f: open(f, "w", newline=""),
        default=sys.stdout,
        help="Output CSV file (default: stdout).",
    )
    p.add_argument(
        "--action",
        choices=["encode", "decode"],
        default="encode",
        help="Whether to encode or decode (default: encode).",
    )
    p.add_argument(
        "--columns", required=True, help="Comma-separated list of columns to process."
    )
    p.add_argument(
        "--encoding",
        default="base64",
        help="Encoding scheme: base64, upper, lower, strip, reverse (default: base64).",
    )
    p.set_defaults(func=cmd_encode)
