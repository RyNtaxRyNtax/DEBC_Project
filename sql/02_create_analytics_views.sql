-- Daily revenue trend view
CREATE OR REPLACE VIEW vw_daily_revenue AS
SELECT 
    sale_date,
    SUM(gross_revenue) AS total_revenue,
    SUM(net_revenue) AS net_revenue,
    SUM(gross_profit) AS gross_profit,
    SUM(quantity) AS total_quantity_sold
FROM fact_sales
GROUP BY sale_date
ORDER BY sale_date;

-- Revenue by product view
CREATE OR REPLACE VIEW vw_product_revenue AS
SELECT 
    p.product_name,
    c.category_name,
    SUM(s.quantity) AS total_quantity,
    SUM(s.net_revenue) AS net_revenue
FROM fact_sales s
JOIN dim_products p ON s.product_id = p.product_id
JOIN dim_categories c ON p.category_id = c.category_id
GROUP BY p.product_name, c.category_name
ORDER BY net_revenue DESC;

-- Revenue by branch view
CREATE OR REPLACE VIEW vw_branch_revenue AS
SELECT 
    b.branch_name,
    b.city,
    SUM(s.net_revenue) AS net_revenue
FROM fact_sales s
JOIN dim_branches b ON s.branch_id = b.branch_id
GROUP BY b.branch_name, b.city
ORDER BY net_revenue DESC;

-- Category gross margin view
CREATE OR REPLACE VIEW vw_category_margin AS
SELECT 
    c.category_name,
    SUM(s.net_revenue) AS net_revenue,
    SUM(s.gross_profit) AS gross_profit,
    CASE 
        WHEN SUM(s.net_revenue) > 0 THEN (SUM(s.gross_profit) / SUM(s.net_revenue)) * 100 
        ELSE 0 
    END AS margin_percent
FROM fact_sales s
JOIN dim_products p ON s.product_id = p.product_id
JOIN dim_categories c ON p.category_id = c.category_id
GROUP BY c.category_name
ORDER BY margin_percent DESC;

-- Customer lifetime value and average order value view
CREATE OR REPLACE VIEW vw_customer_lifetime_value AS
SELECT 
    c.customer_id,
    c.name,
    COUNT(s.sale_id) AS total_orders,
    SUM(s.net_revenue) AS lifetime_value,
    CASE 
        WHEN COUNT(s.sale_id) > 0 THEN SUM(s.net_revenue) / COUNT(s.sale_id)
        ELSE 0 
    END AS average_order_value
FROM fact_sales s
JOIN dim_customers c ON s.customer_id = c.customer_id
GROUP BY c.customer_id, c.name
ORDER BY lifetime_value DESC;

-- Stockout risk view (products below reorder level)
CREATE OR REPLACE VIEW vw_stockout_risk AS
SELECT 
    p.product_name,
    b.branch_name,
    i.stock_quantity,
    i.reorder_level,
    (i.stock_quantity - i.reorder_level) AS safety_stock_margin
FROM fact_inventory_snapshot i
JOIN dim_products p ON i.product_id = p.product_id
JOIN dim_branches b ON i.branch_id = b.branch_id
WHERE i.stock_quantity <= i.reorder_level
ORDER BY safety_stock_margin ASC;