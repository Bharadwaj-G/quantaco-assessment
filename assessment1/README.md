# Quantaco Weather API

Fetches hourly historical weather (Open-Meteo) for a venue over a date range and
saves it into Postgres. See `POST /weather` and `GET /weather` below.

## Architecture

- **Runtime**: Cloud Run (containerized FastAPI, sync)
- **Database**: Cloud SQL for PostgreSQL, raw SQL via `psycopg2` (no ORM)
- **DB connectivity**: no client library needed — Cloud Run's built-in
  `--add-cloudsql-instances` flag mounts a Unix socket to the instance in
  production; locally, the [Cloud SQL Auth Proxy](https://cloud.google.com/sql/docs/postgres/sql-proxy)
  opens the same kind of tunnel over a local TCP port. Same `psycopg2.connect(...)`
  call either way — see `database.py`.
- **CI/CD**: Cloud Build, triggered from this GitHub repo

## Prerequisites

- Python 3.11+
- A Cloud SQL for PostgreSQL instance (see "GCP setup" below)
- The [Cloud SQL Auth Proxy](https://cloud.google.com/sql/docs/postgres/connect-auth-proxy#install) binary, for local testing only
- A GCP service account with the **Cloud SQL Client** role, JSON key downloaded
  (Console: IAM & Admin → Service Accounts → Create → grant role → Keys → Add Key)

## Local setup & testing

1. **Create a virtualenv and install dependencies**
   ```bash
   python -m venv .venv
   source .venv/Scripts/activate   # Windows Git Bash; use .venv\Scripts\Activate.ps1 in PowerShell
   pip install -r requirements.txt
   ```

2. **Configure environment**
   ```bash
   cp .env.example .env
   ```
   Fill in `DB_USER`, `DB_PASS`, `DB_NAME` to match what you set up on the Cloud SQL
   instance, and `INSTANCE_CONNECTION_NAME` (format `PROJECT_ID:REGION:INSTANCE_NAME`,
   shown on the instance's Overview page in the Console).

3. **Start the Cloud SQL Auth Proxy** (separate terminal, keep it running)
   ```bash
   ./cloud-sql-proxy --credentials-file=key.json --port 5432 PROJECT_ID:REGION:INSTANCE_NAME
   ```
   This opens `127.0.0.1:5432`, tunneled to your real Cloud SQL instance.

4. **Apply the schema + seed data** (one-time, or after schema changes)
   ```bash
   python sql/apply_schema.py
   ```

5. **Run the API**
   ```bash
   uvicorn main:app --reload --port 8000
   ```

6. **Test it**

   Success case:
   ```bash
   curl -X POST http://localhost:8000/weather \
     -H "Content-Type: application/json" \
     -d '{"venue_id": 1, "start_date": "2024-01-01", "end_date": "2024-01-07"}'
   ```
   Expected: `200` with `{"status": "success", "records_saved": 168, ...}`

   Verify saved rows:
   ```bash
   curl "http://localhost:8000/weather?venue_id=1&start_date=2024-01-01&end_date=2024-01-07"
   ```

   Error cases:
   ```bash
   # Unknown venue -> 404 VENUE_NOT_FOUND
   curl -X POST http://localhost:8000/weather -H "Content-Type: application/json" \
     -d '{"venue_id": 99, "start_date": "2024-01-01", "end_date": "2024-01-07"}'

   # start_date after end_date -> 400 INVALID_DATE_RANGE
   curl -X POST http://localhost:8000/weather -H "Content-Type: application/json" \
     -d '{"venue_id": 1, "start_date": "2024-01-07", "end_date": "2024-01-01"}'

   # Missing field -> 422 VALIDATION_ERROR
   curl -X POST http://localhost:8000/weather -H "Content-Type: application/json" \
     -d '{"venue_id": 1, "start_date": "2024-01-01"}'
   ```

   Or import the OpenAPI spec (auto-generated at `http://localhost:8000/openapi.json`,
   interactive docs at `http://localhost:8000/docs`) into Postman directly.

## GCP setup

_To be filled in as the Cloud SQL instance / Cloud Run service / Cloud Build trigger
are provisioned via the Console._

## Running with Docker

```bash
docker build -t quantaco-weather-api .
docker run --env-file .env -p 8080:8080 quantaco-weather-api
```
(Requires the Auth Proxy reachable from inside the container — for local Docker
testing, run the proxy with `--address 0.0.0.0` and point `DB_HOST` at your host
machine's address, e.g. `host.docker.internal` on Windows/Mac.)

## SQL QA checks

See `sql/qa_checks.sql`.
