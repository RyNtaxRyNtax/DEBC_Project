import logging
from extract import extract_raw_data
from transform import clean_data, calculate_metrics, generate_dimensions_and_facts
from quality import validate_and_filter_sales, validate_and_filter_inventory
from load import load_data_to_postgres
from reports import generate_charts, generate_summary_report


def main():
    logging.info("Starting Retail Analytics ETL Pipeline...")
    raw_df = extract_raw_data()
    cleaned_df = clean_data(raw_df)
    metrics_df = calculate_metrics(cleaned_df)
    dim_cust, dim_cat, dim_prod, dim_branch, fact_sales, fact_inv = (
        generate_dimensions_and_facts(metrics_df)
    )
    valid_sales = validate_and_filter_sales(fact_sales, dim_cust, dim_prod, dim_branch)
    valid_inv = validate_and_filter_inventory(fact_inv, dim_prod, dim_branch)
    load_data_to_postgres(
        dim_cust, dim_cat, dim_prod, dim_branch, valid_sales, valid_inv
    )
    generate_charts()
    generate_summary_report()
    logging.info("ETL Pipeline completed successfully.")


if __name__ == "__main__":
    main()
