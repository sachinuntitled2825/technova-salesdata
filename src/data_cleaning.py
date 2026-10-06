"""Data loading and cleaning utilities for the sales dataset.

The cleaning pipeline is defensive: every check reports what it found, and
rows are only removed when the missing/invalid value makes analysis impossible
(e.g. missing sales amount). Legitimate negative profits (losses) are kept.
"""

from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATA_PATH = PROJECT_ROOT / "data" / "sales_data.csv"

# Columns that must always be present to run the analysis
EXPECTED_COLUMNS = [
    "Order_ID",
    "Order_Date",
    "Customer_Name",
    "Product",
    "Category",
    "Region",
    "Quantity",
    "Sales",
    "Discount",
    "Profit",
]

NUMERIC_COLUMNS = ["Quantity", "Sales", "Discount", "Profit"]

# Columns where a missing value makes the record unusable for this analysis
ESSENTIAL_COLUMNS = [
    "Order_Date",
    "Product",
    "Category",
    "Region",
    "Quantity",
    "Sales",
    "Profit",
]


def load_dataset(path: str | Path = DEFAULT_DATA_PATH) -> pd.DataFrame:
    """Load the raw sales CSV. Raises a clear error if the file is missing."""
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(
            f"Dataset not found at '{path}'.\n"
            "Generate the sample dataset first:  python src/generate_dataset.py"
        )
    return pd.read_csv(path)


def profile_dataset(df: pd.DataFrame) -> dict:
    """Collect a quality profile of a dataset (rows, types, missing, duplicates)."""
    missing = df.isna().sum()
    return {
        "rows": int(len(df)),
        "columns": int(df.shape[1]),
        "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()},
        "missing_by_column": {col: int(count) for col, count in missing.items() if count > 0},
        "missing_cells": int(missing.sum()),
        "duplicate_rows": int(df.duplicated().sum()),
    }


