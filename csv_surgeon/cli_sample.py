"""CLI sub-command: sample."""
from __future__ import annotations

import argparse
import csv
import sys

from csv_surgeon.reader import stream_rows
from csv_surgeon.sample import sample_fraction, sample_rows, systematic_sample
from csv_surgeon.writer import write_rows


def cmd_sample(args: argparse.Namespace) -> None:
    rows = list(stream_rows(args.input, delimiter=args.delimiter))
    if not rows:
        return
    fieldnames = list(rows[0].keys())

    if args.mode == "reservoir":
        result = sample_rows(rows, args.n, seed=args.seed)
    elif args.mode == "fraction":
        result = list(sample_fraction(rows, args.fraction, seed=args.seed))
    elif args.mode == "systematic":
        result = list(systematic_sample(rows, args.step, offset=args.offset))
    else:
        print(f"Unknown mode: {args.mode}", file=sys.stderr)
        sys.exit(1)

    out = args.output or args.input
    write_rows(out, fieldnames, iter(result), delimiter=args.delimiter)


def register_sample_parser(sub: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    p = sub.add_parser("sample", help="Sample rows from a CSV file")
    p.add_argument("input", help="Input CSV file")
    p.add_argument("--output", default=None, help="Output file (default: in-place)")
    p.add_argument("--delimiter", default=",")
    p.add_argument("--seed", type=int, default=None)
    mode = p.add_subparsers(dest="mode", required=True)

    r = mode.add_parser("reservoir", help="Reservoir sample n rows")
    r.add_argument("n", type=int)

    f = mode.add_parser("fraction", help="Sample each row with given probability")
    f.add_argument("fraction", type=float)

    s = mode.add_parser("systematic", help="Every k-th row")
    s.add_argument("step", type=int)
    s.add_argument("--offset", type=int, default=0)

    p.set_defaults(func=cmd_sample)
