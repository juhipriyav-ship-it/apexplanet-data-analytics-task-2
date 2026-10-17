-- ===========================================================================
-- 02_basic_queries.sql
-- ApexPlanet Data Analytics - Task 2 : Day 7-8 SQL Fundamentals
-- Demonstrates: SELECT, WHERE, ORDER BY, LIMIT, DISTINCT, GROUP BY,
--               HAVING, JOIN, aliases, and the common operators.
--
-- Every statement below is written to be runnable on its own in MySQL
-- Workbench, the mysql CLI, or via:
--     python scripts/db_utils.py --query "<paste a query here>"
-- ===========================================================================


-- ---------------------------------------------------------------------------
-- 1. SELECT - choosing the columns we want
-- ---------------------------------------------------------------------------

-- 1.1 Select every column for the first five rows.
SELECT *
FROM superstore
LIMIT 5;

-- 1.2 Select specific columns, with aliases to make the output readable.
SELECT
    order_id,
    order_date,
    customer_name,
    product_name,
    sales,
    profit
FROM superstore
LIMIT 10;

-- 1.3 Computed column: profit as a percentage of sales.
SELECT
    order_id,
    product_name,
    sales,
    profit,
    ROUND(100 * profit / NULLIF(sales, 0), 2) AS profit_margin_pct
FROM superstore
LIMIT 10;


-- ---------------------------------------------------------------------------
-- 2. WHERE - filtering rows
-- ---------------------------------------------------------------------------

-- 2.1 Simple equality filter.
SELECT order_id, category, sub_category, sales, profit
FROM superstore
WHERE category = 'Technology'
ORDER BY sales DESC
LIMIT 10;

-- 2.2 Multiple conditions with AND / OR (parentheses control the logic).
SELECT order_id, region, category, sales, profit
FROM superstore
WHERE (region = 'West' OR region = 'East')
  AND profit > 500
ORDER BY profit DESC
LIMIT 15;

-- 2.3 IN, BETWEEN and date comparison.
SELECT order_id, order_date, region, sales
FROM superstore
WHERE region IN ('Central', 'South')
  AND order_date BETWEEN '2017-01-01' AND '2017-03-31'
ORDER BY order_date
LIMIT 20;

-- 2.4 Pattern matching with LIKE.
SELECT DISTINCT product_name
FROM superstore
WHERE product_name LIKE '%Chair%'
ORDER BY product_name
LIMIT 15;

-- 2.5 Rows that lost money (negative profit).
SELECT order_id, customer_name, sub_category, sales, discount, profit
FROM superstore
WHERE profit < 0
ORDER BY profit ASC
LIMIT 15;

-- 2.6 NOT NULL / IS NULL checks.
SELECT COUNT(*) AS rows_with_missing_city
FROM superstore
WHERE city IS NULL;


-- ---------------------------------------------------------------------------
-- 3. ORDER BY and LIMIT - sorting and top-N
-- ---------------------------------------------------------------------------

-- 3.1 Single-column sort, highest sales first.
SELECT order_id, customer_name, product_name, sales
FROM superstore
ORDER BY sales DESC
LIMIT 10;

-- 3.2 Multi-column sort: sales descending, then profit descending as a tie-break.
SELECT category, sub_category, sales, profit
FROM superstore
ORDER BY sales DESC, profit DESC
LIMIT 10;

-- 3.3 Offset paging: rows 11-20 of the same ranking.
SELECT order_id, sales
FROM superstore
ORDER BY sales DESC
LIMIT 10 OFFSET 10;


-- ---------------------------------------------------------------------------
-- 4. DISTINCT - unique value lists
-- ---------------------------------------------------------------------------

SELECT DISTINCT category    FROM superstore ORDER BY category;
SELECT DISTINCT region      FROM superstore ORDER BY region;
SELECT DISTINCT segment     FROM superstore ORDER BY segment;
SELECT DISTINCT ship_mode   FROM superstore ORDER BY ship_mode;

-- Distinct combinations of two columns.
SELECT DISTINCT category, sub_category
FROM superstore
ORDER BY category, sub_category;


-- ---------------------------------------------------------------------------
-- 5. GROUP BY - aggregating rows into groups
-- ---------------------------------------------------------------------------

-- 5.1 Sales and profit by category.
SELECT
    category,
    COUNT(*)              AS line_items,
    SUM(quantity)         AS units_sold,
    ROUND(SUM(sales), 2)  AS total_sales,
    ROUND(SUM(profit), 2) AS total_profit,
    ROUND(AVG(sales), 2)  AS avg_line_value
