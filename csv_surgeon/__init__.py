"""csv-surgeon: surgical in-place edits and transforms on large CSV files."""

from csv_surgeon.reader import stream_rows, read_header
from csv_surgeon.writer import write_rows, transform_inplace
from csv_surgeon.filter import (
    filter_rows,
    filter_by_value,
    filter_by_contains,
    filter_columns,
    drop_empty,
)
from csv_surgeon.transform import (
    apply_transforms,
    rename_columns,
    add_column,
    strip_whitespace,
)
from csv_surgeon.sort import sort_rows, sort_rows_multi
from csv_surgeon.dedupe import dedupe_rows, count_duplicates
from csv_surgeon.stats import column_stats, multi_column_stats
from csv_surgeon.join import inner_join, left_join

__all__ = [
    "stream_rows", "read_header",
    "write_rows", "transform_inplace",
    "filter_rows", "filter_by_value", "filter_by_contains",
    "filter_columns", "drop_empty",
    "apply_transforms", "rename_columns", "add_column", "strip_whitespace",
    "sort_rows", "sort_rows_multi",
    "dedupe_rows", "count_duplicates",
    "column_stats", "multi_column_stats",
    "inner_join", "left_join",
]
