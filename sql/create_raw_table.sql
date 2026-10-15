CREATE TABLE IF NOT EXISTS raw_aqi (
    id SERIAL PRIMARY KEY,
    observed_at TIMESTAMP NOT NULL,
    pm10 NUMERIC,
    pm2_5 NUMERIC,
    nitrogen_dioxide NUMERIC,
    ozone NUMERIC,
    UNIQUE (observed_at)
);