FROM superstore
GROUP BY category
ORDER BY total_sales DESC;

-- 5.2 Grouping by two columns (category + sub-category).
SELECT
    category,
    sub_category,
    ROUND(SUM(sales), 2)  AS total_sales,
    ROUND(SUM(profit), 2) AS total_profit
FROM superstore
GROUP BY category, sub_category
ORDER BY category, total_sales DESC;

-- 5.3 Grouping by a date part - yearly summary.
SELECT
    YEAR(order_date)      AS sales_year,
    COUNT(DISTINCT order_id) AS orders,
    ROUND(SUM(sales), 2)  AS total_sales,
    ROUND(SUM(profit), 2) AS total_profit
FROM superstore
GROUP BY YEAR(order_date)
ORDER BY sales_year;


-- ---------------------------------------------------------------------------
-- 6. HAVING - filtering the aggregated result
--        (WHERE filters rows *before* grouping, HAVING filters groups *after*)
-- ---------------------------------------------------------------------------

-- 6.1 Sub-categories that generated more than $100,000 in sales.
SELECT
    sub_category,
    ROUND(SUM(sales), 2) AS total_sales
FROM superstore
GROUP BY sub_category
HAVING SUM(sales) > 100000
ORDER BY total_sales DESC;

-- 6.2 Combining WHERE (row filter) with HAVING (group filter).
SELECT
    category,
    sub_category,
    COUNT(*)              AS line_items,
    ROUND(SUM(sales), 2)  AS total_sales
FROM superstore
WHERE discount > 0                       -- only discounted lines...
GROUP BY category, sub_category
HAVING COUNT(*) >= 100                   -- ...in sub-categories with 100+ such lines
ORDER BY total_sales DESC;

-- 6.3 Groups whose average profit is negative.
SELECT
    sub_category,
    ROUND(AVG(profit), 2) AS avg_profit,
    ROUND(SUM(profit), 2) AS total_profit
FROM superstore
GROUP BY sub_category
HAVING AVG(profit) < 0
ORDER BY total_profit ASC;


-- ---------------------------------------------------------------------------
-- 7. JOIN - combining rows from more than one row source
--
-- The Superstore dataset is a single denormalised table, so instead of
-- separate customer / product tables we join the base table to derived
-- tables and views.  The JOIN syntax is exactly the same as it would be
-- with fully normalised tables.
-- ---------------------------------------------------------------------------

-- 7.1 INNER JOIN against a derived table: every order line for customers
--     whose lifetime spend is above $10,000.
SELECT
    s.order_id,
    s.customer_name,
    s.product_name,
    ROUND(s.sales, 2)              AS line_sales,
    ROUND(big.total_sales, 2)      AS customer_lifetime_sales
FROM superstore AS s
INNER JOIN (
    SELECT customer_id, SUM(sales) AS total_sales
    FROM superstore
    GROUP BY customer_id
    HAVING SUM(sales) > 10000
) AS big
    ON big.customer_id = s.customer_id
ORDER BY big.total_sales DESC, s.sales DESC
LIMIT 20;

-- 7.2 INNER JOIN against a view: pair each line item with its
--     category-level benchmark.
SELECT
    s.sub_category,
    ROUND(s.sales, 2)               AS line_sales,
    c.total_sales                   AS sub_category_sales,
    s.category
FROM superstore AS s
INNER JOIN vw_category_performance AS c
    ON c.category = s.category
   AND c.sub_category = s.sub_category
ORDER BY c.total_sales DESC, s.sales DESC
LIMIT 20;

-- 7.3 LEFT JOIN: list every customer with their region's performance, keeping
--     customers even if the join finds no match (the right side is NULL then).
SELECT
    s.customer_name,
    s.region,
    r.orders,
    r.total_sales AS region_sales
FROM (SELECT DISTINCT customer_name, region FROM superstore) AS s
LEFT JOIN vw_region_performance AS r
    ON r.region = s.region
ORDER BY s.customer_name
LIMIT 25;

-- 7.4 SELF JOIN: find pairs of different customers who live in the same city
--     and are in the same segment (a look-alike customer analysis).
SELECT
    a.city,
    a.segment,
    a.customer_name AS customer_a,
    b.customer_name AS customer_b
FROM (SELECT DISTINCT customer_id, customer_name, city, segment FROM superstore) AS a
INNER JOIN (SELECT DISTINCT customer_id, customer_name, city, segment FROM superstore) AS b
    ON a.city = b.city
   AND a.segment = b.segment
   AND a.customer_id < b.customer_id   -- avoid duplicates and self-matches
ORDER BY a.city, a.customer_name
LIMIT 25;
