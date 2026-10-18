import os
import psycopg

with psycopg.connect(os.environ["NEON_DATABASE_URL"]) as conn:
    with conn.cursor() as cur:
        cur.execute("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
            ORDER BY table_name;
        """)

        tables = cur.fetchall()

print("Tables currently in Neon:")
for table in tables:
    print(table[0])