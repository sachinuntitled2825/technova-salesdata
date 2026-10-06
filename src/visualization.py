"""Professional Matplotlib/Seaborn charts for the sales analysis.

Every chart is titled, labelled, money-formatted and saved as a PNG file in
outputs/charts/.
"""

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from matplotlib.dates import DateFormatter
from matplotlib.ticker import FuncFormatter

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CHART_DIR = PROJECT_ROOT / "outputs" / "charts"

# Consistent, professional look
COLORS = {
    "primary": "#2E86AB",
    "secondary": "#A23B72",
    "positive": "#1B7F3B",
    "negative": "#C0392B",
    "neutral": "#F18F01",
}
CATEGORY_PALETTE = ["#2E86AB", "#A23B72", "#F18F01", "#1B7F3B", "#7B2CBF"]
REGION_PALETTE = ["#2E86AB", "#F18F01", "#A23B72", "#1B7F3B"]


def _apply_style() -> None:
    sns.set_theme(style="whitegrid", font_scale=1.05)
    plt.rcParams.update(
        {
            "figure.dpi": 100,
            "savefig.dpi": 150,
            "axes.titlesize": 14,
            "axes.titleweight": "bold",
            "axes.labelsize": 12,
            "xtick.labelsize": 10,
            "ytick.labelsize": 10,
            "legend.fontsize": 10,
            "axes.edgecolor": "#555555",
            "axes.grid": True,
            "grid.alpha": 0.3,
            "figure.autolayout": False,
        }
    )


def _money_formatter(value: float, _position: int) -> str:
    """Format large rupee values compactly, e.g. 1500000 -> '₹1,500,000'."""
    return f"₹{value:,.0f}"


def _setup_axes(ax, title: str, x_label: str, y_label: str, money_axis: str = "y") -> None:
    ax.set_title(title, pad=14)
    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)
    axis = ax.yaxis if money_axis == "y" else ax.xaxis
    axis.set_major_formatter(FuncFormatter(_money_formatter))
    ax.grid(axis="y" if money_axis == "y" else "x", alpha=0.3)
    ax.grid(axis="x" if money_axis == "y" else "y", visible=False)
    for spine in ("top", "right"):
        ax.spines[spine].set_visible(False)


def _save(fig, output_path: Path) -> Path:
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return output_path


def plot_sales_by_category(category_perf: pd.DataFrame, output_path: Path) -> Path:
    """Vertical bar chart: total sales by category."""
    _apply_style()
    fig, ax = plt.subplots(figsize=(9, 5.5))
    sns.barplot(
        data=category_perf, x="Category", y="Sales",
        hue="Category", palette=CATEGORY_PALETTE[: len(category_perf)],
        legend=False, ax=ax,
    )
    bars = ax.containers[0]
    ax.bar_label(bars, labels=[f"₹{v:,.0f}" for v in bars.datavalues], padding=3, fontsize=9)
    ax.set_ylim(0, category_perf["Sales"].max() * 1.15)
    _setup_axes(ax, "Total Sales by Category", "Category", "Sales (₹)")
    return _save(fig, output_path)


def plot_profit_by_category(category_perf: pd.DataFrame, output_path: Path) -> Path:
    """Vertical bar chart: total profit by category (red if negative)."""
    _apply_style()
    fig, ax = plt.subplots(figsize=(9, 5.5))
    palette = {
        row.Category: COLORS["positive"] if row.Profit >= 0 else COLORS["negative"]
        for row in category_perf.itertuples()
    }
    sns.barplot(
        data=category_perf, x="Category", y="Profit",
        hue="Category", palette=palette, legend=False, ax=ax,
    )
    bars = ax.containers[0]
    ax.bar_label(bars, labels=[f"₹{v:,.0f}" for v in bars.datavalues], padding=3, fontsize=9)
    limit = category_perf["Profit"].abs().max() * 1.2
    ax.set_ylim(min(0, category_perf["Profit"].min() * 1.3), limit)
    _setup_axes(ax, "Total Profit by Category", "Category", "Profit (₹)")
    return _save(fig, output_path)


def plot_sales_by_region(region_perf: pd.DataFrame, output_path: Path) -> Path:
    """Vertical bar chart: total sales by region."""
    _apply_style()
    fig, ax = plt.subplots(figsize=(9, 5.5))
    sns.barplot(
        data=region_perf, x="Region", y="Sales",
        hue="Region", palette=REGION_PALETTE[: len(region_perf)],
        legend=False, ax=ax,
    )
    bars = ax.containers[0]
    ax.bar_label(bars, labels=[f"₹{v:,.0f}" for v in bars.datavalues], padding=3, fontsize=9)
    ax.set_ylim(0, region_perf["Sales"].max() * 1.15)
    _setup_axes(ax, "Total Sales by Region", "Region", "Sales (₹)")
    return _save(fig, output_path)


def plot_profit_by_region(region_perf: pd.DataFrame, output_path: Path) -> Path:
    """Vertical bar chart: total profit by region (red if negative)."""
    _apply_style()
    fig, ax = plt.subplots(figsize=(9, 5.5))
    ordered = region_perf.sort_values("Profit", ascending=False).reset_index(drop=True)
    palette = {
        row.Region: COLORS["positive"] if row.Profit >= 0 else COLORS["negative"]
        for row in ordered.itertuples()
    }
    sns.barplot(
        data=ordered, x="Region", y="Profit",
        hue="Region", palette=palette, legend=False, ax=ax,
    )
    bars = ax.containers[0]
    ax.bar_label(bars, labels=[f"₹{v:,.0f}" for v in bars.datavalues], padding=3, fontsize=9)
    limit = ordered["Profit"].abs().max() * 1.2
    ax.set_ylim(min(0, ordered["Profit"].min() * 1.3), limit)
    _setup_axes(ax, "Total Profit by Region", "Region", "Profit (₹)")
    return _save(fig, output_path)


