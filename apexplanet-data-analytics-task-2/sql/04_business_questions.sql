-- ===========================================================================
-- 04_business_questions.sql
-- ApexPlanet Data Analytics - Task 2 : Day 11-13
--
-- Ten business questions answered with SQL against the `superstore` table
-- (Sample Superstore dataset, Jan 2014 - Dec 2017, 9,994 order lines).
--
-- Each question is self-contained and can be run on its own.  The interpreted
-- answers below each query were produced by running the query and are also
-- summarised in readme.md.
-- ===========================================================================


-- ===========================================================================
-- Q1. Which are the top 5 products by total sales?
-- ===========================================================================
-- Business value: shows the hero products that carry revenue and are the
-- first candidates for stock planning and marketing focus.
SELECT
    product_name,
    category,
    ROUND(SUM(sales), 2)  AS total_sales,
    SUM(quantity)         AS units_sold
FROM superstore
GROUP BY product_name, category
ORDER BY total_sales DESC
LIMIT 5;

-- ANSWER: the top 5 are the Canon imageCLASS 2200 Advanced Copier ($61,599.82),
-- the Fellowes PB500 binding machine ($27,453.38), the Cisco TelePresence
-- System EX90 ($22,638.48), the HON 5400 task chairs ($21,870.58) and the
-- GBC DocuBind TL300 ($19,823.48).  The Canon alone is ~2.2x the runner-up,
-- and Technology equipment dominates the list - high-ticket items carry
-- revenue here far more than high-volume ones.


-- ===========================================================================
-- Q2. What is the monthly sales trend, and how fast is it growing?
-- ===========================================================================
-- Business value: the month-over-month change separates real growth from
-- seasonal noise, and flags the months that need attention.
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
    ROUND(total_sales - LAG(total_sales) OVER (ORDER BY month), 2) AS mom_change,
    ROUND(
        100 * (total_sales - LAG(total_sales) OVER (ORDER BY month))
        / NULLIF(LAG(total_sales) OVER (ORDER BY month), 0), 2
    ) AS mom_growth_pct
FROM monthly
ORDER BY month;

-- ANSWER: sales grow from $14,236.90 in Jan 2014 to a peak of $118,447.83 in
-- Nov 2017.  The pattern is strongly seasonal rather than a smooth ramp: the
-- biggest months are Nov 2017 ($118.4K), Dec 2016 ($97.0K), Sep 2017 ($87.9K)
-- and Dec 2017 ($83.8K), so September and the Q4 holiday season drive the
-- peaks, while Feb 2014 was the weakest month (-68% on the month).


-- ===========================================================================
-- Q3. How can customers be segmented by their total spend?
-- ===========================================================================
-- Business value: a simple High / Medium / Low value segmentation lets the
-- business target retention spend where it pays back.
WITH customer_spend AS (
    SELECT
        customer_id,
        customer_name,
        SUM(sales) AS total_sales
    FROM superstore
    GROUP BY customer_id, customer_name
)
SELECT
    CASE
        WHEN total_sales >= 5000 THEN 'High Value'
        WHEN total_sales >= 2000 THEN 'Medium Value'
        ELSE 'Low Value'
    END                              AS spend_segment,
    COUNT(*)                         AS customers,
    ROUND(SUM(total_sales), 2)       AS segment_sales,
    ROUND(AVG(total_sales), 2)       AS avg_spend,
    ROUND(100 * SUM(total_sales) / (SELECT SUM(total_sales) FROM customer_spend), 2)
                                     AS pct_of_total_sales
FROM customer_spend
GROUP BY spend_segment
ORDER BY segment_sales DESC;

-- ANSWER: 117 customers (14.8% of the base) are High Value and account for
-- $911,958.27 / 39.70% of all sales; 323 Medium Value customers account for
-- 44.49%; and 353 Low Value customers bring in only 15.81% despite being the
-- largest group.  A High Value customer spends on average $7,794.52 versus
-- $1,028.81 for a Low Value one - a 7.6x difference, so the top ~15% of
-- customers are worth roughly as much as the bottom 45% combined.


-- ===========================================================================
-- Q4. Who are the top 10 customers by sales, and are they profitable?
-- ===========================================================================
-- Business value: revenue without profit is a trap.  Showing sales next to
-- profit and margin exposes big customers who are actually unprofitable.
SELECT
    customer_id,
    customer_name,
    COUNT(DISTINCT order_id)                            AS orders,
    ROUND(SUM(sales), 2)                                AS total_sales,
    ROUND(SUM(profit), 2)                               AS total_profit,
    ROUND(100 * SUM(profit) / NULLIF(SUM(sales), 0), 2) AS profit_margin_pct
