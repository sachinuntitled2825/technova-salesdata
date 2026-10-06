"""End-to-end pipeline for the Sales Data Analysis project.

Runs the full workflow:
    load raw data -> clean -> analyse -> visualise -> write reports/outputs

Usage (from the project root):
    python src/main.py
"""

import sys
from pathlib import Path

# Allow running this file directly:  python src/main.py
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Windows consoles default to cp1252, which cannot display the ₹ symbol
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

import matplotlib  # noqa: E402  (backend must be chosen before pyplot import)
import pandas as pd  # noqa: E402

matplotlib.use("Agg")

from src import analysis, data_cleaning, visualization  # noqa: E402

OUTPUT_DIR = PROJECT_ROOT / "outputs"
REPORT_DIR = OUTPUT_DIR / "reports"
CHART_DIR = OUTPUT_DIR / "charts"


def write_analysis_report(
    path: Path,
    kpis: dict,
    category_perf: pd.DataFrame,
    region_perf: pd.DataFrame,
    top_sales: pd.DataFrame,
    top_profit: pd.DataFrame,
    worst: pd.DataFrame,
    monthly: pd.DataFrame,
    findings: list[str],
    recommendations: list[str],
) -> None:
    """Write a Markdown report containing every analysis table and insight."""

    def _table(frame) -> str:
        return analysis.to_markdown_table(frame)

    lines = [
        "# Sales Data Analysis - Report",
        "",
        "All values below are calculated dynamically from the cleaned dataset.",
        "",
        "## KPI Summary",
        "",
        analysis.to_markdown_table(analysis.kpi_summary_frame(kpis)),
        "",
        "## Sales & Profit by Category",
        "",
        _table(category_perf.round(2)),
        "",
        "## Sales & Profit by Region",
        "",
        _table(region_perf.round(2)),
        "",
        "## Top 10 Products by Sales",
        "",
        _table(top_sales.round(2)),
        "",
        "## Top 10 Products by Profit",
        "",
        _table(top_profit.round(2)),
        "",
        "## 5 Least Profitable Products",
        "",
        _table(worst.round(2)),
        "",
        "## Monthly Trend",
        "",
        _table(monthly[["Month_Label", "Sales", "Profit", "Orders", "Quantity", "Profit Margin (%)"]].round(2)),
        "",
        "## Key Findings",
        "",
    ]
    lines += [f"- {item}" for item in findings]
    lines += ["", "## Business Recommendations", ""]
    lines += [f"- {item}" for item in recommendations]
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    print("=" * 70)
    print("SALES DATA ANALYSIS - PIPELINE")
    print("=" * 70)

    # 1. Load and clean ----------------------------------------------------
    raw_df = data_cleaning.load_dataset()
    print(f"\nLoaded raw dataset: {raw_df.shape[0]} rows x {raw_df.shape[1]} columns")

    cleaned_df, cleaning_report = data_cleaning.clean_sales_data(raw_df)
    data_cleaning.print_cleaning_summary(cleaning_report)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    cleaned_path = OUTPUT_DIR / "sales_data_cleaned.csv"
    cleaned_df.to_csv(cleaned_path, index=False)
    (REPORT_DIR / "data_cleaning_report.txt").write_text(
        data_cleaning.format_cleaning_report(cleaning_report), encoding="utf-8"
    )
    print(f"Cleaned dataset saved to: {cleaned_path}")

    # 2. Analyse -----------------------------------------------------------
    kpis = analysis.compute_kpis(cleaned_df)
    category_perf = analysis.sales_profit_by(cleaned_df, "Category")
    region_perf = analysis.sales_profit_by(cleaned_df, "Region")
    top_sales = analysis.top_products(cleaned_df, metric="Sales", n=10)
    top_profit = analysis.top_products(cleaned_df, metric="Profit", n=10)
    worst_products = analysis.worst_products(cleaned_df, n=5)
    monthly = analysis.monthly_trends(cleaned_df)

    summary_path = OUTPUT_DIR / "summary.csv"
    analysis.kpi_summary_frame(kpis).to_csv(summary_path, index=False)
    print(f"KPI summary saved to: {summary_path}")

    category_perf.round(2).to_csv(REPORT_DIR / "sales_by_category.csv", index=False)
    region_perf.round(2).to_csv(REPORT_DIR / "sales_by_region.csv", index=False)
    top_sales.round(2).to_csv(REPORT_DIR / "top10_products_by_sales.csv", index=False)
    top_profit.round(2).to_csv(REPORT_DIR / "top10_products_by_profit.csv", index=False)
    monthly_trend_cols = ["Month_Label", "Sales", "Profit", "Orders", "Quantity", "Profit Margin (%)"]
    monthly[monthly_trend_cols].round(2).to_csv(REPORT_DIR / "monthly_trends.csv", index=False)

    findings = analysis.generate_key_findings(
        cleaned_df, kpis, category_perf, region_perf, top_sales, top_profit, monthly
    )
    recommendations = analysis.generate_recommendations(
        cleaned_df, kpis, category_perf, region_perf, top_sales, monthly
    )

    report_path = REPORT_DIR / "analysis_report.md"
    write_analysis_report(
        report_path, kpis, category_perf, region_perf, top_sales, top_profit,
        worst_products, monthly, findings, recommendations,
    )
    print(f"Analysis report saved to: {report_path}")

    # 3. Visualise ---------------------------------------------------------
    charts = visualization.create_all_charts(
        category_perf, region_perf, top_sales, top_profit, monthly, CHART_DIR
    )
    print(f"\nGenerated {len(charts)} charts in: {CHART_DIR}")

    # 4. Console summary ---------------------------------------------------
    print("\n--- KPI SUMMARY " + "-" * 53)
    for name, value in kpis.items():
        if isinstance(value, float):
            print(f"  {name:<24}: {value:,.2f}")
        else:
            print(f"  {name:<24}: {value}")

    print("\n--- KEY FINDINGS " + "-" * 53)
    for item in findings:
        print(f"  - {item}")

    print("\n--- RECOMMENDATIONS " + "-" * 49)
    for item in recommendations:
        print(f"  - {item}")

    print("\nPipeline completed successfully.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
