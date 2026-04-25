"""CLI subcommands for rolling window context and diff."""
from __future__ import annotations

import argparse
import csv
import sys

from csv_surgeon.rolling_window import window_context, window_diff
from csv_surgeon.reader import stream_rows
from csv_surgeon.writer import write_rows


def cmd_window_context(args: argparse.Namespace) -> None:
    rows = list(stream_rows(args.input))
    result = list(
        window_context(
            rows,
            before=args.before,
            after=args.after,
            prefix_before=args.prefix_before,
            prefix_after=args.prefix_after,
            fill=args.fill,
        )
    )
    out = args.output or args.input
    write_rows(out, result)


def cmd_window_diff(args: argparse.Namespace) -> None:
    rows = stream_rows(args.input)
    result = list(window_diff(rows, column=args.column, out_column=args.out_column, fill=args.fill))
    out = args.output or args.input
    write_rows(out, result)


def register_rolling_window_parser(sub: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    # window-context
    p_ctx = sub.add_parser("window-context", help="Attach preceding/following rows as context columns")
    p_ctx.add_argument("input", help="Input CSV file")
    p_ctx.add_argument("--before", type=int, default=1, help="Number of preceding rows (default 1)")
    p_ctx.add_argument("--after", type=int, default=1, help="Number of following rows (default 1)")
    p_ctx.add_argument("--prefix-before", default="prev_", dest="prefix_before")
    p_ctx.add_argument("--prefix-after", default="next_", dest="prefix_after")
    p_ctx.add_argument("--fill", default="", help="Fill value for missing context")
    p_ctx.add_argument("-o", "--output", default=None)
    p_ctx.set_defaults(func=cmd_window_context)

    # window-diff
    p_diff = sub.add_parser("window-diff", help="Add column with row-to-row numeric difference")
    p_diff.add_argument("input", help="Input CSV file")
    p_diff.add_argument("--column", required=True, help="Column to diff")
    p_diff.add_argument("--out-column", default=None, dest="out_column")
    p_diff.add_argument("--fill", default="", help="Fill value when diff unavailable")
    p_diff.add_argument("-o", "--output", default=None)
    p_diff.set_defaults(func=cmd_window_diff)
