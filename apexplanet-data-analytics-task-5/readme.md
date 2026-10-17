# Task 5 - Final Report, Automation & Presentation

**ApexPlanet Data Analytics Internship - Task 5**

## Objective

Close out the internship by turning the analysis from Tasks 1-4 into something
that runs on its own and can be presented to a non-technical audience:

1. A single automated pipeline that loads, cleans and summarises the Superstore
   dataset, exports the KPIs to Excel, and writes a run log.
2. A crisp, two-page executive PDF report generated programmatically with
   PyMuPDF - no manual editing.
3. A one-click Windows runner (`run_pipeline.bat`) plus instructions for
   scheduling it, so the whole thing is repeatable.

Everything is deliberately simple and dependency-light: one pipeline script,
one report builder, one batch file.

## Status by day

| Day | Milestone | Status |
|-----|-----------|--------|
| Day 27 | Final report (writing and presentation of findings) | Done ✅ |
| Day 28-29 | Automation (pipeline + report generation) | Done ✅ |
| Day 30 | Final submission (repo tag, links, LinkedIn post) | Pending |

## File tree

```
apexplanet-data-analytics-task-5/
|-- scripts/
|   |-- automate_pipeline.py     # load -> clean -> KPIs -> Excel -> summary
|   `-- build_report.py          # builds the 2-page PDF with PyMuPDF
|-- reports/
|   |-- Task5_Final_Report.pdf   # generated: 2-page executive report
|   |-- kpis.xlsx                # generated: 7-sheet KPI workbook
|   |-- pipeline_summary.txt     # generated: timestamped run log
|   `-- superstore_cleaned_pipeline.csv  # generated: cleaned data
|-- run_pipeline.bat             # one-click Windows runner (+ schtasks notes)
|-- requirements.txt
`-- readme.md
```

The dataset lives outside this folder at `../data/superstore_cleaned.csv`; the
pipeline locates it automatically by walking up from the script location, so it
works from any working directory.

## How to run

### 1. Install dependencies

```
pip install -r requirements.txt
```

### 2. Run the pipeline directly

```
python scripts/automate_pipeline.py
```

Useful flags (both optional and simple):

```
python scripts/automate_pipeline.py --quiet        # only print the summary block
python scripts/automate_pipeline.py --excel-only   # skip the .txt log
```

### 3. Rebuild the PDF report

```
python scripts/build_report.py
```

### 4. One-click (double-clickable) runner

Double-click `run_pipeline.bat`, or run it from a terminal. It `cd`s to its own
folder via `%~dp0`, runs the pipeline, then the report, and returns a non-zero
exit code if any step fails.

### 5. Schedule it with Windows Task Scheduler

Run one of these from an elevated Command Prompt:

```
schtasks /Create /TN "ApexPlanet_Task5_Pipeline" /TR "\"%~dp0run_pipeline.bat\"" /SC DAILY /ST 07:00 /F
schtasks /Create /TN "ApexPlanet_Task5_Pipeline" /TR "\"%~dp0run_pipeline.bat\"" /SC WEEKLY /D MON /ST 07:00 /F
```

Manage the task afterwards:

```
schtasks /Run    /TN "ApexPlanet_Task5_Pipeline"
schtasks /Delete /TN "ApexPlanet_Task5_Pipeline" /F
```

## What the pipeline outputs

| Output | Description |
|--------|-------------|
| `reports/superstore_cleaned_pipeline.csv` | Cleaned dataset (de-duplicated, trimmed, numeric-coerced, impossible rows removed) |
| `reports/kpis.xlsx` | 7 sheets: KPIs, Sales_by_Category, Sales_by_Region, Monthly_Sales, Top10_Products, Top10_Customers, Customer_Segments |
| `reports/pipeline_summary.txt` | Timestamped run log: rows in/out, KPI values, output file list |
| `reports/Task5_Final_Report.pdf` | 2-page executive report built by `scripts/build_report.py` |

## KPI table

| KPI | Value |
|-----|-------|
| Total Sales | $2,297,200.86 |
| Total Profit | $286,397.02 |
| Profit Margin | 12.47% |
| Orders | 5,009 |
| Customers | 793 |
| Products | 1,862 |
| Average Order Value | $458.61 |
| Average Discount | 15.62% |

## Top 5 insights

1. **Seasonality is strong.** Sales peak every November and December; November
   2017 hit $118,447.83 and the seasonal strength score is 0.805 (trend strength
   0.279).
2. **Discounting destroys margin.** Profit turns negative above a 20% discount;
   at 41%+ the margin is -77.40%, losing $99,558.59 in total. Discounted lines
   average -$6.66 profit versus +$66.90 at full price (p ~ 4.4e-55).
3. **Technology is the profit engine.** Technology delivered $145,454.95 of
   profit, while Furniture's $741,999.80 of sales produced only $18,451.27.
4. **Customer value is concentrated.** 264 Champions (33.3% of customers) spend
   $5,024.46 each versus $1,645.11 for Discount seekers; even the top spender,
   Sean Miller, is unprofitable at -$1,980.74.
5. **Growth and margin live in different regions.** The West is the largest
   region by sales ($725,457.82) while the Central region is the weakest on
   margin at just 7.92%.

## Business recommendations

1. **Cap routine discounts / reprice the 21%+ bands.** Reserve deep discounts
   for genuine clearance only - every point past 20% erodes margin directly.
2. **Plan stock, staffing and targets around the Nov/Dec peak** rather than a
   flat monthly run-rate. This also improves forecast quality (the 3-month
   moving-average backtest MAPE is 50.58%).
3. **Run segment-specific plays.** Loyalty rewards for Champions, cross-sell for
   the Steady core (34.4% of customers), bundle pricing instead of percentage-off
   for Discount seekers, and one low-cost reactivation email for the 88 Dormant
   customers.

## Scheduling with GitHub Actions

You can run the same pipeline on every push and on a weekly schedule. Create
`.github/workflows/pipeline.yml` in the repository (this file is managed
elsewhere and is **not** created by this task) with content like:

```yaml
name: Superstore Pipeline

