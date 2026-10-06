"""All calculations for the Sales Data Analysis project.

Every number, ranking and sentence produced here is computed dynamically from
the cleaned dataset - nothing is hard-coded.
"""

import pandas as pd


# ---------------------------------------------------------------------------
# Small formatting helpers (used by reports and the notebook)
# ---------------------------------------------------------------------------
def format_inr(value: float) -> str:
    """Format a number as Indian Rupees, e.g. 1234567.8 -> '₹1,234,568'."""
    return f"₹{value:,.0f}"


def format_pct(value: float) -> str:
    """Format a fraction as a percentage, e.g. 0.1234 -> '12.3%'."""
    return f"{value:.1f}%"


def to_markdown_table(df: pd.DataFrame) -> str:
    """Render a DataFrame as a GitHub-flavoured Markdown table."""
    columns = [str(c) for c in df.columns]
    header = "| " + " | ".join(columns) + " |"
    separator = "| " + " | ".join("---" for _ in columns) + " |"
    rows = [
        "| " + " | ".join(str(value) for value in row) + " |"
        for row in df.itertuples(index=False, name=None)
    ]
    return "\n".join([header, separator, *rows])


# ---------------------------------------------------------------------------
# KPI calculation
# ---------------------------------------------------------------------------
def compute_kpis(df: pd.DataFrame) -> dict:
    """Compute the headline KPIs of the cleaned sales dataset."""
    total_sales = float(df["Sales"].sum())
    total_profit = float(df["Profit"].sum())
    total_orders = int(df["Order_ID"].nunique())
    total_quantity = int(df["Quantity"].sum())
    average_order_value = total_sales / total_orders if total_orders else 0.0
    profit_margin_pct = (total_profit / total_sales * 100) if total_sales else 0.0

    return {
        "Total Sales": total_sales,
        "Total Profit": total_profit,
        "Total Orders": total_orders,
        "Total Quantity Sold": total_quantity,
        "Average Order Value": average_order_value,
        "Profit Margin (%)": round(profit_margin_pct, 2),
        "Unique Products": int(df["Product"].nunique()),
        "Unique Customers": int(df["Customer_Name"].nunique()),
        "Loss-Making Orders": int((df["Profit"] < 0).sum()),
        "First Order Date": df["Order_Date"].min(),
        "Last Order Date": df["Order_Date"].max(),
    }


def kpi_summary_frame(kpis: dict) -> pd.DataFrame:
    """Turn the KPI dictionary into a tidy two-column summary table."""
    rows = []
    for name, value in kpis.items():
        if isinstance(value, pd.Timestamp):
            rendered = value.strftime("%Y-%m-%d")
        elif isinstance(value, float):
            rendered = f"{value:,.2f}"
        else:
            rendered = f"{value:,}"
        rows.append({"Metric": name, "Value": rendered})
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# Aggregations
# ---------------------------------------------------------------------------
def sales_profit_by(df: pd.DataFrame, group_col: str) -> pd.DataFrame:
    """Aggregate sales, profit and orders by any column (category, region...)."""
    grouped = (
        df.groupby(group_col)
        .agg(
            Sales=("Sales", "sum"),
            Profit=("Profit", "sum"),
            Orders=("Order_ID", "nunique"),
            Quantity=("Quantity", "sum"),
        )
        .reset_index()
    )
    total_sales = grouped["Sales"].sum()
    total_profit = grouped["Profit"].sum()
    grouped["Sales Share (%)"] = (grouped["Sales"] / total_sales * 100).round(2)
    grouped["Profit Share (%)"] = (grouped["Profit"] / total_profit * 100).round(2)
    grouped["Profit Margin (%)"] = (grouped["Profit"] / grouped["Sales"] * 100).round(2)
    return grouped.sort_values("Sales", ascending=False).reset_index(drop=True)


def top_products(df: pd.DataFrame, metric: str = "Sales", n: int = 10) -> pd.DataFrame:
    """Return the top-n products ranked by 'Sales' or 'Profit'."""
    if metric not in {"Sales", "Profit"}:
        raise ValueError("metric must be 'Sales' or 'Profit'")
    grouped = (
        df.groupby("Product")
        .agg(
            Sales=("Sales", "sum"),
            Profit=("Profit", "sum"),
            Quantity=("Quantity", "sum"),
            Orders=("Order_ID", "nunique"),
        )
        .reset_index()
        .sort_values(metric, ascending=False)
        .reset_index(drop=True)
    )
    grouped.insert(0, "Rank", range(1, len(grouped) + 1))
    return grouped.head(n)


