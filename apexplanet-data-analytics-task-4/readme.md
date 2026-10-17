# Task 4 — Advanced Analytics (Basic)

**ApexPlanet Data Analytics Internship — Task 4 (6-day timeline, Day 21–26)**

**Objective:** apply statistical analysis and basic predictive modeling.

| Day | Activity | Status |
|---|---|---|
| 21–22 | Statistical analysis — descriptive stats, hypothesis testing, confidence intervals | ✅ Done |
| 23–24 | Time series analysis — resampling, decomposition, moving-average forecast | ✅ Done |
| 23–24 | Customer segmentation with K-Means + PCA | ✅ Done (see note on day numbering) |
| 25–26 | Basic predictive model — Linear Regression | ✅ Done |

> **Note on the brief's day numbering:** the task slide lists "23–24" twice
> (once for Time Series, once for Customer Segmentation) while the Task 4
> timeline is only 6 days (Day 21–26). All four activities have therefore been
> completed, in a sensible order, rather than one being dropped.

---

## Deliverables

| From the brief | Delivered as | Status |
|---|---|---|
| Notebook with statistical tests | `notebooks/Task4_Advanced_Analytics.ipynb` — Part 1 | ✅ |
| Clustering (K-Means) | Same notebook — Part 3, plus `reports/customer_segments.csv` | ✅ |
| Prediction model | Same notebook — Part 4 | ✅ |
| LinkedIn post | Text at the bottom of this file | ⬜ Post it |

Notebook executed in place: **33 code cells, 0 errors**, 12 charts exported,
1 CSV exported.

---

## Part 1 — Statistical Analysis (Day 21–22)

### Descriptive statistics

| Measure | Sales | Quantity | Discount | Profit |
|---|---|---|---|---|
| Mean | 229.86 | 3.79 | 0.156 | 28.66 |
| Median | 54.49 | 3.00 | 0.20 | 8.67 |
| Skewness | very high positive | near symmetric | left-skewed | high positive |
| Minimum | 0.44 | 1 | 0.00 | −6,599.98 |
| Maximum | 22,638.48 | 14 | 0.80 | 8,399.98 |

Sales and Profit are right-skewed, and Profit goes **negative** — loss-making
orders exist. Discount is 0 for the largest single group of lines, with a long
heavily-discounted tail up to 80%.

Chart: `reports/charts/01_distributions.png`

### Hypothesis test 1 — independent samples t-test (Welch)

**Question:** does discounting reduce profit per order line?

| | Value |
|---|---|
| Discounted lines | 5,196 · mean profit **−$6.66** |
| Full-price lines | 4,798 · mean profit **+$66.90** |
| t statistic | −15.738 |
| p value | 4.357 × 10⁻⁵⁵ |
| Decision (α = 0.05) | **Reject H₀** — the difference is real |
| Cohen's d | −0.32 (small standardised effect) |

**Interpretation.** The means differ by **$73.56 per line** and the result is
overwhelmingly significant, but Cohen's d is only *small* — because profit per
line swings from about −$6,600 to +$8,400, so the pooled standard deviation is
huge. The effect is real and worth acting on; it is simply buried in line-to-line
variance. That is precisely why the decision should rest on the means and the
confidence intervals (below), not on individual orders.

Chart: `reports/charts/02_ttest_mean_profit.png`

### Hypothesis test 2 — chi-square test of independence

**Question:** is customer `Segment` associated with product `Category`?

| | Value |
|---|---|
| χ² statistic | 1.4612 |
| Degrees of freedom | 4 |
| p value | 0.833 |
| Cramér's V | 0.0086 |
| Decision (α = 0.05) | **Fail to reject H₀** — independent |

**Interpretation — a genuinely useful negative result.** With 9,994 rows, a
p-value of 0.83 means there is no association at all: knowing a customer's
segment tells you essentially nothing about which category they buy. Category
marketing does **not** need to be re-cut for Consumer / Corporate / Home Office
audiences. Budget is better spent on discount policy and customer segments,
which the other analyses show *do* matter.

Chart: `reports/charts/03_chisquare_segment_category.png`

### Confidence intervals (95%)

