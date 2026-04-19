"""CLI sub-command: bucket — bin a numeric column into labeled ranges."""
from __future__ import annotations
import argparse
import csv
import sys
from csv_surgeon.bucket import bucket_column, equal_width_edges
from csv_surgeon.reader import stream_rows
from csv_surgeon.writer import write_rows


def cmd_bucket(args: argparse.Namespace) -> None:
    edges: list[float]
    if args.edges:
        edges = [float(e) for e in args.edges]
    elif args.bins is not None:
        raw = list(stream_rows(args.input, delimiter=args.delimiter))
        vals = []
        for row in raw:
            try:
                vals.append(float(row[args.column]))
            except (ValueError, KeyError):
                pass
        if not vals:
            sys.exit(f"No numeric values found in column '{args.column}'")
        edges = equal_width_edges(min(vals), max(vals), args.bins)
        rows_iter = iter(raw)
    else:
        sys.exit("Provide --edges or --bins")

    if not args.edges:  # already loaded
        rows_iter = iter(raw)  # type: ignore[assignment]
    else:
        rows_iter = stream_rows(args.input, delimiter=args.delimiter)

    labels = args.labels if args.labels else None
    result = bucket_column(
        rows_iter,
        column=args.column,
        edges=edges,
        labels=labels,
        out_column=args.out_column,
    )
    write_rows(args.output, result, delimiter=args.delimiter)


def register_bucket_parser(sub: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    p = sub.add_parser("bucket", help="Bin a numeric column into labeled buckets")
    p.add_argument("input", help="Input CSV file")
    p.add_argument("column", help="Column to bucket")
    p.add_argument("--edges", nargs="+", type=float, help="Explicit bin edges")
    p.add_argument("--bins", type=int, help="Number of equal-width bins (auto edges)")
    p.add_argument("--labels", nargs="+", help="Bucket labels (one per bin)")
    p.add_argument("--out-column", dest="out_column", default=None)
    p.add_argument("--output", default="-", help="Output file (default: stdout)")
    p.add_argument("--delimiter", default=",")
    p.set_defaults(func=cmd_bucket)
