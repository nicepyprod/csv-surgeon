"""CLI subcommands for outlier detection."""
from __future__ import annotations
import argparse
import csv
import sys

from csv_surgeon.outlier import filter_outliers_iqr, flag_iqr_outliers
from csv_surgeon.reader import stream_rows


def cmd_outlier(ns: argparse.Namespace) -> None:
    rows = stream_rows(ns.input, delimiter=ns.delimiter)
    if ns.mode == "flag":
        result = flag_iqr_outliers(
            rows,
            column=ns.column,
            out_column=ns.out_column or "",
            flag_true=ns.flag_true,
            flag_false=ns.flag_false,
        )
    else:
        result = filter_outliers_iqr(
            rows,
            column=ns.column,
            keep_outliers=(ns.mode == "keep"),
        )

    writer: csv.DictWriter | None = None
    out = open(ns.output, "w", newline="") if ns.output else sys.stdout
    try:
        for row in result:
            if writer is None:
                writer = csv.DictWriter(out, fieldnames=list(row.keys()))
                writer.writeheader()
            writer.writerow(row)
    finally:
        if ns.output:
            out.close()


def register_outlier_parser(sub: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    p = sub.add_parser("outlier", help="Detect or remove IQR outliers in a column")
    p.add_argument("input", help="Input CSV file")
    p.add_argument("--column", required=True, help="Column to analyse")
    p.add_argument(
        "--mode",
        choices=["remove", "keep", "flag"],
        default="remove",
        help="remove outliers (default), keep only outliers, or flag them",
    )
    p.add_argument("--out-column", default="", dest="out_column")
    p.add_argument("--flag-true", default="1", dest="flag_true")
    p.add_argument("--flag-false", default="0", dest="flag_false")
    p.add_argument("--output", default="", help="Output file (default: stdout)")
    p.add_argument("--delimiter", default=",")
    p.set_defaults(func=cmd_outlier)
