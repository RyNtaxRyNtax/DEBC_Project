import pandas as pd
import logging
import os
from config import RAW_DATA_PATH

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


def extract_raw_data() -> pd.DataFrame:
    """Read raw CSV file and perform initial validation."""
    if not os.path.exists(RAW_DATA_PATH):
        raise FileNotFoundError(f"Raw data file not found at {RAW_DATA_PATH}")
    logging.info(f"Extracting data from {RAW_DATA_PATH}...")
    df = pd.read_csv(RAW_DATA_PATH)
    # Log data profiling metrics as required
    logging.info(f"Raw data shape: {df.shape[0]} rows, {df.shape[1]} columns")
    null_counts = df.isnull().sum()
    logging.info(f"Null values per column:\n{null_counts[null_counts > 0]}")
    logging.info(f"Duplicate rows: {df.duplicated().sum()}")
    # Generate basic numeric profile
    numeric_cols = df.select_dtypes(include=["number"]).columns
    if not numeric_cols.empty:
        logging.info(f"Basic numeric statistics:\n{df[numeric_cols].describe()}")
    return df
