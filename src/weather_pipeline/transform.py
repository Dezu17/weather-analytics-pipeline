"""Transform: turn a raw Open-Meteo JSON file into one row per date for daily_weather."""

import json
from datetime import date
from pathlib import Path

# Open-Meteo daily field name -> daily_weather column name.
COLUMN_MAP = {
    "temperature_2m_mean": "temperature_mean",
    "temperature_2m_max": "temperature_max",
    "temperature_2m_min": "temperature_min",
    "precipitation_sum": "precipitation_sum",
    "rain_sum": "rain_sum",
    "precipitation_hours": "precipitation_hours",
    "wind_speed_10m_max": "wind_speed_max",
}


def transform(raw_path: Path, city_id: int) -> list[dict]:
    """Read a raw Open-Meteo file and return one daily_weather row per date.

    Missing values (null in the JSON) stay as None. They are not replaced with zero.
    """
    payload = json.loads(Path(raw_path).read_text())
    daily = payload["daily"]
    dates = daily["time"]

    missing = [field for field in COLUMN_MAP if field not in daily]
    if missing:
        raise ValueError(f"Missing fields in {raw_path}: {missing}")

    # zip() would silently drop values if the lists had different lengths, so check explicitly.
    for field in COLUMN_MAP:
        if len(daily[field]) != len(dates):
            raise ValueError(
                f"{field} has {len(daily[field])} values but {raw_path} has {len(dates)} dates"
            )

    rows = []
    for i, day in enumerate(dates):
        row = {"city_id": city_id, "date": date.fromisoformat(day)}
        for api_field, column in COLUMN_MAP.items():
            row[column] = daily[api_field][i]
        rows.append(row)
    return rows
