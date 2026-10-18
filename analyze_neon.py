
import os
import psycopg

query = """
SELECT
    category,
    COUNT(*) AS order_count,
    ROUND(SUM(sales), 2) AS total_sales,
    ROUND(SUM(profit), 2) AS total_profit
FROM public.supermart_sales
GROUP BY category
ORDER BY total_sales DESC;
"""

with psycopg.connect(os.environ["NEON_DATABASE_URL"]) as conn:
    with conn.cursor() as cur:
        cur.execute(query)
        results = cur.fetchall()

print(f"{'CATEGORY':<22} {'ROWS':>6} {'SALES':>14} {'PROFIT':>14}")
print("-" * 60)

for category, count, sales, profit in results:
    print(f"{category:<22} {count:>6} {sales:>14,.2f} {profit:>14,.2f}")
