"""Raw SQL queries. Schema is defined in sql/schema.sql (no ORM)."""

import psycopg2.extensions
from psycopg2.extras import RealDictCursor, execute_values

WEATHER_METRIC_COLUMNS = (
    "temperature_2m",
    "relative_humidity_2m",
    "dewpoint_2m",
    "apparent_temperature",
    "precipitation_probability",
    "precipitation",
    "rain",
    "showers",
    "snowfall",
    "snow_depth",
)

_INSERT_COLUMNS = ("venue_id", "datetime", *WEATHER_METRIC_COLUMNS)

_UPSERT_SQL = f"""
    INSERT INTO weather ({", ".join(_INSERT_COLUMNS)})
    VALUES %s
    ON CONFLICT (venue_id, datetime) DO UPDATE SET
        {", ".join(f"{col} = EXCLUDED.{col}" for col in WEATHER_METRIC_COLUMNS)},
        updated_at = now()
"""


def get_venue(conn: psycopg2.extensions.connection, venue_id: int) -> dict | None:
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(
            "SELECT id, name, latitude, longitude FROM venue WHERE id = %s",
            (venue_id,),
        )
        row = cur.fetchone()
        return dict(row) if row else None


def upsert_weather_records(
    conn: psycopg2.extensions.connection, venue_id: int, records: list[dict]
) -> int:
    """Upsert one row per hourly record. Returns the number of records applied.

    Each input record maps 1:1 to an inserted or updated row (never both),
    so len(records) is the accurate "records_saved" count — no need to trust
    cursor.rowcount, which only reflects the last page under execute_values'
    internal batching.
    """
    if not records:
        return 0

    values = [
        (venue_id, r["datetime"], *(r.get(col) for col in WEATHER_METRIC_COLUMNS))
        for r in records
    ]

    with conn.cursor() as cur:
        execute_values(cur, _UPSERT_SQL, values)
    conn.commit()
    return len(records)
