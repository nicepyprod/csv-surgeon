"""csv-surgeon: surgical in-place edits and transforms on large CSV files."""

from csv_surgeon.filter import (
    drop_empty,
    filter_by_contains,
    filter_by_value,
    filter_columns,
    filter_rows,
)
from csv_surgeon.reader import read_header, stream_rows
from csv_surgeon.writer import transform_inplace, write_rows

__all__ = [
    "stream_rows",
    "read_header",
    "write_rows",
    "transform_inplace",
    "filter_rows",
    "filter_by_value",
    "filter_by_contains",
    "filter_columns",
    "drop_empty",
]

__version__ = "0.1.0"
