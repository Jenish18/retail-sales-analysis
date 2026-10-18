
import os

import pandas as pd
import streamlit as st
import plotly.express as px
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL

# ---------------------------
# 1. Page configuration
# ---------------------------
st.set_page_config(
    page_title="Supermart Sales Intelligence",
    page_icon="🛒",
    layout="wide",
)

st.title("🛒 Supermart Sales Intelligence Dashboard")
st.caption("Sales | Profitability | Discount | Regional Performance")

# ---------------------------
# 2. Database connection
# ---------------------------
@st.cache_resource
def get_engine():
    password = os.getenv("PGPASSWORD")

    if not password:
        raise RuntimeError(
            "PGPASSWORD is missing. Set it in your terminal before "
            "starting the dashboard."
        )

    url = URL.create(
        drivername="postgresql+psycopg",
        username=os.getenv("PGUSER", "jenish"),
        password=password,
        host=os.getenv("PGHOST", "localhost"),
        port=int(os.getenv("PGPORT", "5432")),
        database=os.getenv("PGDATABASE", "retail_intelligence"),
    )

    return create_engine(url, pool_pre_ping=True)


@st.cache_data(ttl=300)
def load_data():
    query = text("""
        SELECT
            order_date,
            category,
            sub_category,
            region,
            city,
            sales,
            profit,
            discount
        FROM supermart_sales
        WHERE order_date IS NOT NULL
    """)

    with get_engine().connect() as connection:
        df = pd.read_sql(query, connection)

    df["order_date"] = pd.to_datetime(df["order_date"])
    return df


# ---------------------------
# 3. Load data safely
# ---------------------------
try:
    df = load_data()
except Exception as exc:
    st.error(f"Unable to load dashboard data: {exc}")
    st.info(
        "Check that PostgreSQL is running, the database/table exists, "
        "and the connection settings are correct."
    )
    st.stop()

if df.empty:
    st.warning("No sales records found.")
    st.stop()

# ---------------------------
# 4. Sidebar filters
# ---------------------------
st.sidebar.header("Dashboard Filters")

min_date = df["order_date"].min().date()
max_date = df["order_date"].max().date()

date_range = st.sidebar.date_input(
    "Order date range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date,
)

selected_categories = st.sidebar.multiselect(
    "Category",
    options=sorted(df["category"].dropna().unique()),
    default=sorted(df["category"].dropna().unique()),
)

selected_regions = st.sidebar.multiselect(
    "Region",
    options=sorted(df["region"].dropna().unique()),
    default=sorted(df["region"].dropna().unique()),
)

if not isinstance(date_range, (tuple, list)) or len(date_range) != 2:
    st.info("Please select both a start date and an end date.")
    st.stop()

start_date, end_date = date_range

if start_date > end_date:
    st.warning("Start date must be before end date.")
    st.stop()

filtered_df = df[
    (df["order_date"].dt.date >= start_date)
    & (df["order_date"].dt.date <= end_date)
    & (df["category"].isin(selected_categories))
    & (df["region"].isin(selected_regions))
].copy()

if filtered_df.empty:
    st.warning("No records match the selected filters.")
    st.stop()

# ---------------------------
# 5. KPI calculations
# ---------------------------
total_sales = filtered_df["sales"].sum()
total_profit = filtered_df["profit"].sum()
profit_margin = (
    total_profit / total_sales * 100
    if total_sales != 0
    else 0
)
average_discount = filtered_df["discount"].mean() * 100
record_count = len(filtered_df)

# ---------------------------
# 6. KPI cards
# ---------------------------
k1, k2, k3, k4 = st.columns(4)

k1.metric("Total Sales", f"{total_sales:,.2f}")
k2.metric("Total Profit", f"{total_profit:,.2f}")
k3.metric("Profit Margin", f"{profit_margin:.2f}%")
k4.metric("Average Discount", f"{average_discount:.2f}%")

st.caption(
    f"Showing {record_count:,} records | "
    f"{start_date} to {end_date}"
)

# ---------------------------
# 7. Monthly sales trend
# ---------------------------
st.subheader("Monthly Sales Trend")