| Measure | Mean | 95% CI | Width |
|---|---|---|---|
| Sales (all lines) | 229.86 | 217.64 → 242.08 | 24.44 |
| Profit (all lines) | 28.66 | 24.06 → 33.25 | 9.19 |
| Profit (discounted) | −6.66 | −12.23 → −1.09 | 11.14 |
| Profit (full price) | 66.90 | 59.62 → 74.18 | 14.55 |

The discounted and full-price intervals **do not overlap**, which is independent
confirmation of the t-test: discounting genuinely depresses profit.

Chart: `reports/charts/04_confidence_intervals.png`

---

## Part 2 — Time Series Analysis (Day 23–24)

### Resampling

| Frequency | Points | Use |
|---|---|---|
| Daily | 1,460 | too noisy to read a trend |
| Weekly | 210 | useful for operations |
| Monthly | 48 | **chosen** — the right level for this dataset |

Chart: `reports/charts/05_resampled_series.png`

### Decomposition (additive, period = 12)

| Component | Strength |
|---|---|
| Trend | 0.279 |
| **Seasonal** | **0.805** |

Seasonality dominates: the annual Nov/Dec peak is far larger than the underlying
growth. Residuals are relatively small, so trend + seasonality explain most of
the movement.

Chart: `reports/charts/06_seasonal_decomposition.png`

### Moving-average forecast

- 3-month and 6-month moving averages computed on the monthly series
- Next 3 months forecast as the mean of the last 3 months
- Backtest over all months with a full window: **MAE $18,002.43, MAPE 50.58%**

**Interpretation.** MAPE of 50.58% is poor in absolute terms, and that is the
honest headline: a moving average tracks the *level* but lags badly at turning
points and completely flattens the Nov/Dec spike. It is a defensible planning
baseline, but the decomposition proves a seasonal model would do materially
better. Recommending this forecast as-is would be over-claiming.

Chart: `reports/charts/07_moving_average_forecast.png`

---

## Part 3 — Customer Segmentation with K-Means

### Method

1. Aggregated 9,994 order lines into **793 customers** with five features:
   `Recency`, `Frequency`, `Monetary`, `AvgDiscount`, `TotalQuantity`
2. **`StandardScaler`** — without it, `Monetary` (thousands) would completely
   dominate `AvgDiscount` (0–1)
3. **Elbow method** over k = 1…10 → the curve bends at **k = 4**
4. **K-Means, k = 4**
5. **PCA** to 2-D for plotting (PC1 47.0% + PC2 20.3% = **67.3%** of variance)

### The four segments

| Segment | Customers | Share | Recency | Frequency | Monetary | Avg discount |
|---|---|---|---|---|---|---|
| **Champions** | 264 | 33.3% | 81 days | 8.9 orders | **$5,024.46** | 16% |
| **Steady core** | 273 | 34.4% | 97 days | 5.4 orders | $2,014.00 | 10% |
| **Discount seekers** | 168 | 21.2% | 111 days | 5.2 orders | $1,645.11 | **26%** |
| **Dormant / at risk** | 88 | 11.1% | **574 days** | 3.7 orders | $1,642.54 | 15% |

### Recommended action per segment

| Segment | Recommendation |
|---|---|
| **Champions** | Protect and grow. They already buy often and at high value — reward them with **loyalty benefits** (early access, free shipping, named account contact), *not* price cuts. Discounting them gives away margin they are already willing to pay. |
| **Steady core** | The biggest group and the most price-disciplined (10% average discount). Grow through **cross-sell** — attach accessories and consumables to the categories they already buy at full price. |
| **Discount seekers** | The only above-average discount habit and the lowest per-head spend. **Test cutting blanket discounts** here — Part 1 showed discounted lines average −$6.66 profit. Shift them to bundle pricing or free-shipping thresholds instead of percentage-off. |
| **Dormant / at risk** | 574 days since their last order — effectively lost. Send **one low-cost reactivation email** and stop. Do not spend acquisition-level budget, and do not discount. |

Charts: `reports/charts/08_elbow_method.png`, `09_clusters_pca.png`,
`10_cluster_profiles.png`. Full table: `reports/customer_segments.csv`.

---

## Part 4 — Basic Predictive Model (Day 25–26)

**Target:** `Sales` (numeric, so Linear Regression applies).
**Features:** `Quantity`, `Discount`, and one-hot encoded `Category`,
`Sub-Category`, `Region`, `Segment`, `Ship Mode`.
**Split:** 80 / 20 with `random_state=42` (7,995 train / 1,999 test).

