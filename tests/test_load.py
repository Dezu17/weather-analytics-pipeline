from datetime import date, timedelta

import psycopg
import pytest

from weather_pipeline.load import load


def make_rows(city_id: int, days: int = 7) -> list[dict]:
    start = date(2026, 10, 1)
    return [
        {
            "city_id": city_id,
            "date": start + timedelta(days=i),
            "temperature_mean": 12.0 + i,
            "temperature_max": 16.0 + i,
            "temperature_min": 8.0 + i,
            "precipitation_sum": 1.5,
            "rain_sum": 1.5,
            "precipitation_hours": 3.0,
            "wind_speed_max": 20.0,
        }
        for i in range(days)
    ]


def count_rows(conn, city_id: int) -> int:
    return conn.execute(
        "SELECT COUNT(*) AS n FROM daily_weather WHERE city_id = %s", (city_id,)
    ).fetchone()["n"]


def test_first_load_inserts_every_row(conn, city_id):
    counts = load(conn, make_rows(city_id))

    assert counts == {"inserted": 7, "updated": 0, "unchanged": 0}
    assert count_rows(conn, city_id) == 7


def test_rerun_with_same_data_changes_nothing(conn, city_id):
    rows = make_rows(city_id)
    load(conn, rows)

    counts = load(conn, rows)

    assert counts == {"inserted": 0, "updated": 0, "unchanged": 7}
    assert count_rows(conn, city_id) == 7


def test_changed_value_updates_only_that_row(conn, city_id):
    rows = make_rows(city_id)
    load(conn, rows)
    rows[3]["temperature_max"] = 30.0

    counts = load(conn, rows)

    assert counts == {"inserted": 0, "updated": 1, "unchanged": 6}
    stored = conn.execute(
        "SELECT temperature_max FROM daily_weather WHERE city_id = %s AND date = %s",
        (city_id, rows[3]["date"]),
    ).fetchone()["temperature_max"]
    assert stored == 30.0


def test_invalid_row_rolls_back_whole_batch(conn, city_id):
    rows = make_rows(city_id)
    rows[5]["precipitation_sum"] = -1.0

    with pytest.raises(psycopg.errors.CheckViolation):
        load(conn, rows)

    assert count_rows(conn, city_id) == 0


def test_none_is_stored_as_null(conn, city_id):
    rows = make_rows(city_id, days=1)
    rows[0]["precipitation_sum"] = None

    load(conn, rows)

    stored = conn.execute(
        "SELECT precipitation_sum FROM daily_weather WHERE city_id = %s", (city_id,)
    ).fetchone()["precipitation_sum"]
    assert stored is None


def test_empty_list_writes_nothing(conn, city_id):
    assert load(conn, []) == {"inserted": 0, "updated": 0, "unchanged": 0}
