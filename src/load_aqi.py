import os
import json
import urllib.request

import psycopg2

# Delhi coordinates
LAT, LON = 28.61, 77.21

url = (
    "https://air-quality-api.open-meteo.com/v1/air-quality"
    f"?latitude={LAT}&longitude={LON}"
    "&hourly=pm10,pm2_5,nitrogen_dioxide,ozone"
    "&past_days=7&forecast_days=1"
)

# 1. Collect: get the data from the API
with urllib.request.urlopen(url) as response:
    data = json.loads(response.read())

hourly = data["hourly"]

# 2. Connect to the database running in Docker
conn = psycopg2.connect(
       host=os.environ.get("DB_HOST", "localhost"),
       port=int(os.environ.get("DB_PORT", "5433")),
       dbname="aqi_db",
       user="aqi_user",
       password="aqi_pass",
   )
cur = conn.cursor()

# 3. Store: insert one row per hour
rows = zip(
    hourly["time"],
    hourly["pm10"],
    hourly["pm2_5"],
    hourly["nitrogen_dioxide"],
    hourly["ozone"],
)

for observed_at, pm10, pm2_5, no2, ozone in rows:
    cur.execute(
        """
        INSERT INTO raw_aqi (observed_at, pm10, pm2_5, nitrogen_dioxide, ozone)
        VALUES (%s, %s, %s, %s, %s)
        ON CONFLICT (observed_at) DO NOTHING
        """,
        (observed_at, pm10, pm2_5, no2, ozone),
    )

conn.commit()
cur.close()
conn.close()

print("Done. Rows loaded.")