FROM superstore
GROUP BY customer_id, customer_name
ORDER BY total_sales DESC
LIMIT 10;

-- ANSWER: Sean Miller is the top customer by sales ($25,043.05) but is
-- *unprofitable* at -$1,980.74 (-7.91% margin) - a big spender that heavy
-- discounting turns into a loss-maker.  Tamara Chand ($19,052.22 / $8,981.32,
-- 47.14% margin) and Raymond Buch ($15,117.34 / $6,976.10, 46.15%) earn
-- similar revenue and far more profit.  Margins across the top 10 range from
-- -7.9% to 47.1%, which is exactly why revenue must never be read alone.


-- ===========================================================================
-- Q5. Which categories and sub-categories drive sales and profit?
-- ===========================================================================
-- Business value: finds the profit engines and, more importantly, the
-- loss-making sub-categories that quietly destroy margin.
SELECT
    category,
    sub_category,
    ROUND(SUM(sales), 2)                                AS total_sales,
    ROUND(SUM(profit), 2)                               AS total_profit,
    ROUND(100 * SUM(profit) / NULLIF(SUM(sales), 0), 2) AS profit_margin_pct
FROM superstore
GROUP BY category, sub_category
ORDER BY category, total_sales DESC;

-- ANSWER: Technology is the most profitable category - $145,454.95 of profit
-- on $836,154.03 of sales (a 17.40% margin) - with Office Supplies a close
-- second at $122,490.80 on $719,047.03 (17.04%).  The best sub-category
-- margins are Labels 44.42%, Paper 43.39%, Envelopes 42.27% and Copiers
-- 37.20%.  Furniture is the problem: $741,999.80 of sales produces only
-- $18,451.27 of profit (2.49%) because Tables (-$17,725.48), Bookcases
-- (-$3,472.56) and Supplies (-$1,189.10) all run at a loss.  Those three
-- sub-categories are the biggest margin killers in the business.


-- ===========================================================================
-- Q6. Which regions perform best on sales, profit and margin?
-- ===========================================================================
-- Ranked with a window function so the ranking is part of the result set.
SELECT
    region,
    COUNT(DISTINCT order_id)                            AS orders,
    COUNT(DISTINCT customer_id)                         AS customers,
    ROUND(SUM(sales), 2)                                AS total_sales,
    ROUND(SUM(profit), 2)                               AS total_profit,
    ROUND(100 * SUM(profit) / NULLIF(SUM(sales), 0), 2) AS profit_margin_pct,
    RANK() OVER (ORDER BY SUM(sales) DESC)              AS sales_rank
FROM superstore
GROUP BY region
ORDER BY total_sales DESC;

-- ANSWER: West ranks 1st ($725,457.82 sales / $108,418.45 profit / 14.94%
-- margin) and East 2nd ($678,781.24 / $91,522.78 / 13.48%).  Central is 3rd on
-- sales ($501,239.89) but has by far the weakest margin at 7.92% - strong
-- revenue, poor profitability.  South is the smallest region
-- ($391,721.91) yet still returns a 11.93% margin, better than Central, so
-- Central's pricing/discounting is the issue rather than its volume.


-- ===========================================================================
-- Q7. How does the discount level affect profitability?
-- ===========================================================================
-- Business value: quantifies the point at which discounting stops buying
-- volume and starts destroying profit.
SELECT
    CASE
        WHEN discount = 0           THEN '0% (no discount)'
        WHEN discount <= 0.10       THEN '1-10%'
        WHEN discount <= 0.20       THEN '11-20%'
        WHEN discount <= 0.30       THEN '21-30%'
        WHEN discount <= 0.40       THEN '31-40%'
        ELSE '41%+'
    END                                                 AS discount_band,
    COUNT(*)                                            AS line_items,
    ROUND(AVG(discount) * 100, 1)                       AS avg_discount_pct,
    ROUND(SUM(sales), 2)                                AS total_sales,
    ROUND(SUM(profit), 2)                               AS total_profit,
    ROUND(100 * SUM(profit) / NULLIF(SUM(sales), 0), 2) AS profit_margin_pct
FROM superstore
GROUP BY discount_band
ORDER BY MIN(discount);

