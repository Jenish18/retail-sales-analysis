
import os
import subprocess
import io
import csv
import psycopg

NEON_URL = os.environ["NEON_DATABASE_URL"]

# 1. Export data from local PostgreSQL Docker container
result = subprocess.run(
    [
        "docker", "exec", "postgres-db",
        "psql", "-X", "-q", "-A", "-t",
        "-U", "jenish",
        "-d", "retail_intelligence",
        "-c",
        "COPY public.supermart_sales TO STDOUT "
        "WITH (FORMAT CSV, HEADER TRUE)"
    ],
    capture_output=True,
    text=True,
    check=True
)

csv_data = result.stdout

# 2. Parse CSV and count source records
rows = list(csv.reader(io.StringIO(csv_data)))

if not rows:
    raise RuntimeError("Local export returned no CSV data.")

header = rows[0]
data_rows = rows[1:]

if len(data_rows) != 9994:
    raise RuntimeError(
        f"Expected 9994 source rows, found {len(data_rows)}. "
        "Migration stopped."
    )

print("Local rows exported:", len(data_rows))
print("Connecting to Neon...")

# 3. Import into Neon only if target table is empty
with psycopg.connect(NEON_URL) as conn:
    with conn.cursor() as cur:
        cur.execute(
            "SELECT COUNT(*) FROM public.supermart_sales;"
        )
        existing_rows = cur.fetchone()[0]

        if existing_rows != 0:
            raise RuntimeError(
                f"Neon table already contains {existing_rows} rows. "
                "No rows were inserted."
            )

        with cur.copy(
            "COPY public.supermart_sales "
            "(order_id, customer_name, category, sub_category, "
            "city, order_date, region, sales, discount, profit, state) "
            "FROM STDIN WITH (FORMAT CSV, HEADER TRUE)"
        ) as copy:
            copy.write(csv_data)

        cur.execute(
            "SELECT COUNT(*) FROM public.supermart_sales;"
        )
        migrated_rows = cur.fetchone()[0]

print("Migration completed!")
print("Rows migrated:", migrated_rows)
