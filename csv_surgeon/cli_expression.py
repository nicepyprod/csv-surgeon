"""CLI integration for the expression/formula column module."""

from __future__ import annotations

import argparse
import csv
import sys
from typing import List

from .expression import add_expression_column, multi_expression
from .reader import stream_rows
from .writer import write_rows


def cmd_expression(args: argparse.Namespace) -> None:
    """Add one or more computed columns to a CSV file using safe expressions.

    Each expression is evaluated per-row with the row dict available as
    variables.  Results are written to *args.output* (default: stdout).

    Example
    -------
    csv-surgeon expression data.csv \\
        --expr total="price * quantity" \\
        --expr discount="total * 0.1" \\
        --output out.csv
    """
    # Parse "name=formula" pairs from the repeated --expr flag
    exprs: List[tuple[str, str]] = []
    for raw in args.expr:
        if "=" not in raw:
            print(
                f"[error] --expr value must be in 'name=formula' form, got: {raw!r}",
                file=sys.stderr,
            )
            sys.exit(1)
        col, _, formula = raw.partition("=")
        exprs.append((col.strip(), formula.strip()))

    rows = list(stream_rows(args.input, delimiter=args.delimiter))
    if not rows:
        return

    if len(exprs) == 1:
        col, formula = exprs[0]
        result = list(
            add_expression_column(
                iter(rows),
                col,
                formula,
                coerce_numeric=not args.no_coerce,
            )
        )
    else:
        # multi_expression applies each formula in sequence so later
        # formulas can reference columns added by earlier ones.
        result = list(
            multi_expression(
                iter(rows),
                exprs,
                coerce_numeric=not args.no_coerce,
            )
        )

    if args.output:
        write_rows(args.output, result, delimiter=args.delimiter)
    else:
        if not result:
            return
        writer = csv.DictWriter(
            sys.stdout,
            fieldnames=list(result[0].keys()),
            lineterminator="\n",
            delimiter=args.delimiter,
        )
        writer.writeheader()
        writer.writerows(result)


def register_expression_parser(subparsers: argparse._SubParsersAction) -> None:  # noqa: SLF001
    """Attach the *expression* sub-command to *subparsers*."""
    p = subparsers.add_parser(
        "expression",
        help="Add computed columns via safe Python expressions.",
        description=(
            "Evaluate one or more Python-like formulas per row and append the "
            "results as new columns.  Row values are available by column name.  "
            "Basic math, string ops, and built-ins (abs, round, len, …) are "
            "supported; imports and attribute access are blocked for safety."
        ),
    )
    p.add_argument("input", help="Path to the input CSV file.")
    p.add_argument(
        "--expr",
        metavar="NAME=FORMULA",
        action="append",
        default=[],
        required=True,
        help=(
            "Column name and formula separated by '='.  "
            "May be repeated to add multiple columns in order."
        ),
    )
    p.add_argument(
        "--delimiter",
        "-d",
        default=",",
        help="Field delimiter (default: comma).",
    )
    p.add_argument(
        "--no-coerce",
        action="store_true",
        default=False,
        help="Keep result values as strings instead of coercing to int/float.",
    )
    p.add_argument(
        "--output",
        "-o",
        default=None,
        help="Write output to this file instead of stdout.",
    )
    p.set_defaults(func=cmd_expression)
