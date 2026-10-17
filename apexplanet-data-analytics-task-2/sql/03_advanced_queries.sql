-- ===========================================================================
-- 03_advanced_queries.sql
-- ApexPlanet Data Analytics - Task 2 : Day 9-10 Advanced SQL
-- Demonstrates: subqueries (scalar, derived, correlated), CTEs (WITH),
--               window functions (ROW_NUMBER, RANK, DENSE_RANK, LAG, LEAD,
--               NTILE, SUM/AVG OVER), and reusable views.
--
-- Requires MySQL 8.0+ (window functions and CTEs).
-- ===========================================================================


-- ---------------------------------------------------------------------------
-- 1. SUBQUERIES
-- ---------------------------------------------------------------------------

-- 1.1 Scalar subquery in WHERE: orders that beat the overall average sale.
SELECT
    order_id,
    customer_name,
    ROUND(sales, 2) AS sales
FROM superstore
WHERE sales > (SELECT AVG(sales) FROM superstore)
ORDER BY sales DESC
LIMIT 15;

-- 1.2 Subquery in the SELECT list: compare each line with the global average.
SELECT
    order_id,
    ROUND(sales, 2)                    AS sales,
    ROUND((SELECT AVG(sales) FROM superstore), 2) AS overall_avg_sales,
    ROUND(sales - (SELECT AVG(sales) FROM superstore), 2) AS difference
FROM superstore
ORDER BY sales DESC
LIMIT 10;

-- 1.3 Derived table in FROM: aggregate first, then filter the aggregate.
--     (This avoids repeating the aggregation in a HAVING clause.)
SELECT
    customer_name,
    orders,
    ROUND(total_sales, 2)  AS total_sales,
    ROUND(total_profit, 2) AS total_profit
FROM (
    SELECT
        customer_id,
        customer_name,
        COUNT(DISTINCT order_id) AS orders,
        SUM(sales)               AS total_sales,
        SUM(profit)              AS total_profit
    FROM superstore
    GROUP BY customer_id, customer_name
) AS customer_totals
WHERE orders >= 10
ORDER BY total_sales DESC
LIMIT 15;

-- 1.4 Correlated subquery in the SELECT list: the subquery re-runs for every
--     outer row and refers back to it through the alias s.customer_id.
--     Here each line item is annotated with its own customer's lifetime sales.
SELECT
    s.order_id,
    s.customer_name,
    ROUND(s.sales, 2) AS line_sales,
    (
        SELECT ROUND(SUM(x.sales), 2)
        FROM superstore AS x
        WHERE x.customer_id = s.customer_id
    ) AS customer_lifetime_sales
FROM superstore AS s
ORDER BY s.sales DESC
LIMIT 10;

-- 1.5 EXISTS: customers who have placed at least one loss-making order.
SELECT DISTINCT
    s.customer_id,
    s.customer_name
FROM superstore AS s
WHERE EXISTS (
    SELECT 1
    FROM superstore AS losers
    WHERE losers.customer_id = s.customer_id
      AND losers.profit < 0
)
ORDER BY s.customer_name
LIMIT 20;


-- ---------------------------------------------------------------------------
-- 2. COMMON TABLE EXPRESSIONS (CTEs) - the WITH clause
--    A CTE is a named subquery declared up front, which makes long queries
--    readable and lets you reuse the same intermediate result.
-- ---------------------------------------------------------------------------

-- 2.1 A single CTE.
WITH monthly AS (
    SELECT
        month,
        SUM(sales)  AS total_sales,
        SUM(profit) AS total_profit
    FROM superstore
    GROUP BY month
)
SELECT
    month,
    ROUND(total_sales, 2)  AS total_sales,
    ROUND(total_profit, 2) AS total_profit
FROM monthly
ORDER BY month;

-- 2.2 Two chained CTEs: first aggregate per sub-category, then rank them.
WITH sub_category_totals AS (
    SELECT
        category,
        sub_category,
        SUM(sales)  AS total_sales,
        SUM(profit) AS total_profit
    FROM superstore
    GROUP BY category, sub_category
),
ranked AS (
    SELECT
        category,
        sub_category,
        total_sales,
        total_profit,
        RANK() OVER (ORDER BY total_profit DESC) AS profit_rank
    FROM sub_category_totals
)
SELECT
    profit_rank,
    category,
    sub_category,
    ROUND(total_sales, 2)  AS total_sales,
    ROUND(total_profit, 2) AS total_profit
FROM ranked
ORDER BY profit_rank;

-- 2.3 A CTE that is referenced twice - not possible with a plain derived table
--     without repeating the SQL.
WITH customer_totals AS (
    SELECT
        customer_id,
        customer_name,
        SUM(sales) AS total_sales
    FROM superstore
    GROUP BY customer_id, customer_name
)
SELECT
    c.customer_name,
    ROUND(c.total_sales, 2)                       AS customer_sales,
    ROUND((SELECT AVG(total_sales) FROM customer_totals), 2) AS avg_customer_sales,
    ROUND(c.total_sales / (SELECT AVG(total_sales) FROM customer_totals), 2) AS times_average
FROM customer_totals AS c
ORDER BY c.total_sales DESC
LIMIT 10;

-- 2.4 Recursive CTE: generate a simple calendar of years present in the data.
--     (Shows the WITH RECURSIVE syntax.)
WITH RECURSIVE years AS (
    SELECT MIN(YEAR(order_date)) AS yr FROM superstore
    UNION ALL
    SELECT yr + 1 FROM years WHERE yr < (SELECT MAX(YEAR(order_date)) FROM superstore)
)
SELECT yr AS sales_year
FROM years
ORDER BY sales_year;


