import psycopg2

conn = psycopg2.connect(
    host="localhost", port=5433,
    dbname="aqi_db", user="aqi_user", password="aqi_pass",
)
cur = conn.cursor()

checks = {
    "rows exist": ("SELECT COUNT(*) FROM raw_aqi", lambda n: n > 0),
    "no null pm2_5": ("SELECT COUNT(*) FROM raw_aqi WHERE pm2_5 IS NULL", lambda n: n == 0),
    "pm2_5 in range 0-1000": ("SELECT COUNT(*) FROM raw_aqi WHERE pm2_5 < 0 OR pm2_5 > 1000", lambda n: n == 0),
    "no duplicate hours": (
        "SELECT COUNT(*) FROM (SELECT observed_at FROM raw_aqi GROUP BY observed_at HAVING COUNT(*) > 1) d",
        lambda n: n == 0,
    ),
}

failed = 0
for name, (query, ok) in checks.items():
    cur.execute(query)
    value = cur.fetchone()[0]
    status = "PASS" if ok(value) else "FAIL"
    if status == "FAIL":
        failed += 1
    print(f"{status}  {name}  (value: {value})")

cur.close()
conn.close()
print(f"\n{failed} check(s) failed")