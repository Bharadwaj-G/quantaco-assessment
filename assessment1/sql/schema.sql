-- Quantaco Weather API — schema
-- Source of truth for the venue/weather tables

CREATE TABLE IF NOT EXISTS venue (
    id        INTEGER PRIMARY KEY,
    name      VARCHAR NOT NULL,
    latitude  NUMERIC NOT NULL,
    longitude NUMERIC NOT NULL
);

CREATE TABLE IF NOT EXISTS weather (
    id                          SERIAL PRIMARY KEY,
    venue_id                    INTEGER NOT NULL REFERENCES venue(id),
    datetime                    TIMESTAMP NOT NULL,
    temperature_2m              NUMERIC,
    relative_humidity_2m        NUMERIC,
    dewpoint_2m                 NUMERIC,
    apparent_temperature        NUMERIC,
    precipitation_probability   NUMERIC,
    precipitation                NUMERIC,
    rain                        NUMERIC,
    showers                     NUMERIC,
    snowfall                    NUMERIC,
    snow_depth                  NUMERIC,
    created_at                  TIMESTAMP NOT NULL DEFAULT now(),
    updated_at                  TIMESTAMP NOT NULL DEFAULT now(),
    CONSTRAINT uq_weather_venue_datetime UNIQUE (venue_id, datetime)
);
