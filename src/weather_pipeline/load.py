"""Load: upsert transformed rows into daily_weather."""

import psycopg

# On conflict, only update when a weather value actually changed, so reruns leave
# updated_at untouched. RETURNING (xmax = 0) is true for inserted rows and false
# for updated ones; unchanged rows return nothing.
UPSERT_SQL = """
INSERT INTO daily_weather (
    city_id, date,
    temperature_mean, temperature_max, temperature_min,
    precipitation_sum, rain_sum, precipitation_hours, wind_speed_max
)
VALUES (
    %(city_id)s, %(date)s,
    %(temperature_mean)s, %(temperature_max)s, %(temperature_min)s,
    %(precipitation_sum)s, %(rain_sum)s, %(precipitation_hours)s, %(wind_speed_max)s
)
ON CONFLICT (city_id, date) DO UPDATE SET
    temperature_mean    = EXCLUDED.temperature_mean,
    temperature_max     = EXCLUDED.temperature_max,
    temperature_min     = EXCLUDED.temperature_min,
    precipitation_sum   = EXCLUDED.precipitation_sum,
    rain_sum            = EXCLUDED.rain_sum,
    precipitation_hours = EXCLUDED.precipitation_hours,
    wind_speed_max      = EXCLUDED.wind_speed_max,
    updated_at          = now()
WHERE (
    daily_weather.temperature_mean, daily_weather.temperature_max, daily_weather.temperature_min,
    daily_weather.precipitation_sum, daily_weather.rain_sum, daily_weather.precipitation_hours,
    daily_weather.wind_speed_max
) IS DISTINCT FROM (
    EXCLUDED.temperature_mean, EXCLUDED.temperature_max, EXCLUDED.temperature_min,
    EXCLUDED.precipitation_sum, EXCLUDED.rain_sum, EXCLUDED.precipitation_hours,
    EXCLUDED.wind_speed_max
)
RETURNING (xmax = 0) AS inserted
"""


def load(conn: psycopg.Connection, rows: list[dict]) -> dict[str, int]:
    """Upsert rows into daily_weather in a single transaction.

    Returns counts of inserted, updated and unchanged rows. If any row fails
    (for example a CHECK constraint), nothing is written.
    """
    inserted = updated = 0

    if rows:
        with conn.transaction(), conn.cursor() as cur:
            cur.executemany(UPSERT_SQL, rows, returning=True)
            while True:
                result = cur.fetchone()
                if result is not None:
                    if result["inserted"]:
                        inserted += 1
                    else:
                        updated += 1
                if not cur.nextset():
                    break

    return {
        "inserted": inserted,
        "updated": updated,
        "unchanged": len(rows) - inserted - updated,
    }
