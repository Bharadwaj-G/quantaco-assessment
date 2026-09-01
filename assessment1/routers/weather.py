"""POST /weather, GET /weather — route defs + request-level validation."""

import logging
from datetime import date

import psycopg2
from fastapi import APIRouter, Depends, Query

import crud
from database import get_db
from integrations.open_meteo import fetch_hourly_weather
from schemas import (
    AppError,
    WeatherListResponse,
    WeatherRecord,
    WeatherRequest,
    WeatherSuccessResponse,
    MAX_RANGE_DAYS,
)

logger = logging.getLogger(__name__)

router = APIRouter(tags=["weather"])


def _validate_date_range(start_date: date, end_date: date) -> None:
    if start_date > end_date:
        raise AppError(
            400, "INVALID_DATE_RANGE", "start_date must be on or before end_date"
        )
    if (end_date - start_date).days > MAX_RANGE_DAYS:
        raise AppError(
            400, "INVALID_DATE_RANGE", f"date range cannot exceed {MAX_RANGE_DAYS} days"
        )


def _get_venue_or_404(conn, venue_id: int) -> dict:
    venue = crud.get_venue(conn, venue_id)
    if venue is None:
        raise AppError(404, "VENUE_NOT_FOUND", f"Venue with id {venue_id} does not exist")
    return venue


@router.post("/weather", response_model=WeatherSuccessResponse)
def post_weather(request: WeatherRequest, conn=Depends(get_db)) -> WeatherSuccessResponse:
    _validate_date_range(request.start_date, request.end_date)
    venue = _get_venue_or_404(conn, request.venue_id)

    records = fetch_hourly_weather(
        latitude=venue["latitude"],
        longitude=venue["longitude"],
        start_date=request.start_date,
        end_date=request.end_date,
    )

    try:
        records_saved = crud.upsert_weather_records(conn, request.venue_id, records)
    except psycopg2.Error as exc:
        conn.rollback()
        logger.exception("Failed to save weather data for venue_id=%s", request.venue_id)
        raise AppError(500, "DATABASE_ERROR", "Failed to save weather data") from exc

    logger.info(
        "Saved %d weather records for venue_id=%s (%s to %s)",
        records_saved, request.venue_id, request.start_date, request.end_date,
    )
    return WeatherSuccessResponse(
        venue_id=request.venue_id,
        start_date=request.start_date,
        end_date=request.end_date,
        records_saved=records_saved,
    )


@router.get("/weather", response_model=WeatherListResponse)
def get_weather(
    venue_id: int = Query(...),
    start_date: date = Query(...),
    end_date: date = Query(...),
    conn=Depends(get_db),
) -> WeatherListResponse:
    _validate_date_range(start_date, end_date)
    _get_venue_or_404(conn, venue_id)

    try:
        rows = crud.get_weather_records(conn, venue_id, start_date, end_date)
    except psycopg2.Error as exc:
        logger.exception("Failed to read weather data for venue_id=%s", venue_id)
        raise AppError(500, "DATABASE_ERROR", "Failed to read weather data") from exc

    records = [WeatherRecord(**{**row, "datetime": str(row["datetime"])}) for row in rows]
    return WeatherListResponse(
        venue_id=venue_id,
        start_date=start_date,
        end_date=end_date,
        count=len(records),
        records=records,
    )
