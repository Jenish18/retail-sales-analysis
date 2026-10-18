
import os
import psycopg

database_url = os.environ["NEON_DATABASE_URL"]

create_table_sql = """
CREATE TABLE IF NOT EXISTS public.supermart_sales (
    order_id TEXT PRIMARY KEY,
    customer_name TEXT NOT NULL,
    category TEXT,
    sub_category TEXT,
    city TEXT,
    order_date DATE NOT NULL,
    region TEXT,
    sales NUMERIC(12,2) NOT NULL,
    discount NUMERIC(5,4),
    profit NUMERIC(12,2) NOT NULL,
    state TEXT
);
"""

with psycopg.connect(database_url) as conn:
    with conn.cursor() as cur:
        cur.execute(create_table_sql)

        cur.execute("""
            SELECT COUNT(*)
            FROM information_schema.columns
            WHERE table_schema = 'public'
              AND table_name = 'supermart_sales';
        """)
        column_count = cur.fetchone()[0]

print("Neon table schema is ready!")
print("Column count:", column_count)
