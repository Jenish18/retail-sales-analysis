
import os
from pathlib import Path

import psycopg


# 1. Locate the cleaned CSV file
csv_path = Path("data/processed/supermart_clean.csv")

if not csv_path.exists():
    raise FileNotFoundError(f"CSV file not found: {csv_path}")


# 2. Connect to PostgreSQL and load the CSV
with psycopg.connect(
    host="localhost",
    port=5432,
    dbname="retail_intelligence",
    user="jenish",
    password=os.environ["PGPASSWORD"],
) as conn:

    with conn.cursor() as cur:

        # 3. Prevent accidental duplicate imports
        cur.execute("SELECT COUNT(*) FROM supermart_sales")
        existing_rows = cur.fetchone()[0]

        if existing_rows > 0:
            raise RuntimeError(
                f"Import cancelled: table already contains "
                f"{existing_rows} rows."
            )

        # 4. Stream the CSV into PostgreSQL
        with csv_path.open(
            "r", encoding="utf-8-sig", newline=""
        ) as csv_file:

            with cur.copy("""
                COPY supermart_sales (
                    order_id,
                    customer_name,
                    category,
                    sub_category,
                    city,
                    order_date,
                    region,
                    sales,
                    discount,
                    profit,
                    state
                )
                FROM STDIN
                WITH (FORMAT CSV, HEADER TRUE)
            """) as copy:

                while chunk := csv_file.read(1024 * 1024):
                    copy.write(chunk)

        # 5. Verify the number of imported rows
        cur.execute("SELECT COUNT(*) FROM supermart_sales")
        total_rows = cur.fetchone()[0]

print("CSV import completed!")
print("Rows in PostgreSQL:", total_rows)
