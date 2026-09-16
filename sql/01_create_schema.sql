-- Dimension Table 
CREATE TABLE IF NOT EXISTS dim_customers (
    customer_id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(100),
    email VARCHAR(100),
    phone VARCHAR(50),
    city VARCHAR(100),
    signup_date DATE
);

CREATE TABLE IF NOT EXISTS dim_categories (
    category_id VARCHAR(50) PRIMARY KEY,
    category_name VARCHAR(100)
);

CREATE TABLE IF NOT EXISTS dim_products (
    product_id VARCHAR(50) PRIMARY KEY,
    product_name VARCHAR(255),
    category_id VARCHAR(50) REFERENCES dim_categories(category_id),
    unit_cost NUMERIC(10, 2),
    unit_price NUMERIC(10, 2)
);

CREATE TABLE IF NOT EXISTS dim_branches (
    branch_id VARCHAR(50) PRIMARY KEY,
    branch_name VARCHAR(100),
    city VARCHAR(100),
    sales_channel VARCHAR(50)
);

-- Fact Table
CREATE TABLE IF NOT EXISTS fact_sales (
    sale_id VARCHAR(50) PRIMARY KEY,
    sale_date DATE,
    customer_id VARCHAR(50) REFERENCES dim_customers(customer_id),
    product_id VARCHAR(50) REFERENCES dim_products(product_id),
    branch_id VARCHAR(50) REFERENCES dim_branches(branch_id),
    quantity INT,
    discount_amount NUMERIC(10, 2),
    gross_revenue NUMERIC(10, 2),
    net_revenue NUMERIC(10, 2),
    gross_profit NUMERIC(10, 2),
    margin_percent NUMERIC(10, 2)
);

CREATE TABLE IF NOT EXISTS fact_inventory_snapshot (
    snapshot_id SERIAL PRIMARY KEY,
    snapshot_date DATE,
    product_id VARCHAR(50) REFERENCES dim_products(product_id),
    branch_id VARCHAR(50) REFERENCES dim_branches(branch_id),
    stock_quantity INT,
    reorder_level INT
);