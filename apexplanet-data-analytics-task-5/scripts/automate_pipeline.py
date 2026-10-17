"""
automate_pipeline.py
====================
ApexPlanet Data Analytics Internship - Task 5 (Final Report, Automation & Presentation)

End-to-end automated pipeline for the Superstore sales dataset:

    1. Load     - find data/superstore_cleaned.csv by walking up from this script,
                  then parse the date columns.
    2. Clean    - de-duplicate, strip whitespace, coerce numerics, drop impossible
                  rows, flag missing values. Prints what it did (idempotent).
    3. KPIs     - compute the headline business KPIs and print them.
    4. Export   - write a multi-sheet Excel workbook (reports/kpis.xlsx).
    5. Summary  - write a timestamped run log (reports/pipeline_summary.txt).

Usage:
    python scripts/automate_pipeline.py
    python scripts/automate_pipeline.py --quiet        # only print the summary
    python scripts/automate_pipeline.py --excel-only   # skip the summary text file

The script always exits with code 0 on a successful run and prints a short
"PIPELINE OK" banner so the batch file / Task Scheduler can detect success.
"""

import argparse
import sys
import traceback
from datetime import datetime
from pathlib import Path

import pandas as pd

# ---------------------------------------------------------------------------
# Path handling
# ---------------------------------------------------------------------------
# Walk up from this script's folder to locate the repo root (the folder that
# contains "data/superstore_cleaned.csv"). This makes the script work no matter
# which working directory it is launched from.
SCRIPT_DIR = Path(__file__).resolve().parent          # .../task-5/scripts
TASK_DIR = SCRIPT_DIR.parent                           # .../task-5
REPORTS_DIR = TASK_DIR / "reports"


def find_dataset(start: Path) -> Path:
    """Walk up from `start` looking for data/superstore_cleaned.csv."""
    for folder in [start, *start.parents]:
        candidate = folder / "data" / "superstore_cleaned.csv"
        if candidate.is_file():
            return candidate
    raise FileNotFoundError(
        "Could not find data/superstore_cleaned.csv by walking up from "
        f"{start}"
    )


# ---------------------------------------------------------------------------
# Step 1 - Load
# ---------------------------------------------------------------------------
def load_data(path: Path) -> pd.DataFrame:
    """Read the CSV and parse the two date columns."""
    df = pd.read_csv(path)
    for col in ("Order Date", "Ship Date"):
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")
    return df


# ---------------------------------------------------------------------------
# Step 2 - Clean (idempotent)
# ---------------------------------------------------------------------------
def clean_data(df: pd.DataFrame, log) -> pd.DataFrame:
    """Clean the frame and report each action. Running twice is a no-op."""
    rows_before = len(df)
    log(f"Clean - rows before: {rows_before}")

    # 2a. Drop exact duplicate rows.
    before = len(df)
    df = df.drop_duplicates()
    log(f"Clean - dropped {before - len(df)} exact duplicate row(s)")

    # 2b. Strip leading/trailing whitespace from text (object) columns.
    text_cols = df.select_dtypes(include=["object", "str"]).columns
    for col in text_cols:
        df[col] = df[col].astype(str).str.strip()
    log(f"Clean - stripped whitespace from {len(text_cols)} text column(s)")

    # 2c. Coerce the numeric columns (bad values become NaN).
    numeric_cols = ["Sales", "Quantity", "Discount", "Profit"]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    log(f"Clean - coerced {len(numeric_cols)} numeric column(s)")

    # 2d. Drop rows with impossible values:
    #     Ship Date before Order Date, or negative Sales.
    bad_dates = 0
    if {"Order Date", "Ship Date"}.issubset(df.columns):
        bad_dates = int((df["Ship Date"] < df["Order Date"]).sum())
    neg_sales = int((df["Sales"] < 0).sum()) if "Sales" in df.columns else 0
    if bad_dates or neg_sales:
        mask = pd.Series(False, index=df.index)
        if {"Order Date", "Ship Date"}.issubset(df.columns):
            mask |= df["Ship Date"] < df["Order Date"]
        if "Sales" in df.columns:
            mask |= df["Sales"] < 0
        df = df.loc[~mask].copy()
    log(f"Clean - dropped {bad_dates} bad-date row(s) and {neg_sales} negative-sales row(s)")

    # 2e. Flag / fill missing values in the critical numeric columns.
    missing = int(df[numeric_cols].isna().sum().sum()) if numeric_cols else 0
    if missing:
        df[numeric_cols] = df[numeric_cols].fillna(0)
        log(f"Clean - filled {missing} missing numeric value(s) with 0")
    else:
        log("Clean - no missing values in critical numeric columns")

    rows_after = len(df)
    log(f"Clean - rows after: {rows_after} (removed {rows_before - rows_after})")
    return df.reset_index(drop=True)


