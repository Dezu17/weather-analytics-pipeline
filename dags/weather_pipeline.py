"""Manually triggered weather ETL for one city and date range: extract -> transform."""

from datetime import date, datetime, timedelta
from pathlib import Path

from airflow.sdk import Param, dag, task

from weather_pipeline.db import get_city, get_connection
from weather_pipeline.extract import extract
from weather_pipeline.transform import transform


@dag(
    dag_id="weather_pipeline",
    schedule=None,
    start_date=datetime(2026, 1, 1),
    catchup=False,
    tags=["weather"],
    params={
        "city": Param("Dublin", type="string"),
        "country": Param("Ireland", type="string"),
        "start_date": Param("2026-10-01", type="string", format="date"),
        "end_date": Param("2026-10-07", type="string", format="date"),
    },
)
def weather_pipeline():
    @task(retries=2, retry_delay=timedelta(minutes=1))
    def extract_city(**context) -> dict:
        params = context["params"]
        with get_connection() as conn:
            city = get_city(conn, params["city"], params["country"])

        raw_path = extract(
            city,
            date.fromisoformat(params["start_date"]),
            date.fromisoformat(params["end_date"]),
        )
        return {"city_id": city["city_id"], "raw_path": str(raw_path)}

    # No retries: a bad file fails the same way every time.
    @task
    def transform_rows(extracted: dict) -> list[dict]:
        rows = transform(Path(extracted["raw_path"]), extracted["city_id"])
        print(f"Transformed {len(rows)} rows from {extracted['raw_path']}")
        return rows

    transform_rows(extract_city())


weather_pipeline()
