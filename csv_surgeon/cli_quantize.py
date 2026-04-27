"""CLI sub-commands for quantize: bin numeric columns."""
from __future__ import annotations

import argparse
import sys

from csv_surgeon.reader import stream_rows, read_header
from csv_surgeon.writer import write_rows, transform_inplace
from csv_surgeon.quantize import quantize_column, equal_width_quantize


def cmd_quantize(args: argparse.Namespace) -> None:
    labels = args.labels.split(",") if args.labels else None

    if args.edges:
        edges = [float(e) for e in args.edges.split(",")]

        def _transform(rows):
            return quantize_column(
                rows,
                column=args.column,
                edges=edges,
                out_column=args.out_column,
                labels=labels,
            )
    else:
        n_bins = args.bins or 4

        def _transform(rows):
            return equal_width_quantize(
                rows,
                column=args.column,
                n_bins=n_bins,
                out_column=args.out_column,
                labels=labels,
            )

    if args.inplace:
        transform_inplace(args.input, _transform, delimiter=args.delimiter)
    else:
        header = read_header(args.input, delimiter=args.delimiter)
        rows = stream_rows(args.input, delimiter=args.delimiter)
        out = args.output or sys.stdout
        write_rows(out, _transform(rows), delimiter=args.delimiter)


def register_quantize_parser(subparsers) -> None:
    p = subparsers.add_parser("quantize", help="Bin a numeric column into discrete buckets")
    p.add_argument("input", help="Input CSV file")
    p.add_argument("--column", required=True, help="Column to quantize")
    p.add_argument("--edges", default="", help="Comma-separated bin edges (e.g. 0,10,20,30)")
    p.add_argument("--bins", type=int, default=0, help="Number of equal-width bins (used when --edges not given)")
    p.add_argument("--labels", default="", help="Comma-separated bin labels")
    p.add_argument("--out-column", default="", dest="out_column", help="Output column name")
    p.add_argument("--output", default="", help="Output file (default: stdout)")
    p.add_argument("--inplace", action="store_true", help="Edit file in place")
    p.add_argument("--delimiter", default=",", help="CSV delimiter")
    p.set_defaults(func=cmd_quantize)