-- ANSWER: profit is healthy at a 29.51% margin on undiscounted lines, stays
-- positive down to about 20% discount (11.58% margin), then turns negative:
-- 21-30% gives -10.05%, 31-40% gives -19.44%, and 41%+ discounts bleed
-- -77.40% on average.  There is a clear cliff: discounting beyond ~20% stops
-- buying extra volume and starts destroying profit.  The 933 lines in the
-- 41%+ band alone lose $99,558.59.


-- ===========================================================================
-- Q8. What are the top 3 selling products in each category?
-- ===========================================================================
-- ROW_NUMBER() with PARTITION BY solves this in one pass; a plain GROUP BY
-- cannot, because it would collapse the products together.
SELECT
    category,
    product_name,
    ROUND(total_sales, 2) AS total_sales,
    rn AS rank_in_category
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
ORDER BY category, rank_in_category;

-- ANSWER: nine rows come back, three per category.  Furniture is led by the
-- HON 5400 task chairs ($21,870.58), Office Supplies by the Fellowes PB500
-- binding machine ($27,453.38) and Technology by the Canon copier
-- ($61,599.82).  ROW_NUMBER() with PARTITION BY is what makes "top 3 per
-- group" possible in a single pass.


-- ===========================================================================
-- Q9. What is the year-over-year sales growth?
-- ===========================================================================
-- LAG() reads the previous row (the previous year) in the same result set.
WITH yearly AS (
    SELECT
        YEAR(order_date) AS sales_year,
        SUM(sales)       AS total_sales,
        SUM(profit)      AS total_profit
    FROM superstore
    GROUP BY YEAR(order_date)
)
SELECT
    sales_year,
    ROUND(total_sales, 2)                                        AS total_sales,
    ROUND(total_profit, 2)                                       AS total_profit,
    ROUND(LAG(total_sales) OVER (ORDER BY sales_year), 2)         AS prev_year_sales,
    ROUND(
        100 * (total_sales - LAG(total_sales) OVER (ORDER BY sales_year))
        / NULLIF(LAG(total_sales) OVER (ORDER BY sales_year), 0), 2
    )                                                            AS yoy_growth_pct
FROM yearly
ORDER BY sales_year;

-- ANSWER: revenue is $484,247.50 in 2014, dips slightly to $470,532.51 in
-- 2015 (-2.83%), then grows +29.47% to $609,205.60 in 2016 and +20.36% to
-- $733,215.26 in 2017.  Profit, however, rises every single year
-- ($49,543.97 -> $61,618.60 -> $81,795.17 -> $93,439.27), so the business
-- improved its margins even through the flat 2015.


-- ===========================================================================
-- Q10. How loyal are customers - how many buy more than once?
-- ===========================================================================
-- Business value: repeat purchase rate is the cheapest growth lever there
-- is, so it is worth knowing how much of the base is one-and-done.
WITH order_counts AS (
    SELECT
        customer_id,
        COUNT(DISTINCT order_id) AS orders
    FROM superstore
    GROUP BY customer_id
)
SELECT
    CASE
        WHEN orders = 1  THEN 'One-time buyer'
        WHEN orders <= 3 THEN 'Occasional (2-3 orders)'
        WHEN orders <= 6 THEN 'Regular (4-6 orders)'
        ELSE 'Loyal (7+ orders)'
    END                          AS loyalty_segment,
    COUNT(*)                     AS customers,
    ROUND(100 * COUNT(*) / (SELECT COUNT(*) FROM order_counts), 2) AS pct_of_customers,
    SUM(orders)                  AS orders_placed
FROM order_counts
GROUP BY loyalty_segment
ORDER BY orders_placed DESC;

-- ANSWER: repeat purchasing is the norm, not the exception.  Only 12
-- customers (1.51%) ever bought once; 357 customers (45.02%) placed 7+ orders
-- and together account for 3,074 of the 5,009 orders.  A further 337 (42.50%)
-- are "Regular" at 4-6 orders.  So the revenue base rests on a large,
-- healthy loyal segment - the opportunity is the ~99 occasional/one-time
-- buyers who could be nudged up a tier.

-- ---------------------------------------------------------------------------
-- Bonus: a single reusable view that answers "who are my best customers?"
-- (defined in sql/05_views.sql) - handy for dashboards and the notebook.
-- ---------------------------------------------------------------------------
SELECT
    customer_name,
    segment,
    regions_ordered_in,
    total_orders,
    total_sales,
    total_profit
FROM vw_customer_summary
ORDER BY total_sales DESC
LIMIT 10;
