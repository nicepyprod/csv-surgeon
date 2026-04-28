"""CLI sub-commands for the impute module."""
from __future__ import annotations

import argparse
import sys
import csv

from csv_surgeon.impute import impute_constant, impute_mean, impute_median, impute_mode
from csv_surgeon.writer import transform_inplace


def cmd_impute(args: argparse.Namespace) -> None:
    strategy = args.strategy
    column = args.column
    output = args.output

    def _transform(rows):
        if strategy == "constant":
            if not args.value:
                raise ValueError("--value is required for strategy=constant")
            return impute_constant(rows, column, args.value)
        if strategy == "mean":
            return impute_mean(rows, column, args.out_column or None)
        if strategy == "median":
            return impute_median(rows, column, args.out_column or None)
        if strategy == "mode":
            return impute_mode(rows, column, args.out_column or None)
        raise ValueError(f"Unknown strategy: {strategy}")

    if output:
        transform_inplace(args.input, output, _transform)
    else:
        import csv_surgeon.reader as rdr
        rows = list(rdr.stream_rows(args.input))
        result = list(_transform(iter(rows)))
        if not result:
            return
        writer = csv.DictWriter(sys.stdout, fieldnames=list(result[0].keys()))
        writer.writeheader()
        writer.writerows(result)


def register_impute_parser(sub: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    p = sub.add_parser("impute", help="Impute missing values in a column")
    p.add_argument("input", help="Input CSV file")
    p.add_argument("--column", required=True, help="Column to impute")
    p.add_argument(
        "--strategy",
        choices=["constant", "mean", "median", "mode"],
        default="mean",
        help="Imputation strategy (default: mean)",
    )
    p.add_argument("--value", default="", help="Fill value for strategy=constant")
    p.add_argument("--out-column", dest="out_column", default="", help="Output column name")
    p.add_argument("--output", default="", help="Write result to this file (in-place style)")
    p.set_defaults(func=cmd_impute)
