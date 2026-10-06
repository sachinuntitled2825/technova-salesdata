# Sales Data Analysis

**Data Analytics Internship - Task 1**

An end-to-end analysis of a retail sales dataset covering revenue performance,
profitability, products, categories, regions and monthly trends - built with
Python (Pandas, NumPy, Matplotlib, Seaborn) and a runnable Jupyter Notebook.

---

## Project Overview

This project answers a simple business question: *where is the business making
money, where is it losing money, and what should be done about it?*

The workflow covers the full analytical cycle:

1. Load and inspect the dataset
2. Profile and clean the data (missing values, duplicates, invalid records, data types)
3. Run exploratory data analysis (EDA)
4. Calculate business KPIs
5. Analyse sales and profit by category, region, product and month
6. Build professional visualisations
7. Generate key findings and actionable business recommendations

All numbers, rankings and insights in this project are **calculated dynamically
from the dataset** - none are hard-coded.

---

## Objective

- Measure overall **sales performance** (total revenue, orders, units, average order value)
- Measure overall **profit performance** (total profit, margin, loss-making orders)
- Identify the **best-performing products, categories and regions**
- Identify **poor-performing** products, categories and regions
- Track **sales and profit trends** across the year
- Translate the analysis into **business insights and recommendations**

---

## Dataset Description

> **Note:** No official dataset was supplied with the task, so a **realistic
> sample dataset** was generated for this internship analysis
> (`data/sales_data.csv`, created by `src/generate_dataset.py`, fixed random
> seed so it is fully reproducible). It intentionally contains realistic quality
> issues (missing values, duplicates, invalid records) so the data-cleaning step
> does genuine work.

| Column | Description | Example |
| --- | --- | --- |
| `Order_ID` | Unique order identifier | `ORD-10042` |
| `Order_Date` | Date of the order (ISO format) | `2025-06-18` |
| `Customer_Name` | Customer who placed the order | `Priya Nair` |
| `Product` | Product sold | `Wireless Headphones` |
| `Category` | Product category | `Electronics` |
| `Region` | Sales region | `North` |
| `Quantity` | Units purchased | `3` |
| `Sales` | Order revenue in ₹ | `4,950.00` |
| `Discount` | Discount applied (0-1) | `0.10` |
| `Profit` | Order profit in ₹ (can be negative) | `412.75` |

- **Rows (raw):** 652
- **Period:** 1 January 2025 - 31 December 2025
- **Categories:** Electronics, Furniture, Clothing, Grocery, Sports (25 products)
- **Regions:** North, South, East, West
- **Currency:** Indian Rupees (₹)

---

## Tools & Technologies

| Tool | Purpose |
| --- | --- |
| Python 3.12 | Core programming language |
| Pandas | Data loading, cleaning, aggregation |
| NumPy | Numerical operations |
| Matplotlib | Chart rendering and formatting |
| Seaborn | Statistical chart styling |
| Jupyter Notebook | Interactive, step-by-step analysis |

---

## Data Cleaning

Cleaning is implemented in `src/data_cleaning.py` and runs automatically in both
the pipeline and the notebook.

| # | Step | Why |
| --- | --- | --- |
| 1 | Validate required columns | Fail fast if the schema changes |
| 2 | Trim stray whitespace in text fields | `North ` must match `North` |
| 3 | Convert `Order_Date` to datetime, drop unparseable dates | Dates arrive as text |
| 4 | Coerce numeric columns, drop rows missing essential values | Sales/profit cannot be imputed responsibly |
| 5 | Fill non-essential missing values (`Customer_Name` -> "Unknown Customer", `Discount` -> median) | Keep otherwise valid orders |
| 6 | Remove exact duplicate records | Duplicates inflate revenue |
| 7 | Remove invalid records (Quantity <= 0, Sales <= 0, Discount outside 0-1) | Physically impossible values |
| 8 | **Keep** negative profits | A loss is valid business data, not an error |

