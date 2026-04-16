"""Pivot and unpivot (melt) operations for CSV rows."""
from typing import Iterator, List, Dict, Iterable


def pivot_rows(
    rows: Iterable[Dict[str, str]],
    index: str,
    columns: str,
    values: str,
    aggfunc: str = "first",
) -> List[Dict[str, str]]:
    """Pivot rows: unique values of `columns` field become new column headers.

    Args:
        rows: iterable of dicts
        index: field to use as the row identifier
        columns: field whose values become column names
        values: field whose values fill the new columns
        aggfunc: 'first' or 'last' when multiple values exist
    """
    from collections import defaultdict

    # {index_val: {col_val: value}}
    table: Dict[str, Dict[str, str]] = defaultdict(dict)
    col_order: List[str] = []

    for row in rows:
        idx = row.get(index, "")
        col = row.get(columns, "")
        val = row.get(values, "")
        if col not in col_order:
            col_order.append(col)
        if aggfunc == "last" or col not in table[idx]:
            table[idx][col] = val

    result = []
    for idx_val, col_map in table.items():
        record: Dict[str, str] = {index: idx_val}
        for col in col_order:
            record[col] = col_map.get(col, "")
        result.append(record)
    return result


def melt_rows(
    rows: Iterable[Dict[str, str]],
    id_vars: List[str],
    value_vars: List[str],
    var_name: str = "variable",
    value_name: str = "value",
) -> Iterator[Dict[str, str]]:
    """Unpivot (melt) rows: turn `value_vars` columns into rows.

    Args:
        rows: iterable of dicts
        id_vars: columns to keep as identifiers
        value_vars: columns to unpivot
        var_name: name for the new variable column
        value_name: name for the new value column
    """
    for row in rows:
        base = {k: row.get(k, "") for k in id_vars}
        for var in value_vars:
            record = dict(base)
            record[var_name] = var
            record[value_name] = row.get(var, "")
            yield record