# ---------------------------------------------------------------------------
# Step 3 - KPIs
# ---------------------------------------------------------------------------
def compute_kpis(df: pd.DataFrame) -> dict:
    """Compute the headline KPIs from the cleaned frame."""
    total_sales = df["Sales"].sum()
    total_profit = df["Profit"].sum()
    margin = total_profit / total_sales * 100 if total_sales else 0.0

    kpis = {
        "Total Sales": round(total_sales, 2),
        "Total Profit": round(total_profit, 2),
        "Profit Margin %": round(margin, 2),
        "Orders": int(df["Order ID"].nunique()),
        "Customers": int(df["Customer ID"].nunique()),
        "Products": int(df["Product ID"].nunique()),
        "Average Order Value": round(total_sales / df["Order ID"].nunique(), 2),
        "Average Discount %": round(df["Discount"].mean() * 100, 2),
    }
    return kpis


def compute_breakdowns(df: pd.DataFrame) -> dict:
    """Build the supporting tables used for the Excel sheets."""
    by_cat = (
        df.groupby("Category")
        .agg(Sales=("Sales", "sum"), Profit=("Profit", "sum"),
             Quantity=("Quantity", "sum"))
        .round(2)
        .reset_index()
    )
    by_region = (
        df.groupby("Region")
        .agg(Sales=("Sales", "sum"), Profit=("Profit", "sum"),
             Orders=("Order ID", "nunique"))
        .round(2)
        .reset_index()
    )
    by_region["Profit Margin %"] = (by_region["Profit"] / by_region["Sales"] * 100).round(2)

    # Monthly sales series from the parsed Order Date.
    monthly = (
        df.dropna(subset=["Order Date"])
        .assign(MonthPeriod=lambda d: d["Order Date"].dt.to_period("M").astype(str))
        .groupby("MonthPeriod")
        .agg(Sales=("Sales", "sum"), Profit=("Profit", "sum"))
        .round(2)
        .reset_index()
    )

    top_products = (
        df.groupby("Product Name")
        .agg(Sales=("Sales", "sum"), Profit=("Profit", "sum"))
        .round(2)
        .sort_values("Sales", ascending=False)
        .head(10)
        .reset_index()
    )
    top_customers = (
        df.groupby("Customer Name")
        .agg(Sales=("Sales", "sum"), Profit=("Profit", "sum"),
             Orders=("Order ID", "nunique"))
        .round(2)
        .sort_values("Sales", ascending=False)
        .head(10)
        .reset_index()
    )
    return {
        "Sales_by_Category": by_cat,
        "Sales_by_Region": by_region,
        "Monthly_Sales": monthly,
        "Top10_Products": top_products,
        "Top10_Customers": top_customers,
    }


# The 4 customer segments were produced by the Task 4 K-Means model. They are
# recorded here as static reference data (recomputing KMeans is unnecessary).
CUSTOMER_SEGMENTS = pd.DataFrame([
    {"Segment": "Champions", "Customers": 264, "Share %": 33.3,
     "Avg Recency (days)": 81, "Avg Orders": 8.9,
     "Avg Monetary ($)": 5024.46, "Avg Discount %": 16},
    {"Segment": "Steady core", "Customers": 273, "Share %": 34.4,
     "Avg Recency (days)": 97, "Avg Orders": 5.4,
     "Avg Monetary ($)": 2014.00, "Avg Discount %": 10},
    {"Segment": "Discount seekers", "Customers": 168, "Share %": 21.2,
     "Avg Recency (days)": 111, "Avg Orders": 5.2,
     "Avg Monetary ($)": 1645.11, "Avg Discount %": 26},
    {"Segment": "Dormant / at risk", "Customers": 88, "Share %": 11.1,
     "Avg Recency (days)": 574, "Avg Orders": 3.7,
     "Avg Monetary ($)": 1642.54, "Avg Discount %": 15},
])


