
# Superstore Sales Data Analysis

## Project Overview

This project performs Exploratory Data Analysis (EDA) on the Superstore Sales dataset using Python.

The purpose of this project is to clean the dataset, analyze sales and profit performance, identify patterns, and generate useful business insights.

## Tools and Libraries

- Python
- Pandas
- NumPy
- Matplotlib
- Seaborn
- Plotly

## Dataset

The dataset used for this project is the Sample Superstore dataset.

It contains information about:

- Orders
- Customers
- Products
- Categories
- Sales
- Quantity
- Discount
- Profit
- Regions
- Order and shipping dates

The dataset contains 21 columns.

## Data Cleaning

The following steps were performed:

1. Loaded the dataset using Pandas.
2. Checked the dataset structure.
3. Checked for missing values.
4. Checked and removed duplicate rows.
5. Checked data types.
6. Converted Order Date and Ship Date into datetime format.
7. Identified potential outliers using the IQR method.
8. Saved the cleaned dataset.

## Exploratory Data Analysis

The following analyses were performed:

- Sales by Category
- Profit by Category
- Sales by Region
- Monthly Sales Trend
- Top 10 Products by Sales
- Sales vs Profit
- Sales by Sub-Category
- Profit by Sub-Category
- Discount vs Profit
- Correlation Heatmap

## Key Business Insights

1. The category with the highest sales was identified through category-level analysis.

2. The most profitable category was identified by comparing total profit across categories.

3. Regional analysis showed which region generated the highest sales.

4. Product-level analysis identified the top-performing products by sales.

5. Sub-category and discount analysis helped identify areas with strong or weak profitability.

## Project Structure

```text
apexplanet-data-analytics/
│
├── data/
│   ├── Sample - Superstore.csv
│   └── superstore_cleaned.csv
│
├── notebooks/
│   └── Task1_EDA.ipynb
│
├── scripts/
├── reports/
│   └── charts/
│
├── dashboards/
└── README.md