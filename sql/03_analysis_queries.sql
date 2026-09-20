-- Daily revenue trend
SELECT * FROM vw_daily_revenue;

-- Top 10 products by revenue
SELECT * FROM vw_product_revenue LIMIT 10;

-- Top branches by revenue
SELECT * FROM vw_branch_revenue;

-- Category-level profitability
SELECT * FROM vw_category_margin;

-- Top 10 customers by lifetime value (LTV)
SELECT * FROM vw_customer_lifetime_value LIMIT 10;

-- Stockout risk report
SELECT * FROM vw_stockout_risk;