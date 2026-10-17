-- ===========================================================================
-- 01_schema.sql
-- ApexPlanet Data Analytics - Task 2
-- Creates the `superstore` table that holds the cleaned Task 1 dataset.
-- Run with:  python scripts/db_utils.py --load
-- ===========================================================================

CREATE TABLE IF NOT EXISTS superstore (
    row_id        INT           NOT NULL,
    order_id      VARCHAR(20)   NOT NULL,
    order_date    DATE          NOT NULL,
    ship_date     DATE          NOT NULL,
    ship_mode     VARCHAR(30),
    customer_id   VARCHAR(20),
    customer_name VARCHAR(60),
    segment       VARCHAR(20),
    country       VARCHAR(40),
    city          VARCHAR(60),
    state         VARCHAR(40),
    postal_code   VARCHAR(10),
    region        VARCHAR(20),
    product_id    VARCHAR(30),
    category      VARCHAR(30),
    sub_category  VARCHAR(30),
    product_name  VARCHAR(255),
    sales         DECIMAL(12,4) NOT NULL DEFAULT 0,
    quantity      INT           NOT NULL DEFAULT 0,
    discount      DECIMAL(5,2)  NOT NULL DEFAULT 0,
    profit        DECIMAL(12,4) NOT NULL DEFAULT 0,
    month         VARCHAR(7),
    PRIMARY KEY (row_id),
    KEY idx_order_date (order_date),
    KEY idx_customer  (customer_id),
    KEY idx_product   (product_id),
    KEY idx_category  (category, sub_category),
    KEY idx_region    (region),
    KEY idx_month     (month)
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4
  COLLATE = utf8mb4_unicode_ci;
