# Quantaco Assessment

Technical assessment

## [assessment1/](assessment1/) -- API processing

**Problem:** *"Create an API stack to facilitate a pipeline to fetch Weather data from
an external API, process the data and insert it into a Database using a cloud provider
of your choice."*

**Solution:** A FastAPI service, deployed on GCP Cloud Run, that accepts a venue and
date range, fetches hourly historical weather from Open-Meteo, and upserts it into
Cloud SQL (PostgreSQL) -- with automated CI/CD (GitHub → Cloud Build → Cloud Run),
an OpenAPI spec, and SQL QA checks on the output data.

See [assessment1/README.md](assessment1/README.md) for the live demo link, architecture,
setup, and full details.

## [assessment2/](assessment2/) -- Large file processing

**Problem:** *"Please chunk the nested JSON large data file (100 MB) so that the file
chunks can then be processed and loaded in a fast way."*

**Solution:** A Python script that streams a large, deeply-nested JSON file (the real
file provided is ~4GB) one record at a time via `ijson`, writing each into its own
independent, valid JSON chunk -- without ever loading the full file into memory.

See [assessment2/README.md](assessment2/README.md) for the approach, verified results,
and full details.