on:
  push:
    branches: [ main ]
  schedule:
    - cron: "0 6 * * 1"   # every Monday at 06:00 UTC

jobs:
  pipeline:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - name: Install dependencies
        run: pip install -r apexplanet-data-analytics-task-5/requirements.txt
      - name: Run pipeline
        working-directory: apexplanet-data-analytics-task-5
        run: python scripts/automate_pipeline.py
      - name: Build report
        working-directory: apexplanet-data-analytics-task-5
        run: python scripts/build_report.py
      - name: Upload outputs
        uses: actions/upload-artifact@v4
        with:
          name: task5-outputs
          path: apexplanet-data-analytics-task-5/reports/
```

## Final submission checklist

- [ ] Repository is clean (no stray temp files, no large binaries beyond the
      generated reports).
- [ ] `requirements.txt` present and installable.
- [ ] Tag the release: `git tag -a v1.0.0 -m "ApexPlanet internship - Task 5 complete"` then `git push origin v1.0.0`.
- [ ] PDF report and Excel KPIs regenerated on the final data.
- [ ] GitHub repository link added to the submission.
- [ ] LinkedIn post published (see below) with the GitHub link.

---

## Ready-to-post LinkedIn update

> I have just wrapped up my Data Analytics internship with **ApexPlanet** and it
> has been a genuinely practical learning experience. Over the programme I
> completed 5 tasks that took me from raw data to a repeatable, automated
> workflow.
>
> I started with exploratory data analysis in Python (pandas, NumPy, Matplotlib,
> Seaborn), then wrote SQL queries on MySQL, and built interactive dashboards in
> Power BI and Plotly. From there I moved into the statistical side: hypothesis
> testing, confidence intervals, time-series analysis and decomposition, K-Means
> customer segmentation, and a linear regression model to explain sales. Finally,
> I tied everything together into an automated end-to-end pipeline that cleans
> the data, exports KPIs to Excel, and generates a two-page executive PDF report
> on demand.
>
> The biggest takeaway for me: the analysis only becomes valuable once it is
> automated, documented and easy for someone else to run.
>
> A big thank you to the team at ApexPlanet for the structure, the feedback and
> the real-world datasets. On to the next one.
>
> #DataAnalytics #Python #SQL #PowerBI #MachineLearning
