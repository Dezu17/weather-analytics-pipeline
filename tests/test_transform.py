import json
from datetime import date

import pytest

from weather_pipeline.extract import DAILY_VARIABLES
from weather_pipeline.transform import COLUMN_MAP, transform

DATES = ["2026-10-01", "2026-10-02", "2026-10-03"]


def make_payload() -> dict:
    """A minimal Open-Meteo response with three days of data."""
    daily = {"time": list(DATES)}
    for offset, field in enumerate(COLUMN_MAP):
        daily[field] = [float(offset + day) for day in range(len(DATES))]
    return {"daily": daily}


@pytest.fixture
def write_raw(tmp_path):
    def _write(payload: dict):
        path = tmp_path / "raw.json"
        path.write_text(json.dumps(payload))
        return path

    return _write


def test_column_map_covers_every_requested_variable():
    assert set(COLUMN_MAP) == set(DAILY_VARIABLES)


def test_returns_one_row_per_date(write_raw):
    rows = transform(write_raw(make_payload()), city_id=42)

    assert len(rows) == len(DATES)
    assert [row["date"] for row in rows] == [date.fromisoformat(d) for d in DATES]
    assert all(row["city_id"] == 42 for row in rows)


def test_renames_api_fields_to_column_names(write_raw):
    payload = make_payload()
    rows = transform(write_raw(payload), city_id=1)

    expected_keys = {"city_id", "date", *COLUMN_MAP.values()}
    assert set(rows[0]) == expected_keys
    assert rows[1]["wind_speed_max"] == payload["daily"]["wind_speed_10m_max"][1]


def test_null_values_stay_none(write_raw):
    payload = make_payload()
    payload["daily"]["precipitation_sum"][1] = None

    rows = transform(write_raw(payload), city_id=1)

    assert rows[1]["precipitation_sum"] is None


def test_list_shorter_than_dates_raises(write_raw):
    payload = make_payload()
    payload["daily"]["rain_sum"].pop()

    with pytest.raises(ValueError, match="rain_sum has 2 values"):
        transform(write_raw(payload), city_id=1)


def test_missing_field_raises(write_raw):
    payload = make_payload()
    del payload["daily"]["wind_speed_10m_max"]

    with pytest.raises(ValueError, match="wind_speed_10m_max"):
        transform(write_raw(payload), city_id=1)