def plot_top_products_by_sales(top_sales: pd.DataFrame, output_path: Path) -> Path:
    """Horizontal bar chart: top 10 products by sales."""
    _apply_style()
    fig, ax = plt.subplots(figsize=(9, 6))
    data = top_sales.sort_values("Sales", ascending=True)
    sns.barplot(
        data=data, y="Product", x="Sales",
        hue="Product", palette="viridis", legend=False, ax=ax,
    )
    bars = ax.containers[0]
    ax.bar_label(bars, labels=[f"₹{v:,.0f}" for v in bars.datavalues], padding=3, fontsize=9)
    ax.set_xlim(0, data["Sales"].max() * 1.2)
    _setup_axes(ax, "Top 10 Products by Sales", "Sales (₹)", "Product", money_axis="x")
    return _save(fig, output_path)


def plot_top_products_by_profit(top_profit: pd.DataFrame, output_path: Path) -> Path:
    """Horizontal bar chart: top 10 products by profit."""
    _apply_style()
    fig, ax = plt.subplots(figsize=(9, 6))
    data = top_profit.sort_values("Profit", ascending=True)
    palette = {
        row.Product: COLORS["positive"] if row.Profit >= 0 else COLORS["negative"]
        for row in data.itertuples()
    }
    sns.barplot(
        data=data, y="Product", x="Profit",
        hue="Product", palette=palette, legend=False, ax=ax,
    )
    bars = ax.containers[0]
    ax.bar_label(bars, labels=[f"₹{v:,.0f}" for v in bars.datavalues], padding=3, fontsize=9)
    span = data["Profit"].max() - min(0, data["Profit"].min())
    ax.set_xlim(min(0, data["Profit"].min() * 1.3), data["Profit"].max() + span * 0.15)
    _setup_axes(ax, "Top 10 Products by Profit", "Profit (₹)", "Product", money_axis="x")
    return _save(fig, output_path)


def plot_monthly_sales_trend(monthly: pd.DataFrame, output_path: Path) -> Path:
    """Line chart: monthly sales trend with the peak month highlighted."""
    _apply_style()
    fig, ax = plt.subplots(figsize=(10, 5.5))
    sns.lineplot(
        data=monthly, x="Month_Start", y="Sales",
        marker="o", color=COLORS["primary"], linewidth=2.5, markersize=7, ax=ax,
    )
    peak = monthly.loc[monthly["Sales"].idxmax()]
    ax.annotate(
        f"Peak: ₹{peak['Sales']:,.0f} ({peak['Month_Label']})",
        xy=(peak["Month_Start"], peak["Sales"]),
        xytext=(0, 16), textcoords="offset points",
        ha="center", fontsize=10, fontweight="bold", color=COLORS["secondary"],
    )
    ax.set_ylim(0, monthly["Sales"].max() * 1.18)
    _setup_axes(ax, "Monthly Sales Trend", "Month", "Sales (₹)")
    ax.tick_params(axis="x", rotation=45)
    ax.xaxis.set_major_formatter(DateFormatter("%b %Y"))
    return _save(fig, output_path)


def plot_monthly_profit_trend(monthly: pd.DataFrame, output_path: Path) -> Path:
    """Line chart: monthly profit trend with the peak month highlighted."""
    _apply_style()
    fig, ax = plt.subplots(figsize=(10, 5.5))
    sns.lineplot(
        data=monthly, x="Month_Start", y="Profit",
        marker="o", color=COLORS["positive"], linewidth=2.5, markersize=7, ax=ax,
    )
    peak = monthly.loc[monthly["Profit"].idxmax()]
    ax.annotate(
        f"Peak: ₹{peak['Profit']:,.0f} ({peak['Month_Label']})",
        xy=(peak["Month_Start"], peak["Profit"]),
        xytext=(0, 16), textcoords="offset points",
        ha="center", fontsize=10, fontweight="bold", color=COLORS["secondary"],
    )
    low = monthly["Profit"].min()
    ax.set_ylim(min(0, low * 1.3), monthly["Profit"].max() * 1.18)
    ax.axhline(0, color="#555555", linewidth=1, linestyle="--")
    _setup_axes(ax, "Monthly Profit Trend", "Month", "Profit (₹)")
    ax.tick_params(axis="x", rotation=45)
    ax.xaxis.set_major_formatter(DateFormatter("%b %Y"))
    return _save(fig, output_path)


def create_all_charts(
    category_perf: pd.DataFrame,
    region_perf: pd.DataFrame,
    top_sales: pd.DataFrame,
    top_profit: pd.DataFrame,
    monthly: pd.DataFrame,
    output_dir: Path = DEFAULT_CHART_DIR,
) -> list[Path]:
    """Generate every required chart and return the list of saved file paths."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    saved = [
        plot_sales_by_category(category_perf, output_dir / "01_sales_by_category.png"),
        plot_profit_by_category(category_perf, output_dir / "02_profit_by_category.png"),
        plot_sales_by_region(region_perf, output_dir / "03_sales_by_region.png"),
        plot_profit_by_region(region_perf, output_dir / "04_profit_by_region.png"),
        plot_top_products_by_sales(top_sales, output_dir / "05_top10_products_by_sales.png"),
        plot_top_products_by_profit(top_profit, output_dir / "06_top10_products_by_profit.png"),
        plot_monthly_sales_trend(monthly, output_dir / "07_monthly_sales_trend.png"),
        plot_monthly_profit_trend(monthly, output_dir / "08_monthly_profit_trend.png"),
    ]
    return saved
