import pandas as pd
import os
import logging
from config import REJECTED_DIR

# Ensure the rejected directory exists
os.makedirs(REJECTED_DIR, exist_ok=True)


def validate_and_filter_sales(
    fact_sales: pd.DataFrame,
    dim_customers: pd.DataFrame,
    dim_products: pd.DataFrame,
    dim_branches: pd.DataFrame,
) -> pd.DataFrame:
    """
    Validate sales fact table against quality rules and quarantine invalid records.
    Rules: No negative quantities/prices, no null keys, must reference existing dimensions.
    """
    initial_count = len(fact_sales)
    # Rule 1: No negative sales quantity or negative revenues
    invalid_quantity = fact_sales["quantity"] < 0
    invalid_revenue = fact_sales["gross_revenue"] < 0
    # Rule 2: Required key fields cannot be null
    null_keys = (
        fact_sales[["sale_id", "customer_id", "product_id", "branch_id"]]
        .isnull()
        .any(axis=1)
    )
    # Rule 3: Referential integrity (Foreign keys must exist in Dimension tables)
    invalid_customer = ~fact_sales["customer_id"].isin(dim_customers["customer_id"])
    invalid_product = ~fact_sales["product_id"].isin(dim_products["product_id"])
    invalid_branch = ~fact_sales["branch_id"].isin(dim_branches["branch_id"])
    # Combine all invalid conditions using bitwise OR
    is_invalid = (
        invalid_quantity
        | invalid_revenue
        | null_keys
        | invalid_customer
        | invalid_product
        | invalid_branch
    )
    # Split data into valid and rejected DataFrames
    valid_sales = fact_sales[~is_invalid].copy()
    rejected_sales = fact_sales[is_invalid].copy()
    # Save rejected records to quarantine directory
    if not rejected_sales.empty:
        rejected_path = os.path.join(REJECTED_DIR, "rejected_sales.csv")
        rejected_sales.to_csv(rejected_path, index=False)
        logging.warning(
            f"Rejected {len(rejected_sales)} sales records. Saved to {rejected_path}"
        )
    logging.info(
        f"Fact Sales validation complete. Valid records: {len(valid_sales)} / {initial_count}"
    )
    return valid_sales


def validate_and_filter_inventory(
    fact_inventory: pd.DataFrame, dim_products: pd.DataFrame, dim_branches: pd.DataFrame
) -> pd.DataFrame:
    """
    Validate inventory fact table against quality rules and quarantine invalid records.
    """
    if fact_inventory.empty:
        return fact_inventory
    initial_count = len(fact_inventory)
    # Rule: Inventory stock quantity cannot be negative
    invalid_stock = fact_inventory["stock_quantity"] < 0
    # Rule: Required fields cannot be null
    null_keys = fact_inventory[["product_id", "branch_id"]].isnull().any(axis=1)
    # Rule: Referential integrity
    invalid_product = ~fact_inventory["product_id"].isin(dim_products["product_id"])
    invalid_branch = ~fact_inventory["branch_id"].isin(dim_branches["branch_id"])
    is_invalid = invalid_stock | null_keys | invalid_product | invalid_branch
    valid_inventory = fact_inventory[~is_invalid].copy()
    rejected_inventory = fact_inventory[is_invalid].copy()
    if not rejected_inventory.empty:
        rejected_path = os.path.join(REJECTED_DIR, "rejected_inventory.csv")
        rejected_inventory.to_csv(rejected_path, index=False)
        logging.warning(
            f"Rejected {len(rejected_inventory)} inventory records. Saved to {rejected_path}"
        )
    logging.info(
        f"Fact Inventory validation complete. Valid records: {len(valid_inventory)} / {initial_count}"
    )
    return valid_inventory
