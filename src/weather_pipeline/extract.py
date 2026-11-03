"""Extract: fetch daily weather from the Open-Meteo archive API and save the raw JSON."""

import json
from datetime import date
from pathlib import Path

import requests

from weather_pipeline import config

ARCHIVE_URL = "https://archive-api.open-meteo.com/v1/archive"
DAILY_VARIABLES = [
    "temperature_2m_mean",
    "temperature_2m_max",
    "temperature_2m_min",
    "precipitation_sum",
    "rain_sum",
    "precipitation_hours",
    "wind_speed_10m_max",
]
REQUEST_TIMEOUT_SECONDS = 30


def extract(city: dict, start_date: date, end_date: date) -> Path:
    """Fetch daily weather for one city and save the raw JSON. Returns the file path."""
    params = {
        "latitude": city["latitude"],
        "longitude": city["longitude"],
        "timezone": city["timezone"],
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
        "daily": ",".join(DAILY_VARIABLES),
    }
    response = requests.get(ARCHIVE_URL, params=params, timeout=REQUEST_TIMEOUT_SECONDS)
    response.raise_for_status()

    payload = response.json()
    if "daily" not in payload:
        raise ValueError(f"No 'daily' block in response for {city['city_name']}")

    path = config.RAW_DATA_DIR / f"{city['city_name']}_{city['country']}".lower() / f"{start_date}_{end_date}.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2))
    return path
