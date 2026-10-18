# Supermart Sales Intelligence Dashboard

An end-to-end retail analytics project that uses PostgreSQL, Python, SQL, and Streamlit to analyze supermarket sales, profitability, discount patterns, seasonality, and regional performance.

## Business Problem

Retail businesses need to understand which categories generate revenue, how profitability varies across products and regions, and how sales change over time. This project transforms raw supermarket transaction data into actionable business insights through SQL analysis and an interactive dashboard.

## Project Objectives

- Analyze overall sales and profit performance.
- Identify monthly sales trends and seasonal patterns.
- Compare category and subcategory profitability.
- Evaluate sales and profit across discount bands.
- Compare regional and city-level performance.
- Build an interactive dashboard for exploring the data.
- Validate key dashboard metrics using automated Python tests.

## Technology Stack

- **Python** — data analysis and visualization
- **PostgreSQL** — data storage and SQL analytics
- **Pandas** — data manipulation
- **SQLAlchemy and Psycopg** — database connectivity
- **Streamlit** — interactive dashboard
- **Plotly, Matplotlib and Seaborn** — visualizations
- **Jupyter Notebook** — exploratory and business analysis

## Key Business Findings

Based on the current dataset analysis:

- **Total sales:** 14,956,982
- **Total profit:** 3,747,121.20
- **Overall profit margin:** approximately 25.05%
- **Average discount:** approximately 22.68%
- **Total records:** 9,994
- **Seasonality:** November has the highest average monthly sales among the months analyzed.
- **Regional performance:** West generates the highest total sales and profit among regions with meaningful record counts.
- **Margin opportunity:** Spices has a 23.82% profit margin among the ten lowest-margin subcategories examined.

*Note: The dataset's monetary unit has not been independently verified. Findings are descriptive and do not establish that discounts cause changes in profit.*

## Dashboard Features

- KPI cards for sales, profit, profit margin, and average discount
- Interactive date-range filtering
- Category and region filters
- Monthly sales trend visualization
- Category-wise sales and profit comparisons
- Regional profit comparison
- Discount-band analysis
- Filtered transaction table
- CSV export of filtered data

## Project Structure

```text
retail-sales-analysis/
├── app.py
├── README.md
├── data/
│   ├── raw/
│   └── processed/
├── notebooks/
│   └── 02_sales_analysis.ipynb
└── tests/
    └── test_dashboard_data.py
```

*Adjust the notebook path above if your notebook is stored in the project root instead of `notebooks/`.*

## Setup Instructions

### 1. Clone the repository

```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd retail-sales-analysis
```

### 2. Create and activate a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
python -m pip install pandas streamlit plotly matplotlib seaborn sqlalchemy "psycopg[binary]" jupyter
```

### 4. Configure PostgreSQL

Create or use a PostgreSQL database named `retail_intelligence`, and ensure the `supermart_sales` table has been populated with the dataset.

Set the connection environment variables in your terminal:

```bash
export PGUSER="jenish"
export PGPASSWORD="YOUR_ACTUAL_POSTGRES_PASSWORD"
export PGHOST="localhost"
export PGPORT="5432"
export PGDATABASE="retail_intelligence"
```

Replace the example username and password with your own PostgreSQL credentials. Never commit passwords or other secrets to GitHub.

### 5. Run the dashboard

```bash
streamlit run app.py
```

### 6. Run data validation tests

```bash
python tests/test_dashboard_data.py
```

The current KPI validation script checks record count, sales, profit, profit margin, and average discount against the expected full-dataset results.

## Business Recommendations

- Investigate demand patterns before planning seasonal inventory.
- Evaluate discounts using both profit and sales performance.
- Review lower-margin subcategories for pricing and cost opportunities.
- Validate city-to-region mappings before making location-based decisions.
- Monitor profit margin alongside total sales when evaluating performance.

## Limitations

- Results reflect the provided dataset and may not represent current supermarket conditions.
- Observed relationships do not prove causation.
- City-region mappings and the dataset's monetary unit should be independently verified.
- The current validation test covers overall KPIs, not every dashboard interaction.

## Future Improvements

- Deploy the dashboard online.
- Add automated tests for filters and visualizations.
- Add customer and product-level drill-downs.
- Implement sales forecasting.
- Add automated data-quality checks and refresh workflows.

## Author

Created as a portfolio project to demonstrate SQL analytics, Python data processing, database integration, business intelligence, and dashboard development.
