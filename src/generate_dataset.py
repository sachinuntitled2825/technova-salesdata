"""Generate the sample sales dataset used by this internship project.

IMPORTANT: This project did not come with an official dataset, so a realistic
SAMPLE dataset is generated here. It is fully reproducible (fixed random seed)
and contains a few realistic quality issues (missing values, duplicate rows,
invalid records) so that the data-cleaning step has genuine work to do.

Run from the project root:
    python src/generate_dataset.py
"""

from pathlib import Path

import numpy as np
import pandas as pd

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
RANDOM_SEED = 42
N_BASE_ORDERS = 640  # cleaned data will still be well above the 500-row minimum
START_DATE = pd.Timestamp("2025-01-01")
END_DATE = pd.Timestamp("2025-12-31")

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DATA_PATH = PROJECT_ROOT / "data" / "sales_data.csv"

# Realistic gross-margin rate per category (before discount effect)
CATEGORY_MARGIN = {
    "Electronics": 0.20,
    "Furniture": 0.18,
    "Clothing": 0.32,
    "Grocery": 0.12,
    "Sports": 0.26,
}

# product name, category, unit price range, popularity weight
PRODUCT_CATALOG = [
    ("Laptop", "Electronics", (45000, 75000), 3),
    ("Smartphone", "Electronics", (12000, 30000), 6),
    ("Wireless Headphones", "Electronics", (1500, 5000), 8),
    ("Tablet", "Electronics", (15000, 28000), 4),
    ("Laser Printer", "Electronics", (8000, 15000), 2),
    ("Office Chair", "Furniture", (4000, 9000), 5),
    ("Study Desk", "Furniture", (5000, 12000), 4),
    ("Bookshelf", "Furniture", (3000, 7000), 3),
    ("Sofa Set", "Furniture", (18000, 40000), 2),
    ("Steel Almirah", "Furniture", (9000, 18000), 2),
    ("Cotton Shirt", "Clothing", (800, 2000), 9),
    ("Denim Jeans", "Clothing", (1200, 2500), 7),
    ("Winter Jacket", "Clothing", (1500, 3500), 5),
    ("Sports Shoes", "Clothing", (2000, 5000), 6),
    ("Silk Saree", "Clothing", (2500, 8000), 4),
    ("Rice Bag 5kg", "Grocery", (300, 500), 8),
    ("Cooking Oil 1L", "Grocery", (120, 200), 8),
    ("Tea Pack", "Grocery", (150, 350), 7),
    ("Sugar Bag 5kg", "Grocery", (200, 300), 6),
    ("Detergent Powder", "Grocery", (150, 400), 6),
    ("Cricket Bat", "Sports", (1500, 5000), 5),
    ("Football", "Sports", (500, 1500), 5),
    ("Yoga Mat", "Sports", (400, 1200), 6),
    ("Dumbbell Set", "Sports", (1500, 4000), 3),
    ("Badminton Racket", "Sports", (800, 2500), 4),
]

REGIONS = ["North", "South", "East", "West"]
REGION_WEIGHTS = [0.26, 0.27, 0.20, 0.27]  # West/South are stronger markets

CUSTOMER_NAMES = [
    "Aarav Sharma", "Priya Nair", "Rohan Verma", "Ananya Iyer", "Vikram Singh",
    "Meera Kapoor", "Aditya Rao", "Sneha Patil", "Karthik Reddy", "Neha Gupta",
    "Rahul Malhotra", "Divya Krishnan", "Amit Joshi", "Pooja Deshmukh",
    "Suresh Pillai", "Ritika Banerjee", "Manish Chawla", "Swati Kulkarni",
    "Arjun Menon", "Kavita Saxena", "Nikhil Bhatt", "Shreya Dutta",
    "Harish Prasad", "Anjali Mishra", "Ravi Teja", "Tanvi Shah",
    "Sameer Khan", "Lakshmi Narayan", "Yash Agarwal", "Ishita Bose",
    "Deepak Rane", "Priyanka Sethi", "Varun Chopra", "Rupal Gandhi",
    "Abhishek Tiwari", "Sonal Pande", "Gaurav Ahuja", "Preeti Vyas",
    "Manoj Dixit", "Charu Sinha",
]

# Indian festive season (Diwali in Oct/Nov) lifts sales strongly
MONTH_WEIGHTS = [0.70, 0.68, 0.78, 0.82, 0.88, 0.84, 0.90, 0.96, 1.05, 1.45, 1.50, 1.15]


def _random_dates(rng: np.random.Generator, n: int) -> pd.Series:
    """Draw order dates across 2025 with festive-season weighting."""
    months = np.arange(1, 13)
    weights = np.array(MONTH_WEIGHTS, dtype=float)
    weights = weights / weights.sum()
    chosen_months = rng.choice(months, size=n, p=weights)

    dates = []
    for month in chosen_months:
        month_start = pd.Timestamp(year=START_DATE.year, month=int(month), day=1)
        month_end = month_start + pd.offsets.MonthEnd(0)
        day = int(rng.integers(1, month_end.day + 1))
        dates.append(month_start + pd.Timedelta(days=day - 1))
    return pd.Series(pd.to_datetime(dates))