-- ---------------------------------------------------------------------------
-- 3. WINDOW FUNCTIONS
--    A window function computes across a set of rows related to the current
--    row *without* collapsing them the way GROUP BY does.
-- ---------------------------------------------------------------------------

-- 3.1 ROW_NUMBER - assign a unique sequential number.
--     Top 5 selling products overall.
SELECT
    rn,
    product_name,
    ROUND(total_sales, 2) AS total_sales
FROM (
    SELECT
        product_name,
        SUM(sales) AS total_sales,
        ROW_NUMBER() OVER (ORDER BY SUM(sales) DESC) AS rn
    FROM superstore
    GROUP BY product_name
) AS ranked
WHERE rn <= 5
ORDER BY rn;

-- 3.2 RANK vs DENSE_RANK - the difference appears when values tie.
--     (`row_number` is a reserved word in MySQL 8, hence the alias `row_num`.)
SELECT
    sub_category,
    ROUND(SUM(profit), 2)                             AS total_profit,
    RANK()       OVER (ORDER BY SUM(profit) DESC)     AS rank_with_gaps,
    DENSE_RANK() OVER (ORDER BY SUM(profit) DESC)     AS rank_no_gaps,
    ROW_NUMBER() OVER (ORDER BY SUM(profit) DESC)     AS row_num
FROM superstore
GROUP BY sub_category
ORDER BY total_profit DESC;

-- 3.3 ROW_NUMBER with PARTITION BY - the top 3 products *within each category*.
SELECT
    category,
    product_name,
    ROUND(total_sales, 2) AS total_sales
FROM (
    SELECT
        category,
        product_name,
        SUM(sales) AS total_sales,
        ROW_NUMBER() OVER (PARTITION BY category ORDER BY SUM(sales) DESC) AS rn
    FROM superstore
    GROUP BY category, product_name
) AS ranked
WHERE rn <= 3
ORDER BY category, total_sales DESC;

-- 3.4 LAG and LEAD - compare a month with the previous and next month.
WITH monthly AS (
    SELECT
        month,
        SUM(sales) AS total_sales
    FROM superstore
    GROUP BY month
)
SELECT
    month,
    ROUND(total_sales, 2)                                     AS total_sales,
    ROUND(LAG(total_sales)  OVER (ORDER BY month), 2)          AS prev_month_sales,
    ROUND(LEAD(total_sales) OVER (ORDER BY month), 2)          AS next_month_sales,
    ROUND(total_sales - LAG(total_sales) OVER (ORDER BY month), 2) AS month_over_month_change
FROM monthly
ORDER BY month;

-- 3.5 Running total and running average with SUM() OVER and AVG() OVER.
WITH monthly AS (
    SELECT
        month,
        SUM(sales) AS total_sales
    FROM superstore
    GROUP BY month
)
SELECT
    month,
    ROUND(total_sales, 2) AS total_sales,
    ROUND(SUM(total_sales) OVER (ORDER BY month), 2) AS running_total,
    ROUND(AVG(total_sales) OVER (ORDER BY month), 2) AS running_avg
FROM monthly
ORDER BY month;

-- 3.6 Moving average - a 3-month window around the current month.
WITH monthly AS (
    SELECT
        month,
        SUM(sales) AS total_sales
    FROM superstore
    GROUP BY month
)
SELECT
    month,
    ROUND(total_sales, 2) AS total_sales,
    ROUND(
        AVG(total_sales) OVER (
            ORDER BY month
            ROWS BETWEEN 1 PRECEDING AND 1 FOLLOWING
        ), 2
    ) AS moving_avg_3m
FROM monthly
ORDER BY month;

-- 3.7 NTILE - split customers into four spend quartiles.
SELECT
    customer_name,
    ROUND(total_sales, 2) AS total_sales,
    NTILE(4) OVER (ORDER BY total_sales DESC) AS spend_quartile
FROM (
    SELECT customer_id, customer_name, SUM(sales) AS total_sales
    FROM superstore
    GROUP BY customer_id, customer_name
) AS customers
ORDER BY spend_quartile, total_sales DESC
LIMIT 30;

-- 3.8 Share of total (percentage contribution) using a window aggregate.
SELECT
    category,
    ROUND(SUM(sales), 2) AS total_sales,
    ROUND(100 * SUM(sales) / SUM(SUM(sales)) OVER (), 2) AS pct_of_total_sales
FROM superstore
GROUP BY category
ORDER BY total_sales DESC;


-- ---------------------------------------------------------------------------
-- 4. VIEWS - wrapping recurring logic for reuse
--    The views themselves are defined in sql/05_views.sql.
-- ---------------------------------------------------------------------------

-- 4.1 The view hides the GROUP BY, so a query becomes a one-liner.
SELECT * FROM vw_region_performance ORDER BY total_sales DESC;

-- 4.2 Views can be filtered, joined and aggregated exactly like tables.
SELECT
    category,
    sub_category,
    total_sales,
    total_profit,
    profit_margin_pct
FROM vw_category_performance
WHERE profit_margin_pct < 0
ORDER BY total_profit;

-- 4.3 Ranking on top of a view.
SELECT
    region,
    total_sales,
    total_profit,
    RANK() OVER (ORDER BY total_sales DESC) AS sales_rank
FROM vw_region_performance;
