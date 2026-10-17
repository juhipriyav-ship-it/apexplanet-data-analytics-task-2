# Task 3 — Data Visualization & Dashboarding

**ApexPlanet Data Analytics Internship — Task 3 (7-day timeline)**

**Objective:** create professional dashboards and visualizations.

| Day | Activity | Status |
|---|---|---|
| 14–15 | Python visualization — Matplotlib, Seaborn, Plotly | ✅ Done |
| 16–18 | Power BI / Tableau basics — connect, charts, slicers, DAX | 📘 Guide ready — build by hand |
| 19–20 | Interactive dashboard + publish | 📘 Guide ready — build by hand |

---

## Deliverables

| From the brief | Delivered as | Status |
|---|---|---|
| Python visualizations (HTML/PNG) | `reports/charts/*.png` (7) + `reports/html/*.html` (5) | ✅ |
| Dashboard file (`.pbix` / `.twbx`) | `dashboards/Task3_Dashboard.pbix` | ⬜ Built by hand — see `POWERBI_GUIDE.md` |
| LinkedIn post | Text at the bottom of this file | ⬜ Post it |

> **Why the `.pbix` is not in this repo yet:** Power BI Desktop is a Windows GUI
> application with no command-line equivalent, so the file cannot be generated
> programmatically. Everything needed to build it in ~45 minutes is in
> [`POWERBI_GUIDE.md`](POWERBI_GUIDE.md) — click-by-click steps, the DAX
> measures to paste, the page layout, and a table of expected KPI values you can
> check your build against.

---

## Day 14–15: Python visualization

### Matplotlib — the four required chart types

| Chart | File | What it shows |
|---|---|---|
| Line | `reports/charts/01_monthly_sales_line.png` | Monthly sales trend, Jan 2014 – Dec 2017 |
| Bar | `reports/charts/02_sales_by_category_bar.png` | Total sales by category |
| Scatter | `reports/charts/03_discount_vs_profit_scatter.png` | Discount against profit, with break-even line |
| Histogram | `reports/charts/04_sales_distribution_histogram.png` | Distribution of sales per order line |

### Seaborn — advanced plots

| Plot | File | What it shows |
|---|---|---|
| Heatmap | `reports/charts/05_correlation_heatmap.png` | Correlation matrix of Sales / Quantity / Discount / Profit |
| Pairplot | `reports/charts/06_pairplot.png` | Every numeric pair, 2,000-row sample |
| Boxen | `reports/charts/07_profit_boxen_by_category.png` | Profit spread by category |

### Plotly — interactive, exported as HTML

| Chart | File |
|---|---|
| Line | `reports/html/interactive_01_monthly_sales.html` |
| Bar | `reports/html/interactive_02_sales_by_subcategory.html` |
| Treemap (sales sized, profit coloured) | `reports/html/interactive_03_treemap.html` |
| US map by state | `reports/html/interactive_04_sales_map.html` |
| Combined dashboard preview | `reports/html/dashboard_preview.html` |

Every Plotly chart is a **standalone HTML file** — open it in any browser, no
Python needed. All 49 US states mapped successfully.

> **Note:** Plotly PNG export is not used here because it requires the extra
> `kaleido` package. Matplotlib and Seaborn cover the PNG deliverable and Plotly
> covers the HTML deliverable, which is exactly what the brief asks for.

---

## Day 16–18: Power BI / Tableau basics

Follow [`POWERBI_GUIDE.md`](POWERBI_GUIDE.md). It covers:

- Installing Power BI Desktop and connecting to `..\data\superstore_cleaned.csv`
- Fixing data types in Power Query (the most common failure point)
- **Calculated columns:** `Order Year`, `Month Label`, `Profit per Unit`
- **DAX measures:** Total Sales, Total Profit, Profit Margin %, Total Orders,
  Total Customers, Total Products, Average Order Value, Average Discount, plus
  `Sales LY` and `Sales YoY %`
- Basic charts: bar, line, pie/donut, map, matrix
- Slicers and the filter panel, and how to make them interact with visuals

---

## Day 19–20: Interactive dashboard

Target layout (a Plotly preview is in `reports/html/dashboard_preview.html`):

