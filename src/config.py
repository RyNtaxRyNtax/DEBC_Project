import os

# DB Connection Configs
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_USER = os.getenv("DB_USER", "retail_user")
DB_PASS = os.getenv("DB_PASS", "retail_password")
DB_NAME = os.getenv("DB_NAME", "retail_db")

DB_PARAMS = {
    "host": DB_HOST,
    "port": DB_PORT,
    "user": DB_USER,
    "password": DB_PASS,
    "database": DB_NAME,
}

# File Paths
RAW_DATA_PATH = "data/raw/raw.csv"
REJECTED_DIR = "data/processed/rejected_records"
REPORTS_DIR = "reports/charts"
