
import os
import subprocess
import psycopg

query = """
SELECT
    COUNT(*),
    ROUND(SUM(sales), 2),
    ROUND(SUM(profit), 2)
FROM public.supermart_sales;
"""

# 1. Get the source totals from local PostgreSQL in Docker
result = subprocess.run(
    [
        "docker", "exec", "postgres-db",
        "psql", "-X", "-A", "-t", "-F", ",",
        "-U", "jenish",
        "-d", "retail_intelligence",
        "-c", query,
    ],
    capture_output=True,
    text=True,
    check=True,
)

local_values = result.stdout.strip().split(",")
local_count = int(local_values[0])
local_sales = local_values[1]
local_profit = local_values[2]

# 2. Get the migrated totals from Neon
with psycopg.connect(os.environ["NEON_DATABASE_URL"]) as conn:
    with conn.cursor() as cur:
        cur.execute(query)
        neon_count, neon_sales, neon_profit = cur.fetchone()

# 3. Compare source and cloud values
print("LOCAL DATABASE")
print("Rows:", local_count)
print("Total sales:", local_sales)
print("Total profit:", local_profit)

print("\nNEON CLOUD DATABASE")
print("Rows:", neon_count)
print("Total sales:", neon_sales)
print("Total profit:", neon_profit)

match = (
    local_count == neon_count
    and local_sales == str(neon_sales)
    and local_profit == str(neon_profit)
)

print("\nVerification:", "PASSED" if match else "FAILED")

if not match:
    raise SystemExit("Data verification failed. Investigate before proceeding.")
