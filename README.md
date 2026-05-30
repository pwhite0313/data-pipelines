# Weather Data Pipeline

An end-to-end data engineering pipeline that ingests, transforms, and stores weather forecast data from the OpenWeatherMap API. Orchestrated with Apache Airflow, containerized with Docker, and transformed with dbt. Tracks 15 cities across North America, Europe, Asia, and Australia.

---

## Architecture

```
OpenWeatherMap API
        |
   Extract (Python)
        |
   Transform (Python)
        |
   Load to CSV (data/raw/)
        |
   Load to PostgreSQL (raw.weather_forecast)
        |
   Validate row count
        |
   dbt staging (staging.stg_weather__forecast)
        |
   dbt mart (analytics.fct_weather_forecast)
```

---

## Tech Stack

- Python 3.x
- Apache Airflow (Docker)
- PostgreSQL
- dbt (dbt-postgres)
- Docker / Docker Compose
- pandas, SQLAlchemy, psycopg2
- pytest

---

## Repository Structure

```
weather_pipeline/
├── dags/
│   └── weather_forecast_pipeline.py  # Airflow DAG: extract → transform → load CSV → load Postgres → validate → dbt
├── data/
│   ├── raw/                           # CSV output files from each DAG run
│   └── processed/
├── dbt/
│   ├── models/
│   │   ├── staging/weather/
│   │   │   ├── stg_weather__forecast.sql
│   │   │   ├── schema.yml             # Column docs and dbt tests
│   │   │   └── weather_sources.yml
│   │   └── marts/
│   │       ├── fct_weather_forecast.sql
│   │       └── schema.yml
│   ├── macros/
│   │   └── generate_schema_name.sql   # Prevents dbt from prepending target schema
│   ├── profiles.yml
│   ├── dbt_project.yml
│   └── packages.yml
├── tests/
│   └── test_transform.py              # pytest unit tests for transform logic
├── src/
│   ├── client.py                      # OpenWeatherMap API client
│   ├── extract.py                     # Calls API and returns raw records
│   ├── transform.py                   # Cleans and flattens records
│   ├── load.py                        # Writes records to CSV
│   ├── postgres_loader.py             # Loads CSVs into raw.weather_forecast
│   ├── main.py                        # CLI entrypoint (runs full pipeline locally)
│   ├── logging_config.py
│   └── utils.py
├── docs/
│   └── lineage.png                    # dbt lineage graph
├── config/
│   └── airflow.cfg
├── docker-compose.yml
├── Dockerfile
├── requirements.txt                   # Pipeline dependencies
├── requirements-airflow.txt           # Airflow dependencies
└── .env                               # Local environment variables (not committed)
```

---

## Database Schema

### raw.weather_forecast
Loaded directly from CSV files by Airflow. Includes all raw API fields plus pipeline metadata:

| Column | Type | Description |
|---|---|---|
| dt | bigint | Forecast Unix timestamp |
| dt_txt | text | Forecast timestamp as text |
| main_temp | numeric | Temperature (°F) |
| main_feels_like | numeric | Feels-like temperature |
| main_temp_min / max | numeric | Min/max temperature |
| main_humidity | bigint | Humidity % |
| main_pressure | bigint | Atmospheric pressure |
| wind_speed | numeric | Wind speed |
| wind_deg | bigint | Wind direction (degrees) |
| wind_gust | numeric | Wind gust speed |
| rain_3h | numeric | Rain volume (last 3 hours) |
| snow_3h | numeric | Snow volume (last 3 hours) — optional, null when no snow |
| clouds_all | bigint | Cloud coverage % |
| visibility | bigint | Visibility distance |
| pop | numeric | Probability of precipitation (0-1) |
| weather_main | text | High-level condition (Rain, Clouds, etc.) |
| weather_description | text | Detailed condition |
| city_id | bigint | City identifier |
| city_name | text | City name |
| city_country | text | Country code |
| city_population | bigint | City population |
| city_timezone | bigint | UTC offset in seconds |
| city_sunrise / sunset | bigint | Sunrise/sunset Unix timestamps |
| city_coord_lat / lon | numeric | Coordinates |
| source_file_name | text | Source CSV filename |
| source_file_ts | timestamp | Timestamp parsed from filename |
| ingested_at | timestamp | UTC time of ingestion |
| dag_run_id | text | Airflow DAG run ID |

### staging.stg_weather__forecast
dbt staging model. Casts all columns to correct types, normalizes timestamps to UTC, trims strings, and deduplicates by keeping the most recent ingestion for each `city_id` + `dt_utc` combination.

### analytics.fct_weather_forecast
dbt mart. Selects the key analytical columns for downstream consumption:
`local_dt`, `city_name`, `city_country`, `city_id`, `main_temp`, `main_temp_min`, `main_temp_max`, `main_feels_like`, `main_humidity`, `clouds_all`, `rain_3h`, `snow_3h`, `wind_speed`, `wind_gust`, `weather_main`, `weather_description`, `weather_id`

---

## Sample Output (raw CSV)