def worst_products(df: pd.DataFrame, n: int = 5) -> pd.DataFrame:
    """Return the n least profitable products (negative profits appear first)."""
    grouped = (
        df.groupby("Product")
        .agg(
            Sales=("Sales", "sum"),
            Profit=("Profit", "sum"),
            Quantity=("Quantity", "sum"),
            Orders=("Order_ID", "nunique"),
        )
        .reset_index()
        .sort_values("Profit")
        .reset_index(drop=True)
    )
    grouped.insert(0, "Rank", range(1, len(grouped) + 1))
    return grouped.head(n)


def monthly_trends(df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate sales, profit and order count by month."""
    temp = df.copy()
    temp["Month"] = temp["Order_Date"].dt.to_period("M")
    trends = (
        temp.groupby("Month")
        .agg(
            Sales=("Sales", "sum"),
            Profit=("Profit", "sum"),
            Orders=("Order_ID", "nunique"),
            Quantity=("Quantity", "sum"),
        )
        .reset_index()
    )
    trends["Month_Label"] = trends["Month"].dt.strftime("%b %Y")
    trends["Month_Start"] = trends["Month"].dt.to_timestamp()
    trends["Profit Margin (%)"] = (trends["Profit"] / trends["Sales"] * 100).round(2)
    return trends.sort_values("Month_Start").reset_index(drop=True)


# ---------------------------------------------------------------------------
# Dynamic insight generation
# ---------------------------------------------------------------------------
def generate_key_findings(
    df: pd.DataFrame,
    kpis: dict,
    category_perf: pd.DataFrame,
    region_perf: pd.DataFrame,
    product_sales_top: pd.DataFrame,
    product_profit_top: pd.DataFrame,
    monthly: pd.DataFrame,
) -> list[str]:
    """Build the KEY FINDINGS list straight from the computed numbers."""
    best_sales_cat = category_perf.loc[category_perf["Sales"].idxmax()]
    best_profit_cat = category_perf.loc[category_perf["Profit"].idxmax()]
    worst_profit_cat = category_perf.loc[category_perf["Profit"].idxmin()]

    best_sales_reg = region_perf.loc[region_perf["Sales"].idxmax()]
    best_profit_reg = region_perf.loc[region_perf["Profit"].idxmax()]
    worst_profit_reg = region_perf.loc[region_perf["Profit"].idxmin()]

    best_product = product_sales_top.iloc[0]
    most_profitable_product = product_profit_top.iloc[0]

    peak_month = monthly.loc[monthly["Sales"].idxmax()]
    low_month = monthly.loc[monthly["Sales"].idxmin()]

    loss_orders = kpis["Loss-Making Orders"]
    loss_share = loss_orders / kpis["Total Orders"] * 100 if kpis["Total Orders"] else 0
    worst_loss_product = worst_products(df, n=1).iloc[0]

    if best_sales_reg["Region"] == best_profit_reg["Region"]:
        region_line = (
            f"Region '{best_sales_reg['Region']}' led both sales "
            f"({format_inr(best_sales_reg['Sales'])}) and profit "
            f"({format_inr(best_profit_reg['Profit'])})."
        )
    else:
        region_line = (
            f"Region '{best_sales_reg['Region']}' led sales "
            f"({format_inr(best_sales_reg['Sales'])}), while region "
            f"'{best_profit_reg['Region']}' led profit ({format_inr(best_profit_reg['Profit'])})."
        )

    findings = [
        f"Total revenue was {format_inr(kpis['Total Sales'])} across "
        f"{kpis['Total Orders']:,} orders and {kpis['Total Quantity Sold']:,} units.",
        f"Total profit was {format_inr(kpis['Total Profit'])} "
        f"(overall margin {format_pct(kpis['Profit Margin (%)'])}).",
        f"Average order value was {format_inr(kpis['Average Order Value'])}.",
        f"Category '{best_sales_cat['Category']}' generated the highest sales "
        f"({format_inr(best_sales_cat['Sales'])}, {format_pct(best_sales_cat['Sales Share (%)'])} of total).",
        f"Category '{best_profit_cat['Category']}' earned the highest profit "
        f"({format_inr(best_profit_cat['Profit'])}).",
        region_line,
        f"'{best_product['Product']}' was the best-selling product "
        f"({format_inr(best_product['Sales'])} revenue, {int(best_product['Quantity']):,} units).",
        f"'{most_profitable_product['Product']}' was the most profitable product "
        f"({format_inr(most_profitable_product['Profit'])} profit).",
        f"{peak_month['Month_Label']} recorded the highest monthly sales "
        f"({format_inr(peak_month['Sales'])}); {low_month['Month_Label']} was the lowest "
        f"({format_inr(low_month['Sales'])}).",
        f"{loss_orders:,} orders ({format_pct(loss_share)}) were loss-making; "
        f"'{worst_loss_product['Product']}' earned the lowest profit of all products "
        f"({format_inr(worst_loss_product['Profit'])}).",
        f"Lowest-profit category: '{worst_profit_cat['Category']}' "
        f"({format_inr(worst_profit_cat['Profit'])}); lowest-profit region: "
        f"'{worst_profit_reg['Region']}' ({format_inr(worst_profit_reg['Profit'])}).",
    ]
    return findings


def generate_recommendations(
    df: pd.DataFrame,
    kpis: dict,
    category_perf: pd.DataFrame,
    region_perf: pd.DataFrame,
    product_sales_top: pd.DataFrame,
    monthly: pd.DataFrame,
) -> list[str]:
    """Build BUSINESS RECOMMENDATIONS from the actual weak/strong segments."""
    best_sales_cat = category_perf.loc[category_perf["Sales"].idxmax()]
    best_profit_cat = category_perf.loc[category_perf["Profit"].idxmax()]
    worst_profit_reg = region_perf.loc[region_perf["Profit"].idxmin()]
    weakest_margin_cat = category_perf.loc[category_perf["Profit Margin (%)"].idxmin()]
    top_products_by_qty = (
        df.groupby("Product")["Quantity"].sum().sort_values(ascending=False).head(5)
    )
    peak_month = monthly.loc[monthly["Sales"].idxmax()]
    low_month = monthly.loc[monthly["Sales"].idxmin()]
    worst_products_df = worst_products(df, n=3)

    if best_sales_cat["Category"] == best_profit_cat["Category"]:
        focus_line = (
            f"Double down on '{best_sales_cat['Category']}' - it leads both sales "
            f"({format_pct(best_sales_cat['Sales Share (%)'])} of revenue) and profit "
            f"({format_inr(best_profit_cat['Profit'])}); it is the strongest growth engine today."
        )
    else:
        focus_line = (
            f"Focus marketing spend on high-performing segments: '{best_sales_cat['Category']}' "
            f"contributes {format_pct(best_sales_cat['Sales Share (%)'])} of revenue and "
            f"'{best_profit_cat['Category']}' delivers the highest profit "
            f"({format_inr(best_profit_cat['Profit'])})."
        )

    if worst_products_df.iloc[0]["Profit"] < 0:
        worst_line = (
            "Fix loss-making products first: "
            + ", ".join(
                f"{row['Product']} ({format_inr(row['Profit'])})"
                for _, row in worst_products_df.iterrows()
            )
            + " - renegotiate costs, bundle them with profitable items or retire them."
        )
    else:
        worst_line = (
            "Lowest-profit products need a cost and pricing review first: "
            + ", ".join(
                f"{row['Product']} ({format_inr(row['Profit'])})"
                for _, row in worst_products_df.iterrows()
            )
            + " - renegotiate costs or bundle them with higher-margin items."
        )

    recommendations = [
        focus_line,
        f"Review pricing and discounts on low-margin category '{weakest_margin_cat['Category']}' "
        f"(margin {format_pct(weakest_margin_cat['Profit Margin (%)'])}) - heavy discounting is "
        "eroding profitability on otherwise popular items.",
        f"Strengthen the weakest region '{worst_profit_reg['Region']}' "
        f"(profit {format_inr(worst_profit_reg['Profit'])}) with local promotions, "
        "better distribution and a review of the regional cost-to-serve.",
        "Maintain inventory for high-demand products: "
        + ", ".join(
            f"{prod} ({int(qty):,} units)" for prod, qty in top_products_by_qty.items()
        )
        + ".",
        f"Plan promotions around the trend: sales peak in {peak_month['Month_Label']} "
        f"({format_inr(peak_month['Sales'])}) and dip in {low_month['Month_Label']} "
        f"({format_inr(low_month['Sales'])}) - run campaigns before the peak and "
        "targeted offers to lift the slow months.",
        worst_line,
        f"Protect the healthy overall margin of {format_pct(kpis['Profit Margin (%)'])} "
        "by setting a maximum discount threshold per category and tracking "
        "profit-per-order in weekly reporting.",
    ]
    return recommendations
