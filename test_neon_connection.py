
import os
import psycopg

database_url = os.environ["NEON_DATABASE_URL"]

with psycopg.connect(database_url) as conn:
    with conn.cursor() as cur:
        cur.execute("SELECT current_database(), current_user;")
        database_name, database_user = cur.fetchone()

print("Neon connection successful!")
print("Database:", database_name)
print("User:", database_user)