```text
┌───────────────────────────────────────────────────────────────┐
│  TITLE:  Superstore Executive Dashboard                       │
├──────────┬────────────────────────────────────────────────────┤
│          │  KPI    KPI    KPI    KPI        ← total sales,    │
│ FILTER   │                                    profit, orders, │
│ PANEL    │                                    customers        │
│ date     ├────────────────────────────────────────────────────┤
│ region   │  Monthly sales trend (line chart)                  │
│ category ├───────────────────────┬────────────────────────────┤
│          │  Sales by category    │  Category donut            │
│          ├───────────────────────┼────────────────────────────┤
│          │  Top 10 products      │  Map by state              │
│          ├───────────────────────┴────────────────────────────┤
│          │  Category / Sub-category matrix                    │
└──────────┴────────────────────────────────────────────────────┘
```

That is 4 KPI cards + 1 line + 2 category visuals + 1 map + 1 top-N + 1 matrix +
3 slicers — covering all six required visual types inside the 6–8 target.

---

## How to reproduce the Python work

```bash
pip install -r requirements.txt
jupyter notebook notebooks/Task3_Visualization.ipynb
```

Or execute it headlessly:

```bash
jupyter nbconvert --to notebook --execute --inplace notebooks/Task3_Visualization.ipynb
```

> **Run it from the Task 3 folder**, not the repo root. If you open Jupyter from
> the repo root the notebook still works (paths are anchored off the data file),
> but running `python -m nbconvert` from the root previously failed because a
> stray `datetime.py` used to shadow Python's stdlib. Those practice files now
> live in `python-practice/`.

Executed status: **18 code cells, 0 errors**, 12 chart files produced.

---

## Verified KPIs (use these to check your Power BI build)

| KPI | Value |
|---|---|
| Total Sales | $2,297,200.86 |
| Total Profit | $286,397.02 |
| Profit Margin | 12.47% |
| Total Orders | 5,009 |
| Total Customers | 793 |
| Total Products | 1,862 |
| Average Order Value | $458.61 |
| Average Discount | 15.62% |
| Best category by profit | Technology — $145,454.95 |
| Best region by sales | West — $725,457.82 |
| Top product by sales | Canon imageCLASS 2200 Advanced Copier — $61,599.82 |
| Top customer by sales | Sean Miller — $25,043.05 |

---

## Key insights from the visualizations

1. **Sales are strongly seasonal.** November and December spike every year;
   Nov 2017 is the single best month at $118,447.83. Any forecast must account
   for this, not treat the series as a straight line.
2. **Revenue is evenly spread across the three categories** — Technology
   $836K, Furniture $742K, Office Supplies $719K — so no single category is
   carrying the business.
3. **Discount and profit are negatively correlated.** The scatter plot shows
   every heavily discounted order sitting below break-even, and the heatmap
   confirms discount is the only numeric column negatively related to profit.
4. **Sales are heavily right-skewed.** Most order lines are small; a few very
   large Technology orders pull the average up. The histogram is therefore
   clipped at the 99th percentile to stay readable.
5. **West and East dominate geographically**, together producing well over half
   of total sales, which is why a regional filter is one of the most useful
   slicers on the dashboard.

---

## Files in this task

```text
apexplanet-data-analytics-task-3/
├── notebooks/
│   └── Task3_Visualization.ipynb     # all Python visualization work (executed)
├── reports/
│   ├── charts/                       # 7 PNG charts (Matplotlib + Seaborn)
│   └── html/                         # 5 interactive Plotly HTML files
├── dashboards/
│   └── Task3_Dashboard.pbix          # ← you build this (see POWERBI_GUIDE.md)
├── POWERBI_GUIDE.md                   # click-by-click Power BI instructions
├── requirements.txt
└── readme.md
```

---

## LinkedIn post

> Task 3 complete! Built an interactive Power BI dashboard on the Superstore
> dataset showing **$2.30M sales, $286K profit, 5,009 orders and 793 customers**
> — with a monthly sales trend, category breakdown, geographic map, top 10
> products and a date/region/category filter panel. Also created the full Python
> visualization layer (Matplotlib, Seaborn, Plotly). Check out the link in the
> comments. #PowerBI #DataVisualization #DataAnalytics

Keep the original wording from the brief if you prefer:
*"Task 3 complete! Built interactive dashboard showing [key metrics]. Check out
the link in comments. #PowerBI #DataVisualization"*