**Before / after cleaning:**

| Metric | Before | After |
| --- | --- | --- |
| Rows | 652 | 616 |
| Missing cells | 36 | 0 |
| Duplicate rows | 12 | 0 |
| `Order_Date` type | text | datetime |
| `Quantity` type | float (nullable) | int64 |

36 rows were removed in total (5 bad dates, 15 missing essential values, 12
duplicates, 4 invalid records) and 105 orders with negative profit were kept as
genuine losses. Full detail: `outputs/reports/data_cleaning_report.txt`.

---

## Analysis Performed

1. Total Sales
2. Total Profit
3. Total Orders
4. Total Quantity Sold
5. Average Order Value
6. Sales by Category
7. Profit by Category
8. Sales by Region
9. Profit by Region
10. Top 10 Products by Sales
11. Top 10 Products by Profit
12. Monthly Sales Trend
13. Monthly Profit Trend
14. Highest-performing category
15. Highest-performing region
16. Most profitable products
17. Poor-performing products / categories / regions (bottom rankings + margin analysis)

---

## Visualizations

Eight charts are generated in `outputs/charts/` (7 required charts + profit by
region). Every chart has a title, axis labels, ₹-formatted values, readable font
sizes and no unnecessary clutter.

| File | Chart |
| --- | --- |
| `01_sales_by_category.png` | Sales by Category - bar chart |
| `02_profit_by_category.png` | Profit by Category - bar chart |
| `03_sales_by_region.png` | Sales by Region - bar chart |
| `04_profit_by_region.png` | Profit by Region - bar chart |
| `05_top10_products_by_sales.png` | Top 10 Products by Sales - horizontal bar chart |
| `06_top10_products_by_profit.png` | Top 10 Products by Profit - horizontal bar chart |
| `07_monthly_sales_trend.png` | Monthly Sales Trend - line chart |
| `08_monthly_profit_trend.png` | Monthly Profit Trend - line chart |

---

## Key Findings

Calculated from the cleaned dataset (616 orders, Jan-Dec 2025):

- **Total revenue:** ₹6,013,456 across 616 orders and 1,437 units
- **Total profit:** ₹883,307 (overall margin 14.7%)
- **Average order value:** ₹9,762
- **Category `Electronics`** generated the highest sales - ₹3,186,566 (53.0% of total revenue) - and also the highest profit (₹416,357)
- **`Clothing`** is the most efficient category by margin (26.4%), while **`Grocery`** earns almost nothing (₹4,205 profit, 3.7% margin) despite the highest order volume
- **Region `North`** led both sales (₹1,884,068) and profit (₹265,850); **`East`** is the weakest region (₹149,893 profit)
- **Best-selling product:** `Laptop` - ₹1,039,593 revenue
- **Most profitable product:** `Tablet` - ₹135,582 profit
- **Lowest-profit product:** `Tea Pack` - ₹272 profit
- **Peak month:** October 2025 (₹921,412); **lowest month:** June 2025 (₹203,530), showing a clear festive-season surge
- **105 orders (17.0%) were loss-making**, driven by deep discounts on low-margin categories

---

## Business Recommendations

- **Double down on `Electronics`** - it leads both sales (53.0% of revenue) and profit (₹416,357); it is the strongest growth engine today
- **Review pricing and discounts on `Grocery`** (3.7% margin) - heavy discounting is eroding profitability on otherwise popular items
- **Strengthen the weakest region `East`** (₹149,893 profit) with local promotions, better distribution and a review of regional cost-to-serve
- **Maintain inventory for high-demand products:** Rice Bag 5kg (125 units), Cotton Shirt (109), Detergent Powder (99), Cooking Oil 1L (99), Sports Shoes (93)
- **Plan promotions around the trend:** sales peak in Oct 2025 and dip in Jun 2025 - run campaigns before the peak and targeted offers to lift slow months
- **Fix the lowest-profit products first** (`Tea Pack`, `Rice Bag 5kg`, `Cooking Oil 1L`) - renegotiate costs or bundle them with higher-margin items
- **Protect the 14.7% margin** with a maximum discount threshold per category and weekly profit-per-order reporting

