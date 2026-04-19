"""CLI subcommand: diff two CSV files."""
import argparse
import csv
import json
import sys
from csv_surgeon.diff import diff_rows, diff_summary
from csv_surgeon.reader import stream_rows


def cmd_diff(ns: argparse.Namespace) -> None:
    try:
        left_rows = list(stream_rows(ns.left, delimiter=ns.delimiter))
        right_rows = list(stream_rows(ns.right, delimiter=ns.delimiter))
    except FileNotFoundError as e:
        print(f"error: {e}", file=sys.stderr)
        sys.exit(1)

    key_cols = ns.key.split(",")

    # Validate that key columns exist in both files
    if left_rows:
        missing = [c for c in key_cols if c not in left_rows[0]]
        if missing:
            print(f"error: key column(s) not found in left file: {', '.join(missing)}", file=sys.stderr)
            sys.exit(1)
    if right_rows:
        missing = [c for c in key_cols if c not in right_rows[0]]
        if missing:
            print(f"error: key column(s) not found in right file: {', '.join(missing)}", file=sys.stderr)
            sys.exit(1)

    if ns.summary:
        s = diff_summary(iter(left_rows), iter(right_rows), key_cols)
        if ns.json:
            print(json.dumps(s))
        else:
            for k, v in s.items():
                print(f"{k}: {v}")
        return

    diffs = list(diff_rows(iter(left_rows), iter(right_rows), key_cols))
    if not diffs:
        return

    fieldnames = list(diffs[0].keys())
    writer = csv.DictWriter(sys.stdout, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(diffs)


def register_diff_parser(subparsers) -> None:
    p = subparsers.add_parser("diff", help="Diff two CSV files by key column(s)")
    p.add_argument("left", help="Left (original) CSV file")
    p.add_argument("right", help="Right (new) CSV file")
    p.add_argument("--key", required=True, help="Comma-separated key column(s)")
    p.add_argument("--delimiter", default=",")
    p.add_argument("--summary", action="store_true", help="Print summary counts only")
    p.add_argument("--json", action="store_true", help="Output summary as JSON")
    p.set_defaults(func=cmd_diff)
