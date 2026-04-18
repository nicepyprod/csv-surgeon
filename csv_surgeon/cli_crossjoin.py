"""CLI commands for cross-join, semi-join, and anti-join."""
import argparse
import csv
import sys
from csv_surgeon.crossjoin import cross_join, semi_join, anti_join
from csv_surgeon.reader import stream_rows


def _load(path: str):
    return list(stream_rows(path))


def cmd_crossjoin(args: argparse.Namespace) -> None:
    left_rows = _load(args.left)
    right_rows = _load(args.right)
    rows = list(cross_join(left_rows, right_rows,
                           left_prefix=args.left_prefix,
                           right_prefix=args.right_prefix))
    if not rows:
        return
    writer = csv.DictWriter(sys.stdout, fieldnames=list(rows[0].keys()))
    writer.writeheader()
    writer.writerows(rows)


def cmd_semijoin(args: argparse.Namespace) -> None:
    left_rows = _load(args.left)
    right_rows = _load(args.right)
    fn = anti_join if args.anti else semi_join
    rows = list(fn(left_rows, right_rows, key=args.key,
                   right_key=args.right_key or None))
    if not rows:
        return
    writer = csv.DictWriter(sys.stdout, fieldnames=list(rows[0].keys()))
    writer.writeheader()
    writer.writerows(rows)


def register_crossjoin_parser(sub: argparse._SubParsersAction) -> None:
    p_cross = sub.add_parser("crossjoin", help="Cartesian product of two CSVs")
    p_cross.add_argument("left")
    p_cross.add_argument("right")
    p_cross.add_argument("--left-prefix", default="l_", dest="left_prefix")
    p_cross.add_argument("--right-prefix", default="r_", dest="right_prefix")
    p_cross.set_defaults(func=cmd_crossjoin)

    p_semi = sub.add_parser("semijoin", help="Semi/anti join two CSVs on a key")
    p_semi.add_argument("left")
    p_semi.add_argument("right")
    p_semi.add_argument("--key", required=True)
    p_semi.add_argument("--right-key", default="", dest="right_key")
    p_semi.add_argument("--anti", action="store_true",
                        help="Return rows NOT in right (anti-join)")
    p_semi.set_defaults(func=cmd_semijoin)
