"""CLI sub-commands for fuzzy matching via Levenshtein distance."""
from __future__ import annotations
import argparse
import csv
import sys
from typing import List

from csv_surgeon.reader import stream_rows
from csv_surgeon.writer import write_rows
from csv_surgeon.levenshtein import fuzzy_match_column, add_distance_column


def cmd_fuzzy_filter(args: argparse.Namespace) -> None:
    rows = stream_rows(args.input, delimiter=args.delimiter)
    result = fuzzy_match_column(
        rows,
        column=args.column,
        target=args.target,
        max_distance=args.max_distance,
        case_sensitive=args.case_sensitive,
    )
    all_rows = list(result)
    if not all_rows:
        return
    write_rows(args.output, all_rows[0].keys(), iter(all_rows), delimiter=args.delimiter)


def cmd_add_distance(args: argparse.Namespace) -> None:
    rows = stream_rows(args.input, delimiter=args.delimiter)
    result = add_distance_column(
        rows,
        column=args.column,
        target=args.target,
        out_column=args.out_column,
        case_sensitive=args.case_sensitive,
    )
    all_rows = list(result)
    if not all_rows:
        return
    write_rows(args.output, all_rows[0].keys(), iter(all_rows), delimiter=args.delimiter)


def register_levenshtein_parser(sub: argparse._SubParsersAction) -> None:
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("input")
    common.add_argument("output")
    common.add_argument("--column", required=True)
    common.add_argument("--target", required=True)
    common.add_argument("--delimiter", default=",")
    common.add_argument("--case-sensitive", action="store_true", default=False)

    p_filter = sub.add_parser("fuzzy-filter", parents=[common],
                               help="Keep rows within edit distance of target")
    p_filter.add_argument("--max-distance", type=int, default=2)
    p_filter.set_defaults(func=cmd_fuzzy_filter)

    p_dist = sub.add_parser("add-distance", parents=[common],
                             help="Append Levenshtein distance column")
    p_dist.add_argument("--out-column", default=None)
    p_dist.set_defaults(func=cmd_add_distance)
