
import os

import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL

password = os.getenv("PGPASSWORD")
if not password:
    raise RuntimeError("Set PGPASSWORD before running tests.")

url = URL.create(
    "postgresql+psycopg",
    username=os.getenv("PGUSER", "jenish"),
    password=password,
    host=os.getenv("PGHOST", "localhost"),
    port=int(os.getenv("PGPORT", "5432")),
    database=os.getenv("PGDATABASE", "retail_intelligence"),
)

engine = create_engine(url, pool_pre_ping=True)

query = text("""
    SELECT
        COUNT(*) AS total_records,
        SUM(sales) AS total_sales,
        SUM(profit) AS total_profit,
        SUM(profit) / NULLIF(SUM(sales), 0) * 100
            AS profit_margin_pct,
        AVG(discount) * 100 AS average_discount_pct
    FROM supermart_sales
    WHERE order_date IS NOT NULL
""")

with engine.connect() as connection:
    result = pd.read_sql(query, connection).iloc[0]

assert result["total_records"] == 9994, (
    f"Unexpected record count: {result['total_records']}"
)

assert abs(result["total_sales"] - 14956982) < 0.01
assert abs(result["total_profit"] - 3747121.20) < 0.01
assert abs(result["profit_margin_pct"] - 25.05) < 0.02
assert abs(result["average_discount_pct"] - 22.68) < 0.02

print("PASS: All dashboard KPI validations succeeded.")
print(result)
engine.dispose()