monthly_df = (
    filtered_df
    .assign(month=filtered_df["order_date"].dt.to_period("M").dt.to_timestamp())
    .groupby("month", as_index=False)
    .agg(
        total_sales=("sales", "sum"),
        total_profit=("profit", "sum"),
    )
    .sort_values("month")
)

fig_monthly = px.line(
    monthly_df,
    x="month",
    y="total_sales",
    markers=True,
    title="Monthly Sales",
    labels={"month": "Month", "total_sales": "Total Sales"},
)

st.plotly_chart(fig_monthly, use_container_width=True)

# ---------------------------
# 8. Category performance
# ---------------------------
st.subheader("Category Performance")

category_df = (
    filtered_df
    .groupby("category", as_index=False)
    .agg(
        total_sales=("sales", "sum"),
        total_profit=("profit", "sum"),
    )
)

left, right = st.columns(2)

with left:
    fig_sales = px.bar(
        category_df,
        x="category",
        y="total_sales",
        title="Sales by Category",
        labels={"category": "Category", "total_sales": "Sales"},
    )
    st.plotly_chart(fig_sales, use_container_width=True)

with right:
    fig_profit = px.bar(
        category_df,
        x="category",
        y="total_profit",
        title="Profit by Category",
        labels={"category": "Category", "total_profit": "Profit"},
    )
    st.plotly_chart(fig_profit, use_container_width=True)

# ---------------------------
# 9. Regional performance
# ---------------------------
st.subheader("Regional Performance")

region_df = (
    filtered_df
    .groupby("region", as_index=False)
    .agg(
        total_sales=("sales", "sum"),
        total_profit=("profit", "sum"),
    )
)

fig_region = px.bar(
    region_df,
    x="region",
    y="total_profit",
    color="region",
    title="Total Profit by Region",
    labels={"region": "Region", "total_profit": "Profit"},
)

st.plotly_chart(fig_region, use_container_width=True)

# ---------------------------
# 10. Detailed data
# ---------------------------
with st.expander("View filtered sales data"):
    st.dataframe(filtered_df, use_container_width=True)

    csv_data = filtered_df.to_csv(index=False).encode("utf-8")

    st.download_button(
        label="Download filtered data as CSV",
        data=csv_data,
        file_name="filtered_supermart_sales.csv",
        mime="text/csv",
    )


# ---------------------------
# 10. Discount impact analysis
# ---------------------------
st.subheader("Discount Analysis")

discount_analysis_df = filtered_df.copy()

# Convert decimal discount to percentage for display
discount_analysis_df["discount_pct"] = (
    discount_analysis_df["discount"] * 100
)

discount_analysis_df["discount_band"] = pd.cut(
    discount_analysis_df["discount_pct"],
    bins=[-0.001, 0, 10, 20, float("inf")],
    labels=[
        "0% discount",
        "1–10%",
        "11–20%",
        "Above 20%",
    ],
    include_lowest=True,
)

discount_summary = (
    discount_analysis_df
    .groupby("discount_band", observed=False)
    .agg(
        records=("sales", "size"),
        total_sales=("sales", "sum"),
        total_profit=("profit", "sum"),
    )
    .reset_index()
)

discount_summary["profit_margin_pct"] = (
    discount_summary["total_profit"]
    .div(discount_summary["total_sales"].replace(0, float("nan")))
    .mul(100)
)

left, right = st.columns(2)

with left:
    fig_discount_sales = px.bar(
        discount_summary,
        x="discount_band",
        y="total_sales",
        title="Sales by Discount Band",
        labels={
            "discount_band": "Discount",
            "total_sales": "Total Sales",
        },
    )
    st.plotly_chart(
        fig_discount_sales,
        use_container_width=True,
    )

with right:
    fig_discount_profit = px.bar(
        discount_summary,
        x="discount_band",
        y="total_profit",
        title="Profit by Discount Band",
        labels={
            "discount_band": "Discount",
            "total_profit": "Total Profit",
        },
    )
    st.plotly_chart(
        fig_discount_profit,
        use_container_width=True,
    )

st.caption(
    "Discount-group comparisons are observational. "
    "Higher discounts do not necessarily cause higher profit."
)

with st.expander("View discount analysis table"):
    display_df = discount_summary.copy()
    display_df["profit_margin_pct"] = (
        display_df["profit_margin_pct"].round(2)
    )
    st.dataframe(display_df, use_container_width=True)
