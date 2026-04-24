"""CLI subcommands for entropy / mutual-information analysis."""
from __future__ import annotations

import argparse
import csv
import json
import sys
from typing import List

from csv_surgeon.entropy import mutual_information, shannon_entropy
from csv_surgeon.reader import stream_rows


def cmd_entropy(args: argparse.Namespace) -> None:
    """Print Shannon entropy for one or more columns."""
    columns: List[str] = args.columns
    rows = list(stream_rows(args.input, delimiter=args.delimiter))

    results = {}
    for col in columns:
        vals = [r.get(col, "") for r in rows]
        h = shannon_entropy(vals)
        results[col] = round(h, 6) if h is not None else None

    if args.format == "json":
        print(json.dumps(results, indent=2))
    else:
        writer = csv.writer(sys.stdout)
        writer.writerow(["column", "entropy_bits"])
        for col, h in results.items():
            writer.writerow([col, "" if h is None else f"{h:.6f}"])


def cmd_mutual_info(args: argparse.Namespace) -> None:
    """Print mutual information between two columns."""
    rows = list(stream_rows(args.input, delimiter=args.delimiter))
    mi = mutual_information(rows, args.col_a, args.col_b)
    value = "" if mi is None else f"{mi:.6f}"

    if args.format == "json":
        print(json.dumps({"col_a": args.col_a, "col_b": args.col_b, "mutual_information_bits": mi}))
    else:
        writer = csv.writer(sys.stdout)
        writer.writerow(["col_a", "col_b", "mutual_information_bits"])
        writer.writerow([args.col_a, args.col_b, value])


def register_entropy_parser(subparsers) -> None:  # type: ignore[type-arg]
    # entropy subcommand
    p_ent = subparsers.add_parser("entropy", help="Shannon entropy of columns")
    p_ent.add_argument("input", help="Input CSV file")
    p_ent.add_argument("columns", nargs="+", help="Column names to analyse")
    p_ent.add_argument("-d", "--delimiter", default=",")
    p_ent.add_argument("--format", choices=["csv", "json"], default="csv")
    p_ent.set_defaults(func=cmd_entropy)

    # mutual-info subcommand
    p_mi = subparsers.add_parser("mutual-info", help="Mutual information between two columns")
    p_mi.add_argument("input", help="Input CSV file")
    p_mi.add_argument("col_a", help="First column")
    p_mi.add_argument("col_b", help="Second column")
    p_mi.add_argument("-d", "--delimiter", default=",")
    p_mi.add_argument("--format", choices=["csv", "json"], default="csv")
    p_mi.set_defaults(func=cmd_mutual_info)
