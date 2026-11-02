CREATE TABLE IF NOT EXISTS cities (
    city_id     INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    city_name   VARCHAR(100)     NOT NULL,
    country     VARCHAR(100)     NOT NULL,
    latitude    DOUBLE PRECISION NOT NULL CHECK (latitude BETWEEN -90 AND 90),
    longitude   DOUBLE PRECISION NOT NULL CHECK (longitude BETWEEN -180 AND 180),
    timezone    VARCHAR(100)     NOT NULL,
    is_active   BOOLEAN          NOT NULL DEFAULT TRUE,
    UNIQUE (city_name, country)
);

CREATE TABLE IF NOT EXISTS daily_weather (
    city_id              INTEGER          NOT NULL REFERENCES cities (city_id),
    date                 DATE             NOT NULL,

    temperature_mean     DOUBLE PRECISION,
    temperature_max      DOUBLE PRECISION,
    temperature_min      DOUBLE PRECISION,
    precipitation_sum    DOUBLE PRECISION CHECK (precipitation_sum >= 0),
    rain_sum             DOUBLE PRECISION CHECK (rain_sum >= 0),
    precipitation_hours  DOUBLE PRECISION CHECK (precipitation_hours BETWEEN 0 AND 24),
    wind_speed_max       DOUBLE PRECISION CHECK (wind_speed_max >= 0),

    ingested_at          TIMESTAMPTZ      NOT NULL DEFAULT now(),
    updated_at           TIMESTAMPTZ      NOT NULL DEFAULT now(),

    PRIMARY KEY (city_id, date),
    CHECK (temperature_min <= temperature_max)
);