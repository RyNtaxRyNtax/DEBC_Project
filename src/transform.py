import pandas as pd
import numpy as np
import logging


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """Standardize columns, strip whitespace, and parse dates based on exact raw data structure."""
    df.columns = df.columns.str.strip().str.lower()
    text_cols = df.select_dtypes(include=["object"]).columns
    for col in text_cols:
        df[col] = df[col].astype(str).str.strip()
    # Title-case text fields
    if "customer_city" in df.columns:
        df["customer_city"] = df["customer_city"].str.title()
    if "branch_city" in df.columns:
        df["branch_city"] = df["branch_city"].str.title()
    if "category_name" in df.columns:
        df["category_name"] = df["category_name"].str.title()
    # Merge first name and last name into a single 'name' column
    if "customer_first_name" in df.columns and "customer_last_name" in df.columns:
        df["customer_name"] = df["customer_first_name"] + " " + df["customer_last_name"]
    # Parse dates
    if "sale_date" in df.columns:
        df["sale_date"] = pd.to_datetime(df["sale_date"], errors="coerce")
    if "customer_signup_date" in df.columns:
        df["customer_signup_date"] = pd.to_datetime(
            df["customer_signup_date"], errors="coerce"
        )
    if "inventory_snapshot_date" in df.columns:
        df["inventory_snapshot_date"] = pd.to_datetime(
            df["inventory_snapshot_date"], errors="coerce"
        )
    df = df.drop_duplicates()
    return df


def calculate_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """Perform vectorized financial calculations using discount percentage."""
    df = df.copy()
    cols_to_fill = ["quantity", "unit_price", "unit_cost", "discount_percent"]
    for col in cols_to_fill:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)
    # Financial Math
    df["gross_revenue"] = df["quantity"] * df["unit_price"]
    # Calculate exact discount amount from percentage
    df["discount_amount"] = df["gross_revenue"] * (df["discount_percent"] / 100)
    df["net_revenue"] = df["gross_revenue"] - df["discount_amount"]
    df["gross_profit"] = df["net_revenue"] - (df["quantity"] * df["unit_cost"])
    df["margin_percent"] = np.where(
        df["net_revenue"] > 0, (df["gross_profit"] / df["net_revenue"]) * 100, 0
    )
    return df


def generate_dimensions_and_facts(df: pd.DataFrame):
    """Split into dimensions and facts mapping exact column names to DB schema."""
    # 1. Customers
    dim_customers = df[
        [
            "customer_id",
            "customer_name",
            "customer_email",
            "customer_phone",
            "customer_city",
            "customer_signup_date",
        ]
    ].drop_duplicates(subset=["customer_id"], keep="last")
    dim_customers.rename(
        columns={
            "customer_name": "name",
            "customer_email": "email",
            "customer_phone": "phone",
            "customer_city": "city",
            "customer_signup_date": "signup_date",
        },
        inplace=True,
    )
    # 2. Categories (Generating stable keys)
    if "category_id" not in df.columns:
        categories = (
            df[["category_name"]].drop_duplicates().dropna().reset_index(drop=True)
        )
        categories["category_id"] = [
            "CAT_" + str(i).zfill(3) for i in range(1, len(categories) + 1)
        ]
        df = df.merge(categories, on="category_name", how="left")
    dim_categories = df[["category_id", "category_name"]].drop_duplicates(
        subset=["category_id"]
    )
    # 3. Products
    dim_products = df[
        ["product_id", "product_name", "category_id", "unit_cost", "unit_price"]
    ].drop_duplicates(subset=["product_id"])
    # 4. Branches
    dim_branches = df[
        ["branch_id", "branch_name", "branch_city", "sales_channel"]
    ].drop_duplicates(subset=["branch_id"])
    dim_branches.rename(columns={"branch_city": "city"}, inplace=True)
    # 5. Sales Fact
    fact_sales = df[
        [
            "sale_id",
            "sale_date",
            "customer_id",
            "product_id",
            "branch_id",
            "quantity",
            "discount_amount",
            "gross_revenue",
            "net_revenue",
            "gross_profit",
            "margin_percent",
        ]
    ].drop_duplicates(subset=["sale_id"])
    # 6. Inventory Snapshot Fact
    fact_inventory = df[
        [
            "inventory_snapshot_date",
            "product_id",
            "branch_id",
            "stock_quantity",
            "reorder_level",
        ]
    ].drop_duplicates()
    fact_inventory.rename(
        columns={"inventory_snapshot_date": "snapshot_date"}, inplace=True
    )
    return (
        dim_customers,
        dim_categories,
        dim_products,
        dim_branches,
        fact_sales,
        fact_inventory,
    )
