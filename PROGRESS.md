# ApexPlanet Data Analytics Internship — Progress Tracker

**Repo:** `apexplanet-data-analytics` (single repo, all tasks)
**Remote:** https://github.com/juhipriyav-ship-it/apexplanet-data-analytics-task-2.git
**Dataset:** Sample Superstore (cleaned in Task 1) — `data/superstore_cleaned.csv`

---

## Task status

| Task | Days | Focus | Status |
|---|---|---|---|
| Task 1 | 1–6 | Foundation & Exploratory Data Analysis | ✅ Done (user confirmed — left untouched) |
| Task 2 | 7–13 | SQL for Data Extraction | ✅ Done (built & verified) |
| Task 3 | 14–20 | Data Visualization & Dashboarding | 🔄 In progress |
| Task 4 | 21–26 | Advanced Analytics (Basic) | ⬜ Not started |
| Task 5 | 27–30 | Final Report, Automation & Presentation | ⬜ Not started |

Legend: ✅ done · 🔄 in progress · ⬜ not started · ⛔ blocked

---

## Task 3 — Data Visualization & Dashboarding

### Day 14–15: Python visualization
- [x] Matplotlib: line, bar, scatter, histogram
- [x] Seaborn: heatmap, pairplot, boxen plot
- [x] Plotly: interactive charts
- [x] Export plots as PNG / HTML

### Day 16–18: Power BI / Tableau basics
- [x] Power BI Desktop guidance (click-by-click) — `POWERBI_GUIDE.md`
- [x] Data type + model guidance
- [x] Basic charts: bar, line, pie, map, matrix (documented)
- [x] Slicers and filters (documented)
- [x] Calculated columns + DAX measures (documented)
- [ ] ⬜ **USER:** actually build `dashboards/Task3_Dashboard.pbix`

### Day 19–20: Interactive dashboard
- [x] Executive dashboard layout, 6–8 visuals (specified)
- [x] KPI cards (sales, customers, orders) — verified values supplied
- [x] Sales trend (line)
- [x] Category breakdown (bar/donut)
- [x] Geographic map (49 states, 0 unmapped)
- [x] Top 10 products / customers
- [x] Filter panel (date, region, category)
- [ ] ⬜ **USER:** publish to Power BI Service + get shareable link

### Deliverables
- [x] GitHub: Python visualizations (12 files — 7 PNG + 5 HTML)
- [ ] ⬜ **USER:** dashboard file `.pbix`
- [ ] ⬜ **USER:** LinkedIn post

> Python half verified: **18 code cells, 0 errors**, notebook executed in place.

---

## Task 4 — Advanced Analytics (Basic)

### Day 21–22: Statistical analysis
- [x] Descriptive stats (mean, median, mode, std dev, skewness)
- [x] Hypothesis testing (`scipy.stats`): t-test, chi-square
- [x] Confidence intervals
- [x] Document statistical findings with business implications

### Day 23–24: Time series analysis
- [x] Convert to time series format
- [x] Resample (daily / weekly / monthly)
- [x] Decompose: trend, seasonality, residuals
- [x] Simple moving average forecast

### Day 23–26: Customer segmentation (clustering)
- [x] Feature scaling (`StandardScaler`)
- [x] K-Means clustering
- [x] Optimal K via elbow method
- [x] PCA 2-D cluster plot
- [x] Profile each segment with recommendations

### Day 25–26: Basic predictive model
- [x] Define target variable
- [x] Train/test split (80/20)
- [x] Linear Regression
- [x] Evaluate: R², MAE, RMSE
- [x] Identify top 3 important features

### Deliverables
- [x] GitHub: notebook with stats tests + clustering + prediction model
- [ ] ⬜ **USER:** LinkedIn post

### Verified results

| Test | Result |
|---|---|
| t-test (discount vs profit) | −$6.66 vs +$66.90 per line · p = 4.4 × 10⁻⁵⁵ · d = −0.32 |
| Chi-square (segment × category) | p = 0.833 · V = 0.009 · **independent** |
| Time series | trend 0.279 · **seasonal 0.805** · MAE $18,002.43 · MAPE 50.58% |
| K-Means (k=4) | Champions 33.3% / Steady core 34.4% / Discount seekers 21.2% / Dormant 11.1% |
| Linear Regression | R² 0.186 · MAE $226.31 · RMSE $693.33 |

> **Verified:** 33 code cells, **0 errors**, 12 charts + `customer_segments.csv` exported.

---

## Task 5 — Final Report, Automation & Presentation

### Day 27: Executive summary report
- [ ] 2-page PDF report
- [ ] Executive summary (key findings)
- [ ] Dashboard screenshot
- [ ] Top 5 insights with visuals
- [ ] 3 business recommendations

### Day 28–29: Automate pipeline (simple)
- [ ] Script: load → clean → save → KPIs → export Excel
- [ ] Schedule via GitHub Actions or Windows Task Scheduler

### Day 30: Final submission
- [ ] Clean repository
- [ ] `requirements.txt`
- [ ] Final commit + tag `v1.0.0`
- [ ] Submit: LinkedIn link + GitHub link

### Deliverables
- [ ] GitHub: final code + automation script + README + requirements.txt + report PDF
- [ ] LinkedIn post (final submission)

---

## Environment

| Package | Version | Used by |
|---|---|---|
| pandas | 3.0.5 | all |
| numpy | — | all |
| matplotlib | 3.11.1 | Task 1, 3 |
| seaborn | 0.13.2 | Task 1, 3 |
| plotly | 6.9.0 | Task 3 |
| SQLAlchemy | 2.0.52 | Task 2 |
| mysql-connector-python | 26.7.0 | Task 2 |
| scipy | 1.18.1 | Task 4 |
| scikit-learn | 1.9.1 | Task 4 |
| statsmodels | 0.15.0 | Task 4 |
| openpyxl | 3.1.5 | Task 5 |
| pymupdf | 1.28.2 | Task 5 (PDF report) |
| jupyter / nbformat / nbconvert | 5.11.0 / 7.17.1 | all |

**MySQL:** 8.0.46, database `apexplanet`, table `superstore` (9,994 rows) — Task 2.
