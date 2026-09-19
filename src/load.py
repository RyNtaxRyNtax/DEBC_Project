import psycopg2
import psycopg2.extras
import pandas as pd
import numpy as np
import logging
from config import DB_PARAMS


def get_connection():
    """Establish connection to PostgreSQL using environment variables."""
    return psycopg2.connect(**DB_PARAMS)


def upsert_dataframe(df: pd.DataFrame, table_name: str, primary_key: str, conn):
    """
    Idempotent load: Insert new records or update existing ones based on the primary key.
    """
    if df.empty:
        logging.info(f"No data to load for table {table_name}.")
        return
    # Replace Pandas NaNs with Python None for PostgreSQL compatibility
    df_clean = df.replace({np.nan: None, pd.NaT: None})
    columns = list(df_clean.columns)
    values = [tuple(x) for x in df_clean.to_numpy()]
    cols_str = ", ".join(columns)
    # Create EXCLUDED string for updating existing records
    update_cols = [col for col in columns if col != primary_key]
    if update_cols:
        update_str = ", ".join([f"{col} = EXCLUDED.{col}" for col in update_cols])
        conflict_action = f"DO UPDATE SET {update_str}"
    else:
        conflict_action = "DO NOTHING"
    query = f"""
        INSERT INTO {table_name} ({cols_str})
        VALUES %s
        ON CONFLICT ({primary_key}) {conflict_action};
    """
    cursor = conn.cursor()
    try:
        psycopg2.extras.execute_values(cursor, query, values, page_size=1000)
        conn.commit()
        logging.info(f"Successfully loaded {len(df)} records into {table_name}.")
    except Exception as e:
        conn.rollback()
        logging.error(f"Error loading data into {table_name}: {e}")
        raise
    finally:
        cursor.close()


def insert_without_conflict(df: pd.DataFrame, table_name: str, conn):
    """Simple bulk insert for tables with auto-incrementing serial IDs (like fact_inventory_snapshot)."""
    if df.empty:
        return
    df_clean = df.replace({np.nan: None, pd.NaT: None})
    columns = list(df_clean.columns)
    values = [tuple(x) for x in df_clean.to_numpy()]
    cols_str = ", ".join(columns)
    query = f"INSERT INTO {table_name} ({cols_str}) VALUES %s;"
    cursor = conn.cursor()
    try:
        # Delete existing data for the same snapshot dates to maintain idempotency
        if "snapshot_date" in df_clean.columns:
            # Extract unique dates, explicitly filtering out None and NaT strings
            valid_dates = [
                str(d)
                for d in df_clean["snapshot_date"].unique()
                if d is not None and str(d) != "NaT"
            ]
            if valid_dates:
                cursor.execute(
                    f"DELETE FROM {table_name} WHERE snapshot_date IN %s",
                    (tuple(valid_dates),),
                )
        psycopg2.extras.execute_values(cursor, query, values, page_size=1000)
        conn.commit()
        logging.info(f"Successfully loaded {len(df)} records into {table_name}.")
    except Exception as e:
        conn.rollback()
        logging.error(f"Error loading data into {table_name}: {e}")
        raise
    finally:
        cursor.close()


def load_data_to_postgres(
    dim_customers,
    dim_categories,
    dim_products,
    dim_branches,
    fact_sales,
    fact_inventory,
):
    """Load all dataframes into the database in the correct dependency order."""
    conn = get_connection()
    try:
        # 1. Load independent dimensions first
        upsert_dataframe(dim_customers, "dim_customers", "customer_id", conn)
        upsert_dataframe(dim_categories, "dim_categories", "category_id", conn)
        upsert_dataframe(dim_branches, "dim_branches", "branch_id", conn)
        # 2. Load dependent dimensions (products depend on categories)
        upsert_dataframe(dim_products, "dim_products", "product_id", conn)
        # 3. Load facts (depend on all dimensions)
        upsert_dataframe(fact_sales, "fact_sales", "sale_id", conn)
        insert_without_conflict(fact_inventory, "fact_inventory_snapshot", conn)
    finally:
        conn.close()
        logging.info("Database connection closed.")
