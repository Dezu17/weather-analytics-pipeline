import os

import psycopg
import pytest

from weather_pipeline.db import get_connection


@pytest.fixture(scope="session")
def database_available():
    """Check once per test run, so a missing database skips quickly instead of per test.

    Set REQUIRE_DATABASE=1 (as CI does) to fail instead of skipping.
    """
    try:
        with get_connection():
            pass
    except psycopg.OperationalError as error:
        if os.getenv("REQUIRE_DATABASE") == "1":
            pytest.fail(f"Postgres not available: {error}")
        pytest.skip(f"Postgres not available: {error}")


@pytest.fixture
def conn(database_available):
    """A database connection whose changes are always rolled back after the test."""
    with get_connection() as connection, connection.transaction(force_rollback=True):
        yield connection


@pytest.fixture
def city_id(conn) -> int:
    """A throwaway city, so tests never touch real cities' weather rows."""
    return conn.execute(
        """
        INSERT INTO cities (city_name, country, latitude, longitude, timezone)
        VALUES ('Test City', 'Testland', 0, 0, 'UTC')
        RETURNING city_id
        """
    ).fetchone()["city_id"]