| Metric | Result |
|---|---|
| R² | **0.186** |
| MAE | **$226.31** |
| RMSE | **$693.33** |

### Top 3 important features

| # | Feature | Coefficient |
|---|---|---|
| 1 | `Sub-Category_Copiers` | **+$2,224.12** |
| 2 | `Sub-Category_Machines` | **+$1,179.38** |
| 3 | `Discount` | **−$341.23** |

**Interpretation — stated honestly.** An R² of 0.186 is a *modest* result: the
model explains about 19% of the variation in sales, and is typically wrong by
$226 per order line. It should not be presented as an accurate sales forecaster.
What it *does* show reliably is **which levers move revenue**: being a Copier or
a Machine adds more to predicted sales than anything else, and each unit of
discount subtracts $341. That independently confirms the discount finding from
Part 1 and points at the same conclusion.

Charts: `reports/charts/11_model_actual_vs_predicted.png`,
`12_feature_importance.png`

---

## How to reproduce

```bash
pip install -r requirements.txt
jupyter notebook notebooks/Task4_Advanced_Analytics.ipynb
```

Headless:

```bash
jupyter nbconvert --to notebook --execute --inplace notebooks/Task4_Advanced_Analytics.ipynb
```

All paths are anchored off `data/superstore_cleaned.csv`, so the notebook runs
correctly from any working directory.

---

## Files in this task

```text
apexplanet-data-analytics-task-4/
├── notebooks/
│   └── Task4_Advanced_Analytics.ipynb   # stats + time series + KMeans + regression
├── reports/
│   ├── charts/                          # 12 PNG charts
│   └── customer_segments.csv            # 793 customers with cluster + segment label
├── requirements.txt
└── readme.md
```

---

## Summary of findings

| # | Analysis | Result |
|---|---|---|
| 1 | Descriptive statistics | Sales and Profit right-skewed; Profit has negative values; Discount is 0 for most lines |
| 2 | t-test (discount vs profit) | Significant (p ≈ 4.4 × 10⁻⁵⁵); $73.56 gap per line; small standardised effect (d = −0.32) |
| 3 | Chi-square (segment vs category) | **No association** (p = 0.833, V = 0.009) |
| 4 | Confidence intervals | Discounted and full-price intervals do not overlap |
| 5 | Time series | Seasonal strength 0.805 — strong annual Nov/Dec peak on a rising trend |
| 6 | Moving-average forecast | Baseline only: MAPE 50.58%, flattens the seasonal peak |
| 7 | K-Means (k = 4) | Champions 33.3% / Steady core 34.4% / Discount seekers 21.2% / Dormant 11.1% |
| 8 | Linear Regression | R² 0.186, MAE $226.31, RMSE $693.33; Copiers, Machines (+) and Discount (−) are the top drivers |

### Three recommendations

1. **Stop treating discount as free growth.** The t-test, the confidence
   intervals and the regression all agree. Cap routine discounts and require
   approval above the break-even band.
2. **Plan around seasonality, not a flat run rate.** Seasonal strength of 0.805
   means Nov/Dec targets and stock levels must be set month by month.
3. **Act differently on each segment.** Loyalty for Champions, cross-sell for
   Steady core, bundle pricing for Discount seekers, one cheap reactivation
   email for the Dormant group.

---

## LinkedIn post

> Task 4 complete! Went beyond dashboards into the statistics behind the numbers
> on the Superstore dataset (9,994 orders, 2014–2017):
>
> 🔹 **Hypothesis testing** — discounted orders average **−$6.66 profit** vs
> **+$66.90** at full price (p ≈ 4.4 × 10⁻⁵⁵). Discounting is not free growth.
> 🔹 **Time series** — seasonal strength 0.805: a clear Nov/Dec peak on top of a
> rising trend.
> 🔹 **K-Means segmentation** — 4 customer segments found; Champions (33% of
> customers) spend $5,024 each vs $1,645 for Discount seekers.
> 🔹 **Linear Regression** — an honest R² of 0.186 showing Copiers, Machines and
> Discount as the biggest drivers of sales.
>
> Full notebook on GitHub — link in the comments.
> #DataAnalytics #MachineLearning #Python #Statistics #KMeans
