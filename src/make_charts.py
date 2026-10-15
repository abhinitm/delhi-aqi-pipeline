import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
import psycopg2

# 1. Get the data from the clean view
conn = psycopg2.connect(
    host=os.environ.get("DB_HOST", "localhost"),
    port=int(os.environ.get("DB_PORT", "5433")),
    dbname="aqi_db",
    user="aqi_user",
    password="aqi_pass",
)
cur = conn.cursor()
cur.execute("""
    SELECT observed_at_ist, aqi
    FROM clean_aqi
    WHERE NOT is_forecast
    ORDER BY observed_at_ist
""")
rows = cur.fetchall()
cur.close()
conn.close()

df = pd.DataFrame(rows, columns=["observed_at_ist", "aqi"])
df["observed_at_ist"] = pd.to_datetime(df["observed_at_ist"])
df["aqi"] = df["aqi"].astype(float)

# Skip the first 23 hours: their 24h average is incomplete
df = df.iloc[23:]

os.makedirs("charts", exist_ok=True)

# 2. Chart 1: AQI over time with category bands
bands = [
    (0, 50, "Good", "#4caf50"),
    (50, 100, "Satisfactory", "#9ccc65"),
    (100, 200, "Moderate", "#ffeb3b"),
    (200, 300, "Poor", "#ff9800"),
    (300, 400, "Very Poor", "#f44336"),
    (400, 500, "Severe", "#7b1fa2"),
]
top = max(300, df["aqi"].max() + 50)

fig, ax = plt.subplots(figsize=(11, 5))
for low, high, label, colour in bands:
    if low < top:
        ax.axhspan(low, high, color=colour, alpha=0.15, label=label)
ax.plot(df["observed_at_ist"], df["aqi"], color="black", linewidth=1.5)
ax.set_ylim(0, top)
ax.set_title("Delhi AQI over time (CPCB method, PM-based, 24h average)")
ax.set_xlabel("Date (India time)")
ax.set_ylabel("AQI")
ax.legend(loc="upper left", fontsize=8)
fig.autofmt_xdate()
fig.tight_layout()
fig.savefig("charts/aqi_over_time.png", dpi=150)
plt.close(fig)

# 3. Chart 2: average AQI by hour of day
df["hour"] = df["observed_at_ist"].dt.hour
by_hour = df.groupby("hour")["aqi"].mean()

fig, ax = plt.subplots(figsize=(11, 5))
ax.bar(by_hour.index, by_hour.values, color="#5c6bc0")
ax.set_xticks(range(24))
ax.set_title("Average Delhi AQI by hour of day (India time)")
ax.set_xlabel("Hour of day")
ax.set_ylabel("Average AQI")
fig.tight_layout()
fig.savefig("charts/aqi_by_hour.png", dpi=150)
plt.close(fig)

# 4. Print a short summary
worst_hour = by_hour.idxmax()
best_hour = by_hour.idxmin()
print(f"Hours analysed: {len(df)}")
print(f"From {df['observed_at_ist'].min()} to {df['observed_at_ist'].max()}")
print(f"Average AQI: {df['aqi'].mean():.0f}")
print(f"Worst hour of day: {worst_hour}:00 (avg AQI {by_hour.max():.0f})")
print(f"Best hour of day: {best_hour}:00 (avg AQI {by_hour.min():.0f})")
print("Charts saved in the charts/ folder.")