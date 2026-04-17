"""csv-surgeon: surgical in-place edits and transforms on large CSV files."""

from csv_surgeon.reader import stream_rows, read_header
from csv_surgeon.writer import write_rows, transform_inplace
from csv_surgeon.filter import (
    filter_rows, filter_by_value, filter_by_contains, filter_columns, drop_empty
)
from csv_surgeon.transform import apply_transforms, rename_columns, add_column, strip_whitespace
from csv_surgeon.sort import sort_rows, sort_rows_multi
from csv_surgeon.dedupe import dedupe_rows, count_duplicates
from csv_surgeon.stats import column_stats, multi_column_stats
from csv_surgeon.join import inner_join, left_join
from csv_surgeon.pivot import pivot_rows, melt_rows
from csv_surgeon.sample import sample_rows, sample_fraction, systematic_sample
from csv_surgeon.validate import validate_rows
from csv_surgeon.rename import rename_headers, reorder_columns, select_columns, drop_columns
from csv_surgeon.slice import head_rows, tail_rows, slice_rows
from csv_surgeon.fill import fill_value, fill_forward, fill_backward, fill_mean
from csv_surgeon.cast import cast_columns
from csv_surgeon.diff import diff_rows, diff_summary

__all__ = [
    "stream_rows", "read_header",
    "write_rows", "transform_inplace",
    "filter_rows", "filter_by_value", "filter_by_contains", "filter_columns", "drop_empty",
    "apply_transforms", "rename_columns", "add_column", "strip_whitespace",
    "sort_rows", "sort_rows_multi",
    "dedupe_rows", "count_duplicates",
    "column_stats", "multi_column_stats",
    "inner_join", "left_join",
    "pivot_rows", "melt_rows",
    "sample_rows", "sample_fraction", "systematic_sample",
    "validate_rows",
    "rename_headers", "reorder_columns", "select_columns", "drop_columns",
    "head_rows", "tail_rows", "slice_rows",
    "fill_value", "fill_forward", "fill_backward", "fill_mean",
    "cast_columns",
    "diff_rows", "diff_summary",
]
