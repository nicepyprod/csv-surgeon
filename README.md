# csv-surgeon

> Surgical in-place edits and transforms on large CSV files without loading them fully into memory.

---

## Installation

```bash
pip install csv-surgeon
```

Or install from source:

```bash
git clone https://github.com/yourname/csv-surgeon.git
cd csv-surgeon && pip install -e .
```

---

## Usage

```bash
# Delete rows where column "status" equals "inactive"
csv-surgeon delete --file data.csv --where "status == inactive"

# Rename a column
csv-surgeon rename --file data.csv --column "old_name" --to "new_name"

# Transform values in a column using a Python expression
csv-surgeon transform --file data.csv --column "price" --expr "float(value) * 1.1"

# Filter and write matching rows to a new file
csv-surgeon filter --file data.csv --where "country == US" --out filtered.csv

# Preview the first 10 rows without loading the full file
csv-surgeon peek --file data.csv --rows 10

# Count rows matching a condition
csv-surgeon count --file data.csv --where "status == active"
```

All operations are **streaming** — csv-surgeon processes files line by line, making it suitable for files too large to fit in memory.

---

## Why csv-surgeon?

- ✅ Handles multi-GB CSV files with constant memory usage
- ✅ In-place edits with safe atomic writes
- ✅ Simple, composable CLI interface
- ✅ No pandas or heavy dependencies required

---

## License

MIT © 2024 [yourname](https://github.com/yourname)
