import psycopg2

conn = psycopg2.connect(
    host="localhost", port=5433,
    dbname="aqi_db", user="aqi_user", password="aqi_pass",
)
cur = conn.cursor()

# Each check: (name, SQL that counts PROBLEMS). 0 problems = PASS.
checks = [
    ("table is not empty",
     "SELECT CASE WHEN COUNT(*) = 0 THEN 1 ELSE 0 END FROM raw_aqi"),
    ("no missing pm2_5 values",
     "SELECT COUNT(*) FROM raw_aqi WHERE pm2_5 IS NULL"),
    ("pm2_5 between 0 and 1000",
     "SELECT COUNT(*) FROM raw_aqi WHERE pm2_5 < 0 OR pm2_5 > 1000"),
    ("no duplicate hours",
     """SELECT COUNT(*) FROM (
            SELECT observed_at FROM raw_aqi
            GROUP BY observed_at HAVING COUNT(*) > 1
        ) AS dupes"""),
    ("no missing hours (gaps)",
     """SELECT COUNT(*)
        FROM generate_series(
            (SELECT MIN(observed_at) FROM raw_aqi),
            (SELECT MAX(observed_at) FROM raw_aqi),
            INTERVAL '1 hour'
        ) AS expected(hour)
        WHERE expected.hour NOT IN (SELECT observed_at FROM raw_aqi)"""),
]

failed = 0
for name, query in checks:
    cur.execute(query)
    problems = cur.fetchone()[0]
    if problems == 0:
        print(f"PASS  {name}")
    else:
        print(f"FAIL  {name}  ({problems} problem rows)")
        failed += 1

cur.close()
conn.close()

print()
print(f"{len(checks) - failed} passed, {failed} failed")