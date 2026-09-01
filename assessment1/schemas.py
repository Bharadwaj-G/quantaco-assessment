"""Pydantic request/response models and the shared error envelope.

Note: start_date/end_date ORDER and RANGE checks are deliberately NOT done
here as Pydantic validators — a raised ValueError there becomes a 422 from
FastAPI's request-validation handler, but the API contract requires those
specific failures to be 400 INVALID_DATE_RANGE. They're checked explicitly
in the route handler instead. This model only enforces shape/type, which is
what should map to 422 VALIDATION_ERROR.
"""

from datetime import date

from pydantic import BaseModel

MAX_RANGE_DAYS = 365


class WeatherRequest(BaseModel):
    venue_id: int
    start_date: date
    end_date: date


class WeatherSuccessResponse(BaseModel):
    status: str = "success"
    venue_id: int
    start_date: date
    end_date: date
    records_saved: int
    message: str = "Weather data saved successfully"


class ErrorResponse(BaseModel):
    status: str = "error"
    error_code: str
    message: str


class AppError(Exception):
    """Raised by route/business logic; caught by a global handler in main.py
    and turned into the {status, error_code, message} envelope + HTTP status."""

    def __init__(self, http_status: int, error_code: str, message: str) -> None:
        self.http_status = http_status
        self.error_code = error_code
        self.message = message
        super().__init__(message)
