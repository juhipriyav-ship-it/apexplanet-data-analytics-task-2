# Task 2 — SQL for Data Extraction

**ApexPlanet Data Analytics Internship — Task 2 (7-day timeline)**

**Objective:** master SQL queries for data extraction and analysis by loading the
Task 1 cleaned dataset into a real relational database, querying it from
beginner to advanced level, and finally driving it from Python with SQLAlchemy
and `pandas.read_sql()`.

The original task slide is kept at [`task-image.png`](task-image.png).

---

## Table of contents

- [What was built](#what-was-built)
- [Dataset](#dataset)
- [Requirements](#requirements)
- [Quick start (reproduce in 3 commands)](#quick-start-reproduce-in-3-commands)
- [Database design](#database-design)
- [The SQL files, by learning day](#the-sql-files-by-learning-day)
- [The 10 business questions](#the-10-business-questions)
- [Key insights](#key-insights)
- [Python + SQL integration](#python--sql-integration)
- [Project structure](#project-structure)
- [LinkedIn post](#linkedin-post)
- [Troubleshooting](#troubleshooting)

---

## What was built

| Requirement from the brief | Delivered as |
|---|---|
| Install SQLite / PostgreSQL (or SQLite online) | MySQL 8.0 (local instance), chosen because it was already available |
| Import cleaned dataset into database | `scripts/db_utils.py --load` loads `data/superstore_cleaned.csv` into the `superstore` table |
| Practice `SELECT`, `WHERE`, `ORDER BY`, `LIMIT`, `GROUP BY`, `HAVING`, `JOIN` | [`sql/02_basic_queries.sql`](sql/02_basic_queries.sql) — 27 labelled examples |
| Subqueries and CTEs (`WITH`) | [`sql/03_advanced_queries.sql`](sql/03_advanced_queries.sql) — sections 1 and 2 |
| Window functions (`ROW_NUMBER`, `RANK`, `LAG`, `LEAD`) | [`sql/03_advanced_queries.sql`](sql/03_advanced_queries.sql) — section 3 (plus `DENSE_RANK`, `NTILE`, running totals, moving averages) |
| Views for reusable queries | [`sql/05_views.sql`](sql/05_views.sql) — 5 views |
| Connect Python to the database using SQLAlchemy | [`scripts/db_utils.py`](scripts/db_utils.py) |
| Execute SQL from Jupyter with `pandas.read_sql()` | [`notebooks/Task2_SQL_Integration.ipynb`](notebooks/Task2_SQL_Integration.ipynb) |
| Build 10 business questions and answer them with SQL | [`sql/04_business_questions.sql`](sql/04_business_questions.sql) |
| Create a reusable database utility script | [`scripts/db_utils.py`](scripts/db_utils.py) |
| GitHub: SQL query files + Python DB integration notebook | This repository |

Every SQL statement in this repository was executed against MySQL 8.0.46 and
verified to run — the notebook executes end to end with **0 cell errors**.

---

## Dataset

The **cleaned Sample Superstore** dataset produced in Task 1
(`../data/superstore_cleaned.csv`).

| Metric | Value |
|---|---|
| Line items (rows) | 9,994 |
| Distinct orders | 5,009 |
| Distinct customers | 793 |
| Distinct products | 1,862 |
| Sub-categories | 17 |
| Date range | 2014-01-03 → 2017-12-30 (48 months) |
| Total sales | $2,297,200.86 |
| Total profit | $286,397.02 (12.47% margin) |

Columns: `row_id, order_id, order_date, ship_date, ship_mode, customer_id,
customer_name, segment, country, city, state, postal_code, region, product_id,
category, sub_category, product_name, sales, quantity, discount, profit, month`.

---

## Requirements

- Python 3.10+
- A running MySQL 8.0+ server

Python packages (`requirements.txt`):

```
pandas, SQLAlchemy, mysql-connector-python, jupyter, ipykernel
```

```bash
pip install -r requirements.txt
```

---

## Quick start (reproduce in 3 commands)

**1. Create your credentials file.** `.env` is gitignored, so copy the template
and fill in your password:

```bash
cp .env.example .env      # Windows: copy .env.example .env
```

```ini
MYSQL_HOST=127.0.0.1
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=your_password_here
MYSQL_DATABASE=apexplanet
```

**2. Create the database, apply the schema and load the data** (one command):

```bash
python scripts/db_utils.py --load
```

```text
[ok] database ready: apexplanet
[ok] applied 01_schema.sql
[ok] applied 05_views.sql
[ok] cleared existing rows from superstore
[ok] loaded 9,994 rows into superstore
```

Re-running `--load` is safe: the table is cleared first, so the row count never
doubles.

**3. Explore.**

```bash
# run an ad-hoc query
python scripts/db_utils.py --query "SELECT category, ROUND(SUM(sales),2) AS sales FROM superstore GROUP BY category"

# list tables and views with row counts
python scripts/db_utils.py --tables

# open the integration notebook
jupyter notebook notebooks/Task2_SQL_Integration.ipynb
```

You can also paste any statement from the `sql/` files straight into MySQL
Workbench or the `mysql` CLI.

---

## Database design

One fact table, deliberately denormalised to match the cleaned CSV, with
indexes on the columns the queries filter and group by.

| Column | Type | Notes |
|---|---|---|
| `row_id` | `INT` | primary key |
| `order_id` | `VARCHAR(20)` | indexed grouping key |
| `order_date`, `ship_date` | `DATE` | real dates, not text |
| `sales`, `profit` | `DECIMAL(12,4)` | money; 4 dp preserves the source values |
| `discount` | `DECIMAL(5,2)` | fraction, e.g. `0.20` = 20% |
| `month` | `VARCHAR(7)` | precomputed `YYYY-MM` from Task 1 |
| … | | `customer_*`, `product_*`, `category`, `region`, `segment`, etc. |

Indexes: `order_date`, `customer_id`, `product_id`, `(category, sub_category)`,
`region`, `month`.

### Views (`sql/05_views.sql`)

| View | Grain | Purpose |
|---|---|---|
| `vw_monthly_sales` | 1 row / month | trend, orders, AOV |
| `vw_customer_summary` | 1 row / customer | lifetime spend, order count |
| `vw_product_performance` | 1 row / product | product revenue and profit |
| `vw_category_performance` | 1 row / sub-category | sales, profit, margin % |
| `vw_region_performance` | 1 row / region | regional sales, profit, margin |

> **Why `vw_customer_summary` does not include region:** 766 of the 793
> customers ordered from more than one region. Grouping by region would split a
> single customer across several rows and silently under-count their orders —
> so region is treated as an order-level attribute and the view exposes
> `regions_ordered_in` instead.

---

## The SQL files, by learning day

### Day 7–8 — `sql/02_basic_queries.sql` (SQL fundamentals)

- `SELECT` — projections, aliases, computed columns
- `WHERE` — `AND`/`OR`, `IN`, `BETWEEN`, `LIKE`, `IS NULL`
- `ORDER BY` / `LIMIT` / `OFFSET` — sorting and top-N with paging
- `DISTINCT` — unique values and unique combinations
- `GROUP BY` — aggregates (`SUM`, `AVG`, `COUNT`, `MIN`, `MAX`), multi-column grouping, date grouping
- `HAVING` — filtering aggregated groups, and `WHERE` + `HAVING` together
- `JOIN` — `INNER JOIN` to derived tables and views, `LEFT JOIN`, and a self-join

### Day 9–10 — `sql/03_advanced_queries.sql` (advanced SQL)

- **Subqueries** — scalar, in the `SELECT` list, derived tables, correlated, and `EXISTS`
- **CTEs** — single `WITH`, chained CTEs, a CTE referenced twice, `WITH RECURSIVE`
- **Window functions** — `ROW_NUMBER`, `RANK` vs `DENSE_RANK`, `PARTITION BY`, `LAG`/`LEAD`, running totals (`SUM() OVER`), moving average (`ROWS BETWEEN`), `NTILE`, `% of total`
- **Views** — querying, filtering, ranking on top of a view

### Day 11–13 — `sql/04_business_questions.sql` (business questions)

Ten questions, each followed by its interpretation as a SQL comment. See below.

---

## The 10 business questions

| # | Question | Answer |
|---|---|---|
| 1 | Top 5 products by sales | Canon imageCLASS 2200 Advanced Copier leads at **$61,599.82** (~2.2x the runner-up); Technology equipment dominates |
| 2 | Monthly sales trend | Seasonal, not a smooth ramp: lowest Jan 2014 (**$14,236.90**), peak Nov 2017 (**$118,447.83**). September and Q4 are the strongest periods |
| 3 | Customer segmentation by spend | 117 customers (**14.8%**) are High Value and generate **39.70%** of sales; the 353 Low Value customers generate only **15.81%**. High Value customers spend **7.6x** more per head |
| 4 | Top 10 customers by sales | The No. 1 customer by sales (Sean Miller, $25,043.05) is **unprofitable** at **-$1,980.74**. Margins across the top 10 span -7.9% to +47.1% |
| 5 | Category / sub-category performance | Technology is most profitable (**$145,454.95**, 17.40% margin). Furniture turns $741,999.80 of sales into only **$18,451.27** (2.49%) because Tables, Bookcases and Supplies lose money |
| 6 | Region performance | West is 1st ($725,457.82, 14.94% margin); East 2nd. Central is 3rd on sales but has the **weakest margin (7.92%)** |
| 7 | Impact of discount on profit | Clear cliff: 29.51% margin at 0% discount, negative from the **21–30%** band, and **-77.40%** at 41%+ (that band alone loses $99,558.59) |
| 8 | Top 3 products per category | Solved in one pass with `ROW_NUMBER() OVER (PARTITION BY category ...)` |
| 9 | Year-over-year growth | **-2.83%** (2015), **+29.47%** (2016), **+20.36%** (2017). Profit rose every single year |
| 10 | Customer loyalty | Repeat purchase is the norm: **45.02%** of customers placed 7+ orders (3,074 of 5,009 orders); only 12 customers (1.51%) ever bought once |

---

## Key insights

1. **Discounting past ~20% destroys profit.** Lines at 0% discount earn a
   29.51% margin; the 41%+ band loses 77.40%. This is the single biggest
   profit leak in the dataset.
2. **Furniture is the margin problem, not Office Supplies or Technology.**
   Tables (-$17,725.48), Bookcases (-$3,472.56) and Supplies (-$1,189.10) are
   the only loss-making sub-categories.
3. **Central region has a pricing problem.** It is 3rd by sales but last by
   margin (7.92%), while the smaller South region earns 11.93%.
4. **A small customer group carries the revenue.** ~15% of customers produce
   ~40% of sales, and the same customers place most of the orders — so
   retention spending is well targeted.
5. **Revenue must always be read next to profit.** The biggest-spending
   customer is a net loss, which a sales-only dashboard would never reveal.
6. **Growth is real but decelerating.** +29.47% → +20.36%, with profit
   improving each year — the business is getting more efficient, not just
   bigger.

---

## Python + SQL integration

`scripts/db_utils.py` is the reusable utility script required by the brief. It
is a single module used by the CLI *and* the notebook, so there is exactly one
place where connection settings, engine creation and loading logic live.

| Function | Purpose |
|---|---|
| `get_settings()` | read connection details from `.env` / environment |
| `get_engine()` | cached SQLAlchemy engine (`mysql+mysqlconnector://…`) |
| `run_query(sql, params)` | run a `SELECT`, return a DataFrame |
| `execute(sql, params)` | run DDL/DML in a transaction |
| `build_database()` | create the database and apply the `.sql` schema/views |
| `load_csv_to_mysql()` | load the cleaned CSV (idempotent — truncates first) |
| `list_tables()` / `row_count()` | introspection helpers |

The notebook demonstrates the two ways SQL is consumed from Python:

```python
from db_utils import get_engine, run_query
from sqlalchemy import text

# 1. plain SQL string
df = pd.read_sql("SELECT category, SUM(sales) FROM superstore GROUP BY category", get_engine())

# 2. bound parameters (the safe way to inject values - never f-strings)
stmt = text("SELECT * FROM superstore WHERE region = :region AND sales > :min_sales")
df = pd.read_sql(stmt, get_engine(), params={"region": "West", "min_sales": 4000})
```

Notebook highlights: connection check, database inventory, `read_sql()` basics,
parameterised queries, all 10 business questions, view reuse, a matplotlib
chart of the monthly trend, and a CSV export.

---

## Project structure

```text
apexplanet-data-analytics-task-2/
├── sql/
│   ├── 01_schema.sql               # table definition + indexes
│   ├── 02_basic_queries.sql        # Day 7-8  fundamentals
│   ├── 03_advanced_queries.sql     # Day 9-10  subqueries, CTEs, window functions
│   ├── 04_business_questions.sql   # Day 11-13 the 10 business questions
│   └── 05_views.sql                # reusable views
├── scripts/
│   └── db_utils.py                 # reusable DB utility script (CLI + library)
├── notebooks/
│   └── Task2_SQL_Integration.ipynb # Python + SQL integration (executed)
├── reports/
│   ├── task2_top_100_customers.csv # exported query result
│   └── charts/
│       └── task2_monthly_sales_trend.png
├── task-image.png                  # the original task brief
├── requirements.txt
├── .env.example                    # template (real .env is gitignored)
└── readme.md
```

The `.git` metadata is local to this folder; `data/superstore_cleaned.csv` is
read from the parent Task 1 folder (`../data/`).

---

## LinkedIn post

> Task 2 done! Mastered SQL queries for business insights. Integrated Python
> with SQLite for automated data extraction. #SQL #DataAnalytics

Adapted for this build (MySQL + SQLAlchemy):

> Task 2 done! Mastered SQL queries for business insights — from `SELECT` and
> `JOIN`s to CTEs and window functions (`ROW_NUMBER`, `RANK`, `LAG`). Loaded the
> cleaned Superstore dataset into MySQL, answered 10 real business questions
> (top products, monthly trends, customer segmentation, discount impact…) and
> integrated Python with SQLAlchemy + `pandas.read_sql()` for automated data
> extraction. Biggest finding: discounting past 20% turns profit negative.
> #SQL #DataAnalytics #Python

---

## Troubleshooting

| Symptom | Fix |
|---|---|
| `Access denied for user 'root'@'localhost'` | the password in `.env` is wrong; check `MYSQL_PASSWORD` |
| `Can't connect to MySQL server on '127.0.0.1'` | the MySQL service is not running: `Get-Service MySQL80` / `Start-Service MySQL80` |
| `Can't connect ... (10061)` | wrong port; confirm with `Get-NetTCPConnection -State Listen \| Where-Object LocalPort -eq 3306` |
| `No module named 'mysql.connector'` | `pip install -r requirements.txt` |
| `Cleaned dataset not found at …` | this repo expects the Task 1 `data/superstore_cleaned.csv` next to it, or pass an explicit `csv_path` |
| Notebook can't find the project root | run Jupyter from the project folder, or edit `find_project_root()` |
| Row count doubled | you loaded an older version; the current loader truncates first, so re-run `python scripts/db_utils.py --load` |

---

## Tools used

Python 3.14 · MySQL 8.0.46 · SQLAlchemy 2.0 · pandas · mysql-connector-python ·
Jupyter / nbformat / nbconvert · matplotlib
