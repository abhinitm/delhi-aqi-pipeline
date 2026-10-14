CREATE OR REPLACE VIEW clean_aqi AS
WITH base AS (
    SELECT
        observed_at AS observed_at_utc,
        observed_at + INTERVAL '5 hours 30 minutes' AS observed_at_ist,
        observed_at > (NOW() AT TIME ZONE 'UTC') AS is_forecast,
        pm10,
        pm2_5,
        nitrogen_dioxide,
        ozone,
        AVG(pm2_5) OVER (ORDER BY observed_at
                         ROWS BETWEEN 23 PRECEDING AND CURRENT ROW) AS pm2_5_24h,
        AVG(pm10)  OVER (ORDER BY observed_at
                         ROWS BETWEEN 23 PRECEDING AND CURRENT ROW) AS pm10_24h
    FROM raw_aqi
),
sub_index AS (
    SELECT
        *,
        CASE
            WHEN pm2_5_24h <= 30  THEN pm2_5_24h * 50 / 30
            WHEN pm2_5_24h <= 60  THEN 50  + (pm2_5_24h - 30)  * 50  / 30
            WHEN pm2_5_24h <= 90  THEN 100 + (pm2_5_24h - 60)  * 100 / 30
            WHEN pm2_5_24h <= 120 THEN 200 + (pm2_5_24h - 90)  * 100 / 30
            WHEN pm2_5_24h <= 250 THEN 300 + (pm2_5_24h - 120) * 100 / 130
            ELSE LEAST(500, 400 + (pm2_5_24h - 250) * 100 / 130)
        END AS pm2_5_index,
        CASE
            WHEN pm10_24h <= 100 THEN pm10_24h
            WHEN pm10_24h <= 250 THEN 100 + (pm10_24h - 100) * 100 / 150
            WHEN pm10_24h <= 350 THEN 200 + (pm10_24h - 250)
            WHEN pm10_24h <= 430 THEN 300 + (pm10_24h - 350) * 100 / 80
            ELSE LEAST(500, 400 + (pm10_24h - 430) * 100 / 80)
        END AS pm10_index
    FROM base
),
scored AS (
    SELECT
        *,
        GREATEST(pm2_5_index, pm10_index) AS aqi_raw
    FROM sub_index
)
SELECT
    observed_at_utc,
    observed_at_ist,
    is_forecast,
    pm10,
    pm2_5,
    nitrogen_dioxide,
    ozone,
    ROUND(pm2_5_24h, 1) AS pm2_5_24h_avg,
    ROUND(pm10_24h, 1)  AS pm10_24h_avg,
    ROUND(aqi_raw)      AS aqi,
    CASE
        WHEN aqi_raw <= 50  THEN 'Good'
        WHEN aqi_raw <= 100 THEN 'Satisfactory'
        WHEN aqi_raw <= 200 THEN 'Moderate'
        WHEN aqi_raw <= 300 THEN 'Poor'
        WHEN aqi_raw <= 400 THEN 'Very Poor'
        ELSE 'Severe'
    END AS aqi_category,
    CASE WHEN pm2_5_index >= pm10_index THEN 'PM2.5' ELSE 'PM10' END AS main_pollutant
FROM scored;