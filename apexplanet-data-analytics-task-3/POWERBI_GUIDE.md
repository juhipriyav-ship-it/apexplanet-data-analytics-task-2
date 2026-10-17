# Power BI Dashboard — Step-by-Step Build Guide

**Task 3 · Day 16–20 · ApexPlanet Data Analytics Internship**

The `.pbix` file has to be built by hand in Power BI Desktop because it is a
Windows GUI application. This guide is the exact click path, in order. Follow it
top to bottom and you will end up with the 6–8 visual executive dashboard the
brief asks for.

**Time needed:** about 45–60 minutes the first time.

---

## Before you start

| You need | Notes |
|---|---|
| Power BI Desktop (free) | Microsoft Store, or https://powerbi.microsoft.com/desktop/ |
| The cleaned dataset | `..\data\superstore_cleaned.csv` (i.e. `apexplanet-data-analytics\data\superstore_cleaned.csv`) |
| A Power BI account | Only needed for step 9 (publishing). A free account is fine. |
| The chart reference | `notebooks/Task3_Visualization.ipynb` and `reports/html/dashboard_preview.html` — open this first to see the target layout |

**Data facts you should see after loading:** 9,994 rows, 22 columns,
Jan 2014 – Dec 2017, total sales $2,297,200.86, total profit $286,397.02.

---

## Step 1 — Get the data

1. Open **Power BI Desktop**.
2. On the splash screen click **Get data**, or on the ribbon: **Home → Get data → Text/CSV**.
3. Browse to `apexplanet-data-analytics\data\superstore_cleaned.csv` and click **Open**.
4. In the preview window set **File Origin** to `65001: Unicode (UTF-8)`.
5. Click **Transform Data** (not *Load*) so we can fix types first.

### Step 1b — Fix the data types in Power Query

In the Power Query Editor, click the icon at the left of each column header:

| Column | Set type to |
|---|---|
| `Order Date` | Date |
| `Ship Date` | Date |
| `Sales` | Decimal Number |
| `Profit` | Decimal Number |
| `Discount` | Decimal Number |
| `Quantity` | Whole Number |
| `Postal Code` | Text *(not a number — leading zeros matter)* |
| everything else | Text |

Then **Home → Close & Apply**.

> The status bar should read **9,994 rows**. If it says something else, you
> loaded the wrong file.

---

## Step 2 — Add calculated columns (Power Query or DAX)

The brief asks for calculated columns, so add these two. In **Data view**
(the table icon on the left rail), right-click the `superstore_cleaned` table →
**New column**, and paste each one.

```dax
Order Year = YEAR(superstore_cleaned[Order Date])
```

```dax
Month Label = FORMAT(superstore_cleaned[Order Date], "MMM YYYY")
```

```dax
Profit per Unit = DIVIDE(superstore_cleaned[Profit], superstore_cleaned[Quantity])
```

**Optional but recommended — a proper date table** (needed for year-over-year):
**Home → New table**, then paste:

```dax
Date Table =
CALENDAR(DATE(2014,1,1), DATE(2017,12,31))
```

Select that new table, then **Table tools → Mark as date table → Date**. Finally
drag `Date Table[Date]` onto `superstore_cleaned[Order Date]` in **Model view**
(the third icon on the left rail) to create the relationship.

---

## Step 3 — Add the DAX measures

In **Data view**, right-click `superstore_cleaned` → **New measure**, and add
each of these one at a time.

### KPI measures

```dax
Total Sales = SUM(superstore_cleaned[Sales])
```

```dax
Total Profit = SUM(superstore_cleaned[Profit])
```

```dax
Profit Margin % = DIVIDE([Total Profit], [Total Sales])
```

```dax
Total Orders = DISTINCTCOUNT(superstore_cleaned[Order ID])
```

```dax
Total Customers = DISTINCTCOUNT(superstore_cleaned[Customer ID])
```

```dax
Total Products = DISTINCTCOUNT(superstore_cleaned[Product ID])
```

```dax
Average Order Value = DIVIDE([Total Sales], [Total Orders])
```

```dax
Average Discount = AVERAGE(superstore_cleaned[Discount])
```

### Growth measures (only if you did the date table in step 2)

```dax
Sales LY = CALCULATE([Total Sales], SAMEPERIODLASTYEAR('Date Table'[Date]))
```

```dax
Sales YoY % = DIVIDE([Total Sales] - [Sales LY], [Sales LY])
```

> `DIVIDE()` is used instead of `/` on purpose — it returns blank instead of an
> error when the denominator is zero.

---

## Step 4 — Build the KPI cards (4 visuals)

1. Click an empty area of the canvas.
2. In the **Visualizations** pane pick **Card** (the "123" icon).
3. Drag `Total Sales` from the Fields pane into the card.
4. Repeat to make three more cards: `Total Profit`, `Total Orders`, `Total Customers`.
5. Select all four cards (click one, then Ctrl-click the others) →
   **Format → General → Effects → Rounded corners**, and set a background colour.
6. Line them up across the top of the page.

Now select the `Total Sales` card → **Format → Callout value** → set
**Display units** to *Millions* / *Thousands* so long numbers stay readable.
Do the same for `Total Profit`.

---

## Step 5 — Sales trend (line chart)

1. Add a **Line chart** visual.
2. **X-axis:** `Order Date` (Power BI will auto-create a date hierarchy).
3. **Y-axis:** `Total Sales`.
4. Change the X-axis to month level: in the Visualizations pane, click the
   down-arrow next to `Order Date` and choose **Month**.
5. **Format → Lines → Markers → On**.

This should look like `reports/charts/01_monthly_sales_line.png`.

---

## Step 6 — Category breakdown (bar + donut)

**Bar chart**
1. Add a **Clustered bar chart**.
2. **Y-axis:** `Category`. **X-axis:** `Total Sales`.
3. Add `Total Profit` to **Tooltips**.

**Donut chart** (the brief also asks for a pie)
1. Add a **Donut chart**.
2. **Legend:** `Category`. **Values:** `Total Sales`.
3. **Format → Detail labels → Label contents → Category, percent of total**.

---

## Step 7 — Geographic map

1. Add a **Map** visual (the globe icon — *Map*, not *Filled map*).
2. Drag `State` into **Location**, `Sales` into **Bubble size**, and
   `Category` into **Legend**.
3. If Power BI does not auto-detect the country, expand **Format → Map
   settings** and set **Data category** for the `Country` field to *Country*.

> Only needed if the map refuses to place US states: in **Data view**, select
> `Country` → **Column tools → Data category → Country**. Then refresh the visual.

---

## Step 8 — Top 10 products / customers (matrix + bar)

**Matrix** (the brief asks for a matrix visual)
1. Add a **Matrix** visual.
2. **Rows:** `Category` then `Sub-Category`.
3. **Values:** `Total Sales`, `Total Profit`, `Profit Margin %`.
4. **Format → Row headers → Stepped layout → Off**.

**Top 10 products**
1. Add a **Clustered bar chart**.
2. **Y-axis:** `Product Name`. **X-axis:** `Total Sales`.
3. In the **Filters** pane drag `Product Name` into *Filters on this visual* →
     **Filter type: Top N** → **Show items: Top 10** → **By value: Total Sales**.
4. **Format → Bars → Colour** → set to your brand colour.

---

## Step 9 — Add the filter panel (slicers)

The brief explicitly asks for a filter panel with date, region and category.

1. Add a **Slicer** visual → drag `Order Date` in → **Format → Slicer settings
   → Style → Between**.
2. Add a second **Slicer** for `Region` (choose **Style → Dropdown**).
3. Add a third **Slicer** for `Category` (**Style → Tile** or *Horizontal*).
4. Group them: select all three → right-click → **Group**.
5. Move the group to a left-hand or right-hand column of the canvas.

**Making the slicers control everything:** click any slicer → **Format → Edit
interactions → Filter**. Then, for each other visual on the page, click the
**filter icon** that appears on it. Repeat for each slicer. *(Power BI filters
all visuals by default when you use the same field, so this is usually only
needed for the date slicer.)*

---

## Step 10 — Lay it out and brand it

Target layout (matches `dashboard_preview.html`):

```text
┌───────────────────────────────────────────────────────────────┐
│  TITLE:  Superstore Executive Dashboard        [logo/brand]   │
├──────────┬────────────────────────────────────────────────────┤
│          │  KPI    KPI    KPI    KPI                          │
│ FILTER   ├────────────────────────────────────────────────────┤
│ PANEL    │  Monthly sales trend (line)                        │
│ date     ├───────────────────────┬────────────────────────────┤
│ region   │  Sales by category    │  Category donut            │
│ category ├───────────────────────┼────────────────────────────┤
│          │  Top 10 products      │  Map by state              │
│          ├───────────────────────┴────────────────────────────┤
│          │  Category / Sub-category matrix                    │
└──────────┴────────────────────────────────────────────────────┘
```

1. **Insert → Text box** for the title.
2. **View → Themes** → pick a built-in theme, or import a JSON theme matching
   the ApexPlanet colours.
3. Align visuals: select several → **Format → Align**.
4. Give every visual a title (**Format → Title**).

> **Check it against the brief:** KPI cards ✅ · sales trend ✅ · category
> breakdown ✅ · geographic map ✅ · top 10 products/customers ✅ · filter panel ✅
> That is 6 visual types plus the matrix — inside the 6–8 target.

---

## Step 11 — Save the .pbix

**File → Save as** → navigate to
`apexplanet-data-analytics\apexplanet-data-analytics-task-3\dashboards\` and
save as:

```text
Task3_Dashboard.pbix
```

This file is the Task 3 dashboard deliverable. Commit it.

---

## Step 12 — Publish and get the shareable link

Required by the brief ("Publish to Power BI Service / Tableau Public",
"Get shareable link").

1. **Home → Publish**.
2. Choose **My workspace** → **Select**.
3. When it finishes, click **Open 'Task3_Dashboard' in Power BI**.
4. Back in the workspace list, hover over the report → **⋮ → File → Embed**,
   or open the report and copy the browser URL.
5. Make it shareable: **⋮ → Share** → *Anyone with the link* (or publish to web).

Paste that link into the README and the LinkedIn post.

---

## Optional — swap the dashboard file for Power BI Service

If you would rather avoid the desktop app entirely, Power BI Service
(app.powerbi.com) can import the same CSV and build the identical visuals in the
browser. The `.pbix` download is still available from there via
**File → Download this file**, so the deliverable is still satisfied.

---

## Troubleshooting

| Problem | Fix |
|---|---|
| Sales totals do not match $2,297,200.86 | `Sales` was imported as Text, not Decimal Number. Redo step 1b. |
| Row count is not 9,994 | You loaded `Sample - Superstore.csv` (the raw file) instead of `superstore_cleaned.csv`. |
| Map is blank | Set the `Country` column's **Data category** to *Country* (step 7). |
| Dates group by year only | In the visual, click the arrow on the date field and choose **Month** instead of the hierarchy. |
| `SAMEPERIODLASTYEAR` errors | You skipped the date table in step 2, or did not mark it as a date table. |
| Slicers do not affect a visual | **Format → Edit interactions** on the slicer, then enable *Filter* on that visual. |

---

## Ready-made reference values (to verify your build)

| KPI | Expected value |
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