def build_dataset() -> pd.DataFrame:
    """Build the raw (slightly messy) sample sales dataset."""
    rng = np.random.default_rng(RANDOM_SEED)

    product_names = [p[0] for p in PRODUCT_CATALOG]
    product_weights = np.array([p[3] for p in PRODUCT_CATALOG], dtype=float)
    product_weights = product_weights / product_weights.sum()
    catalog = {p[0]: p for p in PRODUCT_CATALOG}

    chosen_products = rng.choice(product_names, size=N_BASE_ORDERS, p=product_weights)
    chosen_customers = rng.choice(CUSTOMER_NAMES, size=N_BASE_ORDERS)
    chosen_regions = rng.choice(REGIONS, size=N_BASE_ORDERS, p=REGION_WEIGHTS)
    order_dates = _random_dates(rng, N_BASE_ORDERS)

    # Discount profile: a mix of full-price, small, moderate and heavy cuts
    discount_profile = rng.choice(
        ["none", "low", "medium", "high"], size=N_BASE_ORDERS, p=[0.40, 0.27, 0.22, 0.11]
    )
    discounts = np.where(
        discount_profile == "none",
        0.0,
        np.where(
            discount_profile == "low",
            rng.uniform(0.05, 0.10, N_BASE_ORDERS),
            np.where(
                discount_profile == "medium",
                rng.uniform(0.12, 0.25, N_BASE_ORDERS),
                rng.uniform(0.28, 0.45, N_BASE_ORDERS),
            ),
        ),
    )

    records = []
    for i in range(N_BASE_ORDERS):
        _, category, price_range, _ = catalog[chosen_products[i]]
        unit_price = round(float(rng.uniform(*price_range)), 2)

        if category in ("Electronics", "Furniture"):
            quantity = int(rng.choice([1, 2, 3, 4], p=[0.55, 0.25, 0.13, 0.07]))
        else:
            quantity = int(rng.choice([1, 2, 3, 4, 5, 6], p=[0.30, 0.25, 0.18, 0.12, 0.09, 0.06]))

        discount = round(float(discounts[i]), 2)
        sales = round(quantity * unit_price * (1 - discount) * rng.uniform(0.98, 1.02), 2)

        # Profit falls as discount grows; heavy discounts can create real losses
        profit_rate = (
            CATEGORY_MARGIN[category]
            - 0.90 * discount
            + float(rng.normal(0.0, 0.035))
        )
        profit_rate = float(np.clip(profit_rate, -0.35, 0.45))
        profit = round(sales * profit_rate, 2)

        records.append(
            {
                "Order_ID": f"ORD-{10001 + i}",
                "Order_Date": order_dates[i].strftime("%Y-%m-%d"),
                "Customer_Name": chosen_customers[i],
                "Product": chosen_products[i],
                "Category": category,
                "Region": chosen_regions[i],
                "Quantity": quantity,
                "Sales": sales,
                "Discount": discount,
                "Profit": profit,
            }
        )

    df = pd.DataFrame.from_records(records)

    # ------------------------------------------------------------------
    # Inject realistic quality issues (cleaned later by data_cleaning.py)
    # ------------------------------------------------------------------
    n = len(df)

    def _sample_rows(count: int) -> np.ndarray:
        return rng.choice(n, size=count, replace=False)

    # 1. Missing values
    df.loc[_sample_rows(10), "Customer_Name"] = None
    df.loc[_sample_rows(8), "Discount"] = None
    df.loc[_sample_rows(4), "Region"] = None
    df.loc[_sample_rows(3), "Sales"] = None
    df.loc[_sample_rows(3), "Profit"] = None
    df.loc[_sample_rows(3), "Quantity"] = None
    df.loc[_sample_rows(3), "Order_Date"] = None
    df.loc[_sample_rows(2), "Product"] = None

    # 2. Unparseable dates (day/month swapped beyond valid calendar range)
    bad_date_rows = _sample_rows(2)
    df.loc[bad_date_rows, "Order_Date"] = "2025-13-45"

    # 2b. Stray whitespace in text fields (cleaned by data_cleaning.py)
    name_rows = rng.choice(df.index[df["Customer_Name"].notna()].to_numpy(), size=6, replace=False)
    df.loc[name_rows, "Customer_Name"] = "  " + df.loc[name_rows, "Customer_Name"] + "  "
    region_rows = rng.choice(df.index[df["Region"].notna()].to_numpy(), size=4, replace=False)
    df.loc[region_rows, "Region"] = df.loc[region_rows, "Region"] + "   "

    # 3. Invalid records (zero/negative quantity, zero/negative sales)
    #    Pick rows that still have valid numeric values so the issue is visible.
    eligible = df.index[(df["Sales"].notna()) & (df["Quantity"].notna())].to_numpy()
    invalid_rows = rng.choice(eligible, size=4, replace=False)
    df.loc[invalid_rows[:2], "Quantity"] = 0
    df.loc[invalid_rows[2:], "Sales"] = -1 * df.loc[invalid_rows[2:], "Sales"].abs()

    # 4. Exact duplicate records
    duplicates = df.sample(n=12, random_state=RANDOM_SEED)
    df = pd.concat([df, duplicates], ignore_index=True)

    df = df.sample(frac=1.0, random_state=RANDOM_SEED).reset_index(drop=True)
    return df


def main() -> None:
    df = build_dataset()
    RAW_DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(RAW_DATA_PATH, index=False)

    print(f"Sample dataset written to: {RAW_DATA_PATH}")
    print(f"Rows: {len(df)} | Columns: {len(df.columns)}")
    print(f"Date range: {df['Order_Date'].min()} to {df['Order_Date'].max()}")
    print(f"Missing cells: {int(df.isna().sum().sum())}")
    print(f"Duplicate rows: {int(df.duplicated().sum())}")


if __name__ == "__main__":
    main()