# ---------------------------------------------------------------------------
# Step 4 - Export Excel
# ---------------------------------------------------------------------------
def export_excel(kpis: dict, breakdowns: dict, out_path: Path) -> None:
    """Write the multi-sheet KPI workbook."""
    kpi_df = pd.DataFrame(
        [{"KPI": k, "Value": v} for k, v in kpis.items()]
    )
    with pd.ExcelWriter(out_path, engine="openpyxl") as writer:
        kpi_df.to_excel(writer, sheet_name="KPIs", index=False)
        breakdowns["Sales_by_Category"].to_excel(writer, sheet_name="Sales_by_Category", index=False)
        breakdowns["Sales_by_Region"].to_excel(writer, sheet_name="Sales_by_Region", index=False)
        breakdowns["Monthly_Sales"].to_excel(writer, sheet_name="Monthly_Sales", index=False)
        breakdowns["Top10_Products"].to_excel(writer, sheet_name="Top10_Products", index=False)
        breakdowns["Top10_Customers"].to_excel(writer, sheet_name="Top10_Customers", index=False)
        CUSTOMER_SEGMENTS.to_excel(writer, sheet_name="Customer_Segments", index=False)


# ---------------------------------------------------------------------------
# Step 5 - Summary text
# ---------------------------------------------------------------------------
def write_summary(kpis: dict, rows_in: int, rows_out: int, dataset: Path,
                  outputs: list, out_path: Path) -> str:
    """Build and write the timestamped run log; return it as a string."""
    now = datetime.now()
    lines = []
    lines.append("=" * 70)
    lines.append("APEXPLANET TASK 5 - AUTOMATED PIPELINE RUN LOG")
    lines.append("=" * 70)
    lines.append(f"Run timestamp : {now.strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append(f"Dataset       : {dataset}")
    lines.append("")
    lines.append("DATA")
    lines.append(f"  Rows in  : {rows_in}")
    lines.append(f"  Rows out : {rows_out}")
    lines.append("")
    lines.append("KEY PERFORMANCE INDICATORS")
    for key, value in kpis.items():
        lines.append(f"  {key:<22}: {value}")
    lines.append("")
    lines.append("OUTPUT FILES")
    for path in outputs:
        size = path.stat().st_size if path.exists() else 0
        lines.append(f"  {path.name:<32} {size} bytes")
    lines.append("")
    lines.append("STATUS: PIPELINE OK")
    lines.append("=" * 70)

    text = "\n".join(lines)
    out_path.write_text(text, encoding="utf-8")
    return text


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def parse_args(argv=None):
    parser = argparse.ArgumentParser(description="Superstore automated pipeline (Task 5).")
    parser.add_argument("--quiet", action="store_true",
                        help="Only print the final summary block.")
    parser.add_argument("--excel-only", action="store_true",
                        help="Skip writing reports/pipeline_summary.txt.")
    return parser.parse_args(argv)


def main(argv=None) -> int:
    args = parse_args(argv)

    def log(msg: str) -> None:
        if not args.quiet:
            print(msg)

    try:
        REPORTS_DIR.mkdir(parents=True, exist_ok=True)

        # 1. Load
        dataset = find_dataset(SCRIPT_DIR)
        log(f"Load  - reading {dataset}")
        df = load_data(dataset)
        rows_in = len(df)
        log(f"Load  - loaded {rows_in} rows x {df.shape[1]} columns")

        # 2. Clean
        df = clean_data(df, log)
        rows_out = len(df)
        cleaned_path = REPORTS_DIR / "superstore_cleaned_pipeline.csv"
        df.to_csv(cleaned_path, index=False)
        log(f"Clean - wrote cleaned output to {cleaned_path.name}")

        # 3. KPIs
        kpis = compute_kpis(df)
        log("KPIs")
        for key, value in kpis.items():
            log(f"  {key:<22}: {value}")

        breakdowns = compute_breakdowns(df)

        # 4. Export Excel
        excel_path = REPORTS_DIR / "kpis.xlsx"
        export_excel(kpis, breakdowns, excel_path)
        log(f"Export - wrote workbook {excel_path.name} "
            f"({len(breakdowns) + 2} sheets)")

        # 5. Summary
        outputs = [cleaned_path, excel_path]
        if not args.excel_only:
            summary_path = REPORTS_DIR / "pipeline_summary.txt"
            text = write_summary(kpis, rows_in, rows_out, dataset, outputs, summary_path)
            outputs.append(summary_path)
            if args.quiet:
                print(text)
            log(f"Summary - wrote {summary_path.name}")
        else:
            if args.quiet:
                print("PIPELINE OK (excel-only)")

        print("\nPIPELINE OK")
        return 0

    except Exception:
        print("PIPELINE FAILED", file=sys.stderr)
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