These sentences are generated by `src/analysis.py` directly from the computed
tables - they update automatically if the dataset changes.

---

## Project Structure

```
sales-data-analysis/
│
├── data/
│   └── sales_data.csv              # Sample sales dataset (652 raw rows)
│
├── notebooks/
│   └── sales_analysis.ipynb        # Full 18-section analysis notebook (executed)
│
├── src/
│   ├── __init__.py                 # Package marker
│   ├── generate_dataset.py         # Reproducible sample-dataset generator
│   ├── data_cleaning.py            # Loading + cleaning + quality reports
│   ├── analysis.py                 # KPIs, aggregations, insight generation
│   ├── visualization.py            # Matplotlib/Seaborn chart functions
│   └── main.py                     # End-to-end pipeline
│
├── outputs/
│   ├── charts/                     # 8 generated PNG charts
│   ├── reports/
│   │   ├── data_cleaning_report.txt
│   │   ├── analysis_report.md      # Tables + findings + recommendations
│   │   ├── sales_by_category.csv
│   │   ├── sales_by_region.csv
│   │   ├── top10_products_by_sales.csv
│   │   ├── top10_products_by_profit.csv
│   │   └── monthly_trends.csv
│   ├── sales_data_cleaned.csv      # Cleaned dataset
│   └── summary.csv                 # KPI summary
│
├── README.md
├── requirements.txt
└── .gitignore
```

---

## How to Run

**1. Clone the repository**

```bash
git clone <repository-url>
cd sales-data-analysis
```

**2. Install dependencies**

```bash
pip install -r requirements.txt
```

**3. Run the full pipeline** (cleaning -> analysis -> charts -> reports)

```bash
python src/main.py
```

**4. Launch the Jupyter Notebook**

```bash
jupyter notebook notebooks/sales_analysis.ipynb
```

Or run it headless from the terminal:

```bash
jupyter nbconvert --to notebook --execute notebooks/sales_analysis.ipynb --inplace
```

**Optional - regenerate the sample dataset** (identical output, fixed seed):

```bash
python src/generate_dataset.py
```

---

## Results

| Output | Description |
| --- | --- |
| `outputs/summary.csv` | KPI summary (sales, profit, orders, quantity, AOV, margin) |
| `outputs/sales_data_cleaned.csv` | Cleaned dataset used for all analysis |
| `outputs/charts/*.png` | 8 publication-quality charts |
| `outputs/reports/analysis_report.md` | Full report: tables, key findings, recommendations |
| `outputs/reports/data_cleaning_report.txt` | Before/after cleaning audit trail |
| `outputs/reports/*.csv` | Category, region, product and monthly aggregate tables |
| `notebooks/sales_analysis.ipynb` | Executed notebook with every result and chart inline |

**KPI Summary**

| Metric | Value |
| --- | --- |
| Total Sales | ₹6,013,456 |
| Total Profit | ₹883,307 |
| Total Orders | 616 |
| Total Quantity Sold | 1,437 |
| Average Order Value | ₹9,762 |
| Profit Margin | 14.7% |

---

## Conclusion

The analysis shows a healthy overall business (₹6.01M revenue, ₹0.88M profit,
14.7% margin) with a very uneven profit distribution: **Electronics and the
North region carry the business**, `Clothing` delivers the best margins, while
`Grocery` and deep-discounted orders destroy most of their own value and 17% of
orders end up loss-making. Sales follow a strong festive curve that peaks in
October-November.

The practical priorities are: control discounting on low-margin categories,
lift the underperforming East region, protect stock cover on the top-5
best-selling products, and time promotions to the observed seasonal trend.

The entire project - from raw data to recommendations - reruns reproducibly
with a single command and is ready to be pushed to GitHub as an internship
submission.
