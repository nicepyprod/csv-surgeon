"""CLI sub-commands: split-by and split-chunk."""
from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

from csv_surgeon.reader import stream_rows, read_header
from csv_surgeon.split import split_rows, split_evenly


def cmd_split_by(args: argparse.Namespace) -> None:
    """Split input CSV into one file per distinct value of --column."""
    header = read_header(args.input, delimiter=args.delimiter)
    rows = list(stream_rows(args.input, delimiter=args.delimiter))
    groups = split_rows(rows, args.column, max_groups=args.max_groups or None)
    out_dir = Path(args.outdir)
    out_dir.mkdir(parents=True, exist_ok=True)
    for key, group_rows in groups.items():
        safe_key = key.replace("/", "_").replace("\\", "_") or "__empty__"
        out_path = out_dir / f"{safe_key}.csv"
        with open(out_path, "w", newline="", encoding="utf-8") as fh:
            writer = csv.DictWriter(fh, fieldnames=header, delimiter=args.delimiter)
            writer.writeheader()
            writer.writerows(group_rows)
    print(f"Wrote {len(groups)} file(s) to {out_dir}", file=sys.stderr)


def cmd_split_chunk(args: argparse.Namespace) -> None:
    """Split input CSV into sequential chunks of --size rows."""
    header = read_header(args.input, delimiter=args.delimiter)
    rows = stream_rows(args.input, delimiter=args.delimiter)
    out_dir = Path(args.outdir)
    out_dir.mkdir(parents=True, exist_ok=True)
    for idx, chunk in enumerate(split_evenly(rows, args.size), start=1):
        out_path = out_dir / f"chunk_{idx:04d}.csv"
        with open(out_path, "w", newline="", encoding="utf-8") as fh:
            writer = csv.DictWriter(fh, fieldnames=header, delimiter=args.delimiter)
            writer.writeheader()
            writer.writerows(chunk)
    print(f"Wrote {idx} chunk file(s) to {out_dir}", file=sys.stderr)


def register_split_parser(subparsers) -> None:
    # split-by
    p_by = subparsers.add_parser("split-by", help="Split CSV by column value")
    p_by.add_argument("input", help="Input CSV file")
    p_by.add_argument("--column", required=True, help="Column to split on")
    p_by.add_argument("--outdir", default=".", help="Output directory")
    p_by.add_argument("--delimiter", default=",")
    p_by.add_argument("--max-groups", type=int, default=0, dest="max_groups")
    p_by.set_defaults(func=cmd_split_by)

    # split-chunk
    p_ch = subparsers.add_parser("split-chunk", help="Split CSV into equal-sized chunks")
    p_ch.add_argument("input", help="Input CSV file")
    p_ch.add_argument("--size", type=int, required=True, help="Rows per chunk")
    p_ch.add_argument("--outdir", default=".", help="Output directory")
    p_ch.add_argument("--delimiter", default=",")
    p_ch.set_defaults(func=cmd_split_chunk)
