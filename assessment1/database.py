"""Plain psycopg2 connections to Postgres.

Two ways in which the Postgres connection is configured:
  - On Cloud Run: deploying with --add-cloudsql-instances=INSTANCE_CONNECTION_NAME
    mounts a Unix domain socket at /cloudsql/INSTANCE_CONNECTION_NAME. Set
    INSTANCE_UNIX_SOCKET to that path and psycopg2 connects to it directly
  - Locally: point DB_HOST/DB_PORT at any reachable Postgres (e.g. a local
    Docker container).

"""

import logging
import os
from collections.abc import Generator

import psycopg2
import psycopg2.extensions

from schemas import AppError

logger = logging.getLogger(__name__)


def get_connection() -> psycopg2.extensions.connection:
    common = {
        "user": os.environ["DB_USER"],
        "password": os.environ["DB_PASS"],
        "dbname": os.environ["DB_NAME"],
    }

    unix_socket = os.environ.get("INSTANCE_UNIX_SOCKET")
    if unix_socket:
        return psycopg2.connect(host=unix_socket, **common)

    return psycopg2.connect(
        host=os.environ.get("DB_HOST", "127.0.0.1"),
        port=int(os.environ.get("DB_PORT", 5432)),
        **common,
    )


def get_db() -> Generator[psycopg2.extensions.connection, None, None]:
    """FastAPI dependency — one connection per request, closed after."""
    try:
        conn = get_connection()
    except psycopg2.Error as exc:
        logger.exception("Failed to connect to the database")
        raise AppError(500, "DATABASE_ERROR", "Failed to connect to the database") from exc

    try:
        yield conn
    finally:
        conn.close()
