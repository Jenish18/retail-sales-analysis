
import os
import psycopg

with psycopg.connect(
    host="localhost",
    port=5432,
    dbname="retail_intelligence",
    user="jenish",
    password=os.environ["PGPASSWORD"],
) as conn:

    with conn.cursor() as cur:
        cur.execute("SELECT current_database(), current_user;")
        result = cur.fetchone()

print("Database connection successful!")
print("Database:", result[0])
print("User:", result[1])
