"""CLI sub-command: detect column types."""
from __future__ import annotations
import argparse
import csv
import json
import sys

from csv_surgeon.reader import stream_rows
from csv_surgeon.typecast_detect import type_report


def cmd_detect(args: argparse.Namespace) -> None:
    rows = stream_rows(args.input, delimiter=args.delimiter)
    report = type_report(rows, sample=args.sample)

    if args.format == 'json':
        print(json.dumps(report, indent=2))
    else:
        writer = csv.DictWriter(
            sys.stdout, fieldnames=['column', 'inferred_type'], lineterminator='\n'
        )
        writer.writeheader()
        writer.writerows(report)


def register_detect_parser(sub: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    p = sub.add_parser('detect-types', help='Infer column data types from a sample of rows')
    p.add_argument('input', help='Input CSV file')
    p.add_argument('--delimiter', default=',', help='Field delimiter (default: ,)')
    p.add_argument(
        '--sample', type=int, default=500,
        help='Number of rows to sample (default: 500)'
    )
    p.add_argument(
        '--format', choices=['csv', 'json'], default='csv',
        help='Output format (default: csv)'
    )
    p.set_defaults(func=cmd_detect)
