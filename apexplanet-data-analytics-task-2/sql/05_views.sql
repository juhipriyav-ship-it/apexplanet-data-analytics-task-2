-- ===========================================================================
-- 05_views.sql
-- ApexPlanet Data Analytics - Task 2
-- Reusable views so common business questions do not have to repeat the same
-- aggregations.  Applied automatically by `python scripts/db_utils.py --load`.
-- ===========================================================================

-- One row per month: order volume, revenue, profit and average order value.
CREATE OR REPLACE VIEW vw_monthly_sales AS
SELECT
    month                                         AS month,
    COUNT(DISTINCT order_id)                      AS orders,
    SUM(sales)                                    AS total_sales,
    SUM(profit)                                   AS total_profit,
    ROUND(SUM(sales) / COUNT(DISTINCT order_id), 2) AS avg_order_value
FROM superstore
GROUP BY month;

-- One row per customer: how much they spend and how often they order.
-- NOTE: a customer can order from more than one region (766 of 793 do), so the
-- view must NOT group by region or the same customer would appear several
-- times.  Region is an order-level attribute, not a customer attribute.
CREATE OR REPLACE VIEW vw_customer_summary AS
SELECT
    customer_id,
    customer_name,
    MAX(segment)              AS segment,
    COUNT(DISTINCT order_id)  AS total_orders,
    COUNT(DISTINCT region)    AS regions_ordered_in,
    SUM(quantity)             AS total_quantity,
    ROUND(SUM(sales), 2)      AS total_sales,
    ROUND(SUM(profit), 2)     AS total_profit,
    ROUND(AVG(sales), 2)      AS avg_line_value
FROM superstore
GROUP BY customer_id, customer_name;

-- One row per product with its revenue and profitability.
CREATE OR REPLACE VIEW vw_product_performance AS
SELECT
    product_id,
    product_name,
    category,
    sub_category,
    SUM(quantity)             AS total_quantity,
    ROUND(SUM(sales), 2)      AS total_sales,
    ROUND(SUM(profit), 2)     AS total_profit,
    ROUND(AVG(discount), 4)   AS avg_discount
FROM superstore
GROUP BY product_id, product_name, category, sub_category;

-- One row per category / sub-category combination.
CREATE OR REPLACE VIEW vw_category_performance AS
SELECT
    category,
    sub_category,
    SUM(quantity)             AS total_quantity,
    ROUND(SUM(sales), 2)      AS total_sales,
    ROUND(SUM(profit), 2)     AS total_profit,
    ROUND(100 * SUM(profit) / NULLIF(SUM(sales), 0), 2) AS profit_margin_pct
FROM superstore
GROUP BY category, sub_category;

-- One row per region.
CREATE OR REPLACE VIEW vw_region_performance AS
SELECT
    region,
    COUNT(DISTINCT order_id)                            AS orders,
    COUNT(DISTINCT customer_id)                         AS customers,
    ROUND(SUM(sales), 2)                                AS total_sales,
    ROUND(SUM(profit), 2)                               AS total_profit,
    ROUND(100 * SUM(profit) / NULLIF(SUM(sales), 0), 2) AS profit_margin_pct
FROM superstore
GROUP BY region;
