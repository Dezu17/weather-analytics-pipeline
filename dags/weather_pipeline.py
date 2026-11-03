"""Manually triggered weather ETL for every active city: extract -> transform -> load.

Each step is mapped per city, so one city failing doesn't stop the others.
"""

from datetime import date, datetime, timedelta
from pathlib import Path

from airflow.sdk import Param, dag, get_current_context, task, task_group

from weather_pipeline.db import get_active_cities, get_connection
from weather_pipeline.extract import extract
from weather_pipeline.load import load
from weather_pipeline.transform import transform

# Shows the city name instead of 0, 1, 2... for each mapped task in the UI.
CITY_LABEL = "{{ city_label }}"


def _label(city_name: str) -> None:
    get_current_context()["city_label"] = city_name


@dag(
    dag_id="weather_pipeline",
    schedule=None,
    start_date=datetime(2026, 1, 1),
    catchup=False,
    tags=["weather"],
    params={
        "start_date": Param("2026-10-01", type="string", format="date"),
        "end_date": Param("2026-10-07", type="string", format="date"),
    },
)
def weather_pipeline():
    @task
    def list_active_cities() -> list[dict]:
        with get_connection() as conn:
            cities = get_active_cities(conn)
        print(f"Active cities: {[city['city_name'] for city in cities]}")
        return cities

    @task(retries=2, retry_delay=timedelta(minutes=1), map_index_template=CITY_LABEL)
    def extract_city(city: dict, **context) -> dict:
        _label(city["city_name"])
        params = context["params"]
        raw_path = extract(
            city,
            date.fromisoformat(params["start_date"]),
            date.fromisoformat(params["end_date"]),
        )
        return {
            "city_id": city["city_id"],
            "city_name": city["city_name"],
            "raw_path": str(raw_path),
        }

    # No retries: a bad file fails the same way every time.
    @task(map_index_template=CITY_LABEL)
    def transform_rows(extracted: dict) -> dict:
        _label(extracted["city_name"])
        rows = transform(Path(extracted["raw_path"]), extracted["city_id"])
        print(f"Transformed {len(rows)} rows from {extracted['raw_path']}")
        return {"city_name": extracted["city_name"], "rows": rows}

    @task(retries=2, retry_delay=timedelta(minutes=1), map_index_template=CITY_LABEL)
    def load_rows(transformed: dict) -> dict:
        _label(transformed["city_name"])
        with get_connection() as conn:
            counts = load(conn, transformed["rows"])
        print(f"Loaded into daily_weather: {counts}")
        return counts

    # Mapping the whole group (not each task separately) links the steps per city,
    # so a failure for one city only blocks that city's later steps.
    @task_group
    def city_etl(city: dict):
        load_rows(transform_rows(extract_city(city)))

    city_etl.expand(city=list_active_cities())


weather_pipeline()