def clean_sales_data(df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """Clean the raw sales dataset and return (cleaned_df, cleaning_report).

    Steps performed (in order):
      1. Validate required columns
      2. Trim whitespace in text columns
      3. Convert Order_Date to datetime (unparseable dates -> dropped)
      4. Coerce numeric columns; drop rows missing essential values
      5. Fill non-essential missing values (Customer_Name, Discount)
      6. Remove exact duplicate records
      7. Remove invalid records (Quantity/Sales <= 0, Discount outside 0-1)
      8. Keep negative profits (real losses) but report them
    """
    report: dict = {"steps": [], "notes": []}

    if df.empty:
        raise ValueError("The loaded dataset is empty - nothing to clean.")

    missing_cols = [c for c in EXPECTED_COLUMNS if c not in df.columns]
    if missing_cols:
        raise ValueError(f"Dataset is missing required columns: {missing_cols}")

    # ---- Snapshot BEFORE cleaning -------------------------------------
    before = profile_dataset(df)
    working = df.copy()
    report["before"] = before

    # ---- Step 2: trim whitespace in text columns -----------------------
    text_cols = [c for c in ["Order_ID", "Customer_Name", "Product", "Category", "Region"]
                 if c in working.columns]
    trimmed = 0
    for col in text_cols:
        original = working[col].astype("string")
        stripped = original.str.strip().replace("", pd.NA)
        diff = original.fillna("__NA__") != stripped.fillna("__NA__")
        trimmed += int(diff.sum())
        working[col] = stripped
    report["steps"].append(f"Trimmed whitespace in text columns ({trimmed} cells adjusted).")

    # ---- Step 3: Order_Date -> datetime --------------------------------
    raw_date_missing = int(working["Order_Date"].isna().sum())
    working["Order_Date"] = pd.to_datetime(working["Order_Date"], errors="coerce")
    bad_dates = int(working["Order_Date"].isna().sum()) - raw_date_missing
    n_before = len(working)
    working = working.dropna(subset=["Order_Date"])
    dropped_dates = n_before - len(working)
    report["steps"].append(
        f"Converted Order_Date to datetime: {dropped_dates} row(s) dropped "
        f"({bad_dates} unparseable date string(s), {raw_date_missing} already missing)."
    )

    # ---- Step 4: numeric coercion + essential missing values ------------
    for col in NUMERIC_COLUMNS:
        working[col] = pd.to_numeric(working[col], errors="coerce")

    coerced_missing = int(working[NUMERIC_COLUMNS].isna().sum().sum())
    report["steps"].append(f"Coerced numeric columns to number types ({coerced_missing} non-numeric/missing values found).")

    n_before = len(working)
    working = working.dropna(subset=ESSENTIAL_COLUMNS)
    dropped_essential = n_before - len(working)
    report["steps"].append(
        f"Dropped {dropped_essential} row(s) missing essential values "
        f"({', '.join(ESSENTIAL_COLUMNS)})."
    )

    # ---- Step 5: fill non-essential missing values ----------------------
    if working["Customer_Name"].isna().any():
        n_fill = int(working["Customer_Name"].isna().sum())
        working["Customer_Name"] = working["Customer_Name"].fillna("Unknown Customer")
        report["steps"].append(f"Filled {n_fill} missing Customer_Name value(s) with 'Unknown Customer'.")

    if working["Discount"].isna().any():
        n_fill = int(working["Discount"].isna().sum())
        median_discount = float(working["Discount"].median())
        working["Discount"] = working["Discount"].fillna(round(median_discount, 4))
        report["steps"].append(
            f"Filled {n_fill} missing Discount value(s) with the median discount ({median_discount:.2%})."
        )

    # ---- Step 6: drop exact duplicates ----------------------------------
    n_before = len(working)
    working = working.drop_duplicates()
    dropped_dupes = n_before - len(working)
    report["steps"].append(f"Removed {dropped_dupes} exact duplicate record(s).")

    # ---- Step 7: invalid records ----------------------------------------
    invalid_qty = int((working["Quantity"] <= 0).sum())
    invalid_sales = int((working["Sales"] <= 0).sum())
    invalid_discount = int(((working["Discount"] < 0) | (working["Discount"] > 1)).sum())
    invalid_mask = (
        (working["Quantity"] <= 0)
        | (working["Sales"] <= 0)
        | (working["Discount"] < 0)
        | (working["Discount"] > 1)
    )
    n_before = len(working)
    working = working[~invalid_mask].copy()
    dropped_invalid = n_before - len(working)
    report["steps"].append(
        f"Removed {dropped_invalid} invalid record(s): {invalid_qty} with Quantity <= 0, "
        f"{invalid_sales} with Sales <= 0, {invalid_discount} with Discount outside [0, 1]."
    )

    # ---- Step 8: keep legitimate negative profits ------------------------
    loss_making = int((working["Profit"] < 0).sum())
    report["notes"].append(
        f"{loss_making} order(s) have negative Profit (genuine losses). "
        "These are valid business records and were KEPT for analysis."
    )

    # ---- Final tidy-up ----------------------------------------------------
    working["Quantity"] = working["Quantity"].round().astype("int64")
    working["Order_Date"] = pd.to_datetime(working["Order_Date"])
    working = working.sort_values("Order_Date").reset_index(drop=True)
    working = working[EXPECTED_COLUMNS]

    after = profile_dataset(working)
    report["after"] = after
    report["rows_removed"] = before["rows"] - after["rows"]
    report["rows_dropped_by_duplicates"] = dropped_dupes
    report["loss_making_orders"] = loss_making

    return working, report


def format_cleaning_report(report: dict) -> str:
    """Render the cleaning report as human-readable text."""
    lines = [
        "=" * 70,
        "DATA CLEANING REPORT",
        "=" * 70,
        "",
        "BEFORE CLEANING",
        "-" * 70,
        f"  Rows              : {report['before']['rows']}",
        f"  Columns           : {report['before']['columns']}",
        f"  Missing cells     : {report['before']['missing_cells']}",
        f"  Duplicate rows    : {report['before']['duplicate_rows']}",
        f"  Data types        : {report['before']['dtypes']}",
        "",
        "CLEANING STEPS APPLIED",
        "-" * 70,
    ]
    for i, step in enumerate(report["steps"], start=1):
        lines.append(f"  {i}. {step}")
    lines += [
        "",
        "AFTER CLEANING",
        "-" * 70,
        f"  Rows              : {report['after']['rows']}",
        f"  Columns           : {report['after']['columns']}",
        f"  Missing cells     : {report['after']['missing_cells']}",
        f"  Duplicate rows    : {report['after']['duplicate_rows']}",
        f"  Data types        : {report['after']['dtypes']}",
        "",
        f"  Total rows removed: {report['rows_removed']}",
        "",
        "NOTES",
        "-" * 70,
    ]
    for note in report["notes"]:
        lines.append(f"  - {note}")
    lines += ["", "=" * 70]
    return "\n".join(lines)


def print_cleaning_summary(report: dict) -> None:
    """Print a compact before/after summary to the console."""
    b, a = report["before"], report["after"]
    print("\n--- Data cleaning summary -------------------------------------")
    print(f"  Rows      : {b['rows']} -> {a['rows']}  (-{report['rows_removed']})")
    print(f"  Missing   : {b['missing_cells']} -> {a['missing_cells']} cells")
    print(f"  Duplicates: {b['duplicate_rows']} -> {a['duplicate_rows']}")
    print("  Steps applied:")
    for step in report["steps"]:
        print(f"    - {step}")
    for note in report["notes"]:
        print(f"    - {note}")
    print("----------------------------------------------------------------\n")
