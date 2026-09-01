"""Client for the Open-Meteo Historical Forecast API.

Docs: https://open-meteo.com/en/docs/historical-forecast-api
"""

import logging
from datetime import date

import requests

from schemas import AppError

logger = logging.getLogger(__name__)

BASE_URL = "https://historical-forecast-api.open-meteo.com/v1/forecast"
REQUEST_TIMEOUT_SECONDS = 30

HOURLY_VARIABLES = (
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


def fetch_hourly_weather(
    latitude: float, longitude: float, start_date: date, end_date: date
) -> list[dict]:
    """Fetch hourly weather for the date range and return one dict per hour,
    each keyed by 'datetime' plus the HOURLY_VARIABLES fields.

    Raises AppError(502, "WEATHER_API_ERROR", ...) on any network failure,
    non-2xx response, or a response missing the expected 'hourly' shape.
    """
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
        "hourly": ",".join(HOURLY_VARIABLES),
        "timezone": "UTC",
    }

    try:
        response = requests.get(BASE_URL, params=params, timeout=REQUEST_TIMEOUT_SECONDS)
        response.raise_for_status()
        payload = response.json()
    except requests.RequestException as exc:
        logger.exception("Open-Meteo request failed (lat=%s, lon=%s)", latitude, longitude)
        raise AppError(502, "WEATHER_API_ERROR", "Failed to reach the weather data provider") from exc
    except ValueError as exc:
        logger.exception("Open-Meteo returned a non-JSON response (lat=%s, lon=%s)", latitude, longitude)
        raise AppError(502, "WEATHER_API_ERROR", "Weather data provider returned an unexpected response") from exc

    hourly = payload.get("hourly")
    times = hourly.get("time") if hourly else None
    if not hourly or not times:
        logger.error("Open-Meteo response missing hourly data: %r", payload)
        raise AppError(502, "WEATHER_API_ERROR", "Weather data provider returned an unexpected response")

    records = []
    for i, timestamp in enumerate(times):
        record = {"datetime": timestamp}
        for var in HOURLY_VARIABLES:
            series = hourly.get(var)
            record[var] = series[i] if series is not None else None
        records.append(record)
    return records
