"""FastAPI app instance: mounts routers, global exception handlers."""

import logging

from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from routers.weather import router as weather_router
from schemas import AppError, ErrorResponse

load_dotenv()  # no-op if .env doesn't exist (e.g. on Cloud Run)

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Quantaco Weather API",
    description="Fetches and stores hourly historical weather data per venue.",
    version="1.0.0",
)

app.include_router(weather_router)


@app.exception_handler(AppError)
def handle_app_error(request: Request, exc: AppError) -> JSONResponse:
    body = ErrorResponse(error_code=exc.error_code, message=exc.message)
    return JSONResponse(status_code=exc.http_status, content=body.model_dump())


@app.exception_handler(RequestValidationError)
def handle_validation_error(request: Request, exc: RequestValidationError) -> JSONResponse:
    details = "; ".join(
        f"{'.'.join(str(p) for p in err['loc'])}: {err['msg']}" for err in exc.errors()
    )
    body = ErrorResponse(error_code="VALIDATION_ERROR", message=details)
    return JSONResponse(status_code=422, content=body.model_dump())


@app.exception_handler(Exception)
def handle_unexpected_error(request: Request, exc: Exception) -> JSONResponse:
    logger.exception("Unhandled exception on %s %s", request.method, request.url.path)
    body = ErrorResponse(error_code="INTERNAL_ERROR", message="An unexpected error occurred")
    return JSONResponse(status_code=500, content=body.model_dump())


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}
