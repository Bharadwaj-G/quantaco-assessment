"""Plain psycopg2 connections to Postgres.

Two ways in, same driver, no Cloud SQL client library needed:
  - On Cloud Run: deploying with --add-cloudsql-instances=INSTANCE_CONNECTION_NAME
    mounts a Unix domain socket at /cloudsql/INSTANCE_CONNECTION_NAME. Set
    INSTANCE_UNIX_SOCKET to that path and psycopg2 connects to it directly —
    no IP allowlisting, auth is via the Cloud Run service account's IAM role.
  - Locally: point DB_HOST/DB_PORT at any reachable Postgres (e.g. a local
    Docker container). Same psycopg2 code path either way — only the
    connection target changes.

Required env vars: DB_USER, DB_PASS, DB_NAME, plus either
INSTANCE_UNIX_SOCKET (Cloud Run) or DB_HOST + DB_PORT (local).
"""

import os
from collections.abc import Generator

import psycopg2
import psycopg2.extensions


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
    conn = get_connection()
    try:
        yield conn
    finally:
        conn.close()