```
dt,visibility,pop,dt_txt,main_temp,main_feels_like,main_humidity,wind_speed,city_name,city_country,weather_main,...
1778284800,10000,0.2,2026-05-09 00:00:00,60.51,58.57,49,7.07,New York,US,Rain,...
1778295600,10000,0.0,2026-05-09 03:00:00,58.73,56.93,56,5.03,New York,US,Clouds,...
```

---

## Setup

### Prerequisites
- Docker and Docker Compose
- OpenWeatherMap API key

### Environment Variables

Create a `.env` file in the project root:

```
OPENWEATHER_API_KEY=your_api_key_here
WAREHOUSE_USER=weather_user
WAREHOUSE_PASSWORD=weather_pass
WAREHOUSE_DB=weather_db
WAREHOUSE_HOST=postgres-warehouse
WAREHOUSE_PORT=5432
```

### Start Airflow

```bash
docker compose up
```

Airflow UI available at `http://localhost:8080` (admin / admin).
The warehouse Postgres is available at `localhost:5432`.

---

## Running the Pipeline

### Via Airflow (recommended)

Trigger the DAG from the UI or CLI:

```bash
docker compose exec airflow-scheduler airflow dags trigger weather_forecast_pipeline
```

### Via CLI (local, no Docker)

```bash
source venv/bin/activate
python -m src.main
```

### Backfill existing CSV files

```bash
docker compose exec airflow-scheduler bash -c "
  for f in /opt/airflow/data/raw/output_*.csv; do
    python -m src.postgres_loader file --file-path \"\$f\"
  done
"
```

---

## dbt

dbt runs automatically as part of the Airflow DAG. To run manually:

```bash
source venv/bin/activate
cd dbt
dbt run
dbt test
```

### Lineage

![dbt lineage graph](docs/lineage.png)

`raw.weather_forecast` → `stg_weather__forecast` → `fct_weather_forecast`

To regenerate docs:

```bash
docker compose exec airflow-scheduler bash -c "cd /opt/airflow/dbt && dbt docs generate --profiles-dir /opt/airflow/dbt"
```

---

## Testing

Unit tests cover the transform layer using pytest:

```bash
source venv/bin/activate
python -m pytest tests/ -v
```

Tests validate `validate_response` (input shape, missing fields, wrong types) and `transform_records` (output schema, row count, city broadcast, bad date handling, weather field flattening).

---

## Failure Handling

The pipeline is designed to fail loudly at the point of failure rather than pass bad data downstream.

**API or network failure** — the `extract` task raises an exception if the API call fails or returns an unexpected response. Airflow retries the task twice with a 5-minute delay before marking the DAG run as failed.

**Schema validation failure** — the `transform` task validates the structure of the API response before processing. If required fields (`list`, `city`) are missing or malformed, the task fails immediately and downstream tasks do not run.

**Data quality failure** — the `dbt_test` task runs after `dbt_run` and enforces contracts on the staging model including uniqueness, not-null checks, range validation, and freshness. If any test fails, the DAG fails at `dbt_test` and the mart is not updated. This was observed in practice when overlapping forecast data caused a uniqueness violation, which was resolved by deduplicating in the staging model using rank.

---

## Engineering Considerations

- Idempotent loads — `skip_if_loaded` prevents duplicate ingestion of the same CSV file
- Schema auto-creation — `ensure_raw_schema` creates the `raw` schema on first run
- Metadata columns on every row — source file, ingestion timestamp, DAG run ID for full lineage
- dbt tests enforce data quality — uniqueness, not-null, range checks, accepted values
- Two isolated Postgres instances — Airflow metadata separate from the data warehouse
- CSV landing zone — raw files preserved on disk so data survives database resets and enables reprocessing
- Staging deduplication — overlapping forecast windows across DAG runs are resolved in the staging model using `ROW_NUMBER()`, keeping the most recent ingestion per forecast timestamp per city
- Incremental fact model — `fct_weather_forecast` uses a `NOT EXISTS` anti-join on `(city_id, local_dt)` so new cities are picked up correctly without re-processing existing rows; adding a new city requires a one-time `dbt run --full-refresh --select fct_weather_forecast`
- Schema separation — staging and analytics models write to isolated schemas via a custom `generate_schema_name` macro, preventing dbt's default behavior of prepending the target schema name

---

## Known Limitations

**Schema drift from optional API fields** — the `raw.weather_forecast` table schema is inferred from the first CSV loaded via pandas `to_sql`. The OpenWeatherMap API returns optional fields only when relevant (e.g., `snow_3h` only appears when snow is forecasted). If a new city is added and its first forecast contains a field not present in the original CSV, the load task will fail with:

```
psycopg2.errors.UndefinedColumn: column "snow_3h" of relation "weather_forecast" does not exist
```

**Fix:** run the appropriate `ALTER TABLE` in the warehouse to add the missing column:

```sql
ALTER TABLE raw.weather_forecast ADD COLUMN snow_3h numeric;
```

This was encountered in practice when adding cities like Denver and Toronto, which returned `snow_3h` data not present in the original New York / Chicago load. At production scale this pattern would be handled with explicit schema definitions (e.g., a migration tool like Alembic) or by enforcing a fixed schema at ingest time rather than inferring it from the data.
