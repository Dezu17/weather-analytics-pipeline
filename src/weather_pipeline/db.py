"""Database connection and lookup helpers."""

import psycopg
from psycopg.rows import dict_row

from weather_pipeline import config


def get_connection() -> psycopg.Connection:
    """Open a connection to the weather database. Rows are returned as dicts."""
    return psycopg.connect(
        host=config.POSTGRES_HOST,
        port=config.POSTGRES_PORT,
        user=config.POSTGRES_USER,
        password=config.POSTGRES_PASSWORD,
        dbname=config.POSTGRES_DB,
        row_factory=dict_row,
    )


def get_city(conn: psycopg.Connection, city_name: str, country: str) -> dict:
    """Return the cities row for one city, or raise if it doesn't exist."""
    row = conn.execute(
        """
        SELECT city_id, city_name, country, latitude, longitude, timezone
        FROM cities
        WHERE city_name = %s AND country = %s
        """,
        (city_name, country),
    ).fetchone()

    if row is None:
        raise LookupError(f"City not found in cities table: {city_name}, {country}")
    return row


def get_active_cities(conn: psycopg.Connection) -> list[dict]:
    """Return every city with is_active = TRUE, ordered by city_id."""
    return conn.execute(
        """
        SELECT city_id, city_name, country, latitude, longitude, timezone
        FROM cities
        WHERE is_active
        ORDER BY city_id
        """
    ).fetchall()
