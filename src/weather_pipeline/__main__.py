"""Run extraction for one city and date range.

Example:
    python -m weather_pipeline --city Dublin --country Ireland --start 2026-10-01 --end 2026-10-07
"""

import argparse
from datetime import date

from weather_pipeline.db import get_city, get_connection
from weather_pipeline.extract import extract


def main() -> None:
    parser = argparse.ArgumentParser(description="Extract daily weather for one city.")
    parser.add_argument("--city", required=True)
    parser.add_argument("--country", required=True)
    parser.add_argument("--start", required=True, type=date.fromisoformat)
    parser.add_argument("--end", required=True, type=date.fromisoformat)
    args = parser.parse_args()

    with get_connection() as conn:
        city = get_city(conn, args.city, args.country)

    raw_path = extract(city, args.start, args.end)
    print(f"Extracted: {raw_path}")


if __name__ == "__main__":
    main()
