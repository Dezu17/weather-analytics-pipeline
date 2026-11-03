"""Manually triggered DAG that extracts daily weather for one city and date range."""

from datetime import date, datetime, timedelta

from airflow.sdk import Param, dag, task

from weather_pipeline.db import get_city, get_connection
from weather_pipeline.extract import extract


@dag(
    dag_id="extract_weather",
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
def extract_weather():
    @task(retries=2, retry_delay=timedelta(minutes=1))
    def extract_city(**context) -> str:
        params = context["params"]
        with get_connection() as conn:
            city = get_city(conn, params["city"], params["country"])

        raw_path = extract(
            city,
            date.fromisoformat(params["start_date"]),
            date.fromisoformat(params["end_date"]),
        )
        return str(raw_path)

    extract_city()


extract_weather()
