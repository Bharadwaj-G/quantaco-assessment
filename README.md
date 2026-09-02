# Quantaco Assessment

Technical assessment

## [assessment1/](assessment1/) — API processing

A FastAPI service that fetches hourly historical weather data from Open-Meteo for a
venue over a date range and saves it into Cloud SQL (PostgreSQL), deployed on GCP
Cloud Run. See [assessment1/README.md](assessment1/README.md).

## [assessment2/](assessment2/) — Large file processing

Streams a large, deeply-nested JSON file (~4GB) into multiple smaller chunks
without loading it fully into memory. See [assessment2/README.md](assessment2/README.md).
