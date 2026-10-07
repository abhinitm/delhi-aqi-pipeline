import json
import urllib.request

# Delhi coordinates
LAT, LON = 28.61, 77.21

url = (
    "https://air-quality-api.open-meteo.com/v1/air-quality"
    f"?latitude={LAT}&longitude={LON}"
    "&hourly=pm10,pm2_5,nitrogen_dioxide,ozone"
    "&past_days=1&forecast_days=1"
)

with urllib.request.urlopen(url) as response:
    data = json.loads(response.read())

print(json.dumps(data, indent=2)[:1500])