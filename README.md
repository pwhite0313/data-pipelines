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
   Volume anomaly check (7-run rolling average)
        |
   dbt source freshness
        |
   dbt staging      → staging.stg_weather__forecast
        |
   dbt intermediate → intermediate.int_weather_enriched
        |
   dbt marts        → analytics.dim_city
                    → analytics.fct_weather_forecast  (incremental)
                    → analytics.fct_weather_daily
        |
   dbt reports      → reports.rpt_current_conditions
        |
   dbt test
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
- GitHub Actions (CI)

---

## Repository Structure

```
weather_pipeline/
├── .github/
│   └── workflows/
│       └── ci.yml                     # GitHub Actions: pytest on push
├── dags/
│   └── weather_forecast_pipeline.py   # Airflow DAG definition
├── data/
│   ├── raw/                           # CSV output files from each DAG run
│   └── processed/
├── dbt/
│   ├── models/
│   │   ├── staging/weather/
│   │   │   ├── stg_weather__forecast.sql
│   │   │   ├── schema.yml
│   │   │   └── weather_sources.yml
│   │   ├── intermediate/
│   │   │   └── int_weather_enriched.sql   # Temp, wind, and precip categories
│   │   ├── marts/
│   │   │   ├── dim_city.sql               # City dimension
│   │   │   ├── fct_weather_forecast.sql   # Incremental 3-hour forecast fact
│   │   │   ├── fct_weather_daily.sql      # Daily aggregate fact
│   │   │   └── schema.yml
│   │   └── reports/
│   │       └── rpt_current_conditions.sql # Latest forecast per city
│   ├── macros/
│   │   └── generate_schema_name.sql       # Prevents dbt from prepending target schema
│   ├── profiles.yml                       # dev and prod targets
│   ├── dbt_project.yml
│   └── packages.yml
├── tests/
│   ├── conftest.py                    # Shared pytest fixtures
│   ├── test_transform.py              # Transform logic unit tests
│   └── test_postgres_loader.py        # postgres_loader unit tests
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

### intermediate.int_weather_enriched
Adds derived categorical columns on top of the staging model: `temp_category` (freezing / cold / mild / warm / hot), `wind_category` (calm / light / moderate / strong / storm), and `precip_type` (none / rain / snow / rain_and_snow).

### analytics.dim_city
City dimension table. One row per city, deduplicated using `ROW_NUMBER()` ordered by most recent forecast.

### analytics.fct_weather_forecast
Incremental 3-hour forecast fact table. Uses a `NOT EXISTS` anti-join on `(city_id, local_dt)` so new cities are ingested correctly without reprocessing existing rows.
Columns: `local_dt`, `city_name`, `city_country`, `city_id`, `main_temp`, `main_temp_min`, `main_temp_max`, `main_feels_like`, `main_humidity`, `clouds_all`, `rain_3h`, `snow_3h`, `wind_speed`, `wind_gust`, `weather_main`, `weather_description`, `weather_id`

### analytics.fct_weather_daily
Daily aggregate fact. Rolls up the 3-hour forecasts to one row per `city_id` + calendar date: avg/min/max temp, avg humidity, avg wind speed, total rain and snow.

### reports.rpt_current_conditions
Reporting view. Returns the single most-recent forecast per city joined to all enriched columns from `int_weather_enriched`. Ready for BI tool consumption.

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

### Create the Airflow Connection

After the containers are healthy, register the warehouse connection so Airflow can resolve credentials at runtime:

```bash
docker compose exec airflow-scheduler airflow connections add weather_warehouse \
    --conn-type postgres \
    --conn-host postgres-warehouse \
    --conn-login weather_user \
    --conn-password weather_pass \
    --conn-schema weather_db \
    --conn-port 5432
```

The `postgres_loader.py` module tries this connection first and falls back to the `.env` environment variables if the connection is not found — so the pipeline still works locally without Docker.

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

### Target switching (dev / prod)

The `DBT_TARGET` environment variable controls which `profiles.yml` target is used. It defaults to `dev`. Set `DBT_TARGET=prod` in the Airflow environment (or CI) to run against the production warehouse.

### Lineage

![dbt lineage graph](docs/lineage.png)

`raw.weather_forecast` → `stg_weather__forecast` → `int_weather_enriched` → `fct_weather_forecast` / `fct_weather_daily` / `rpt_current_conditions`

To regenerate docs:

```bash
docker compose exec airflow-scheduler bash -c "cd /opt/airflow/dbt && dbt docs generate --profiles-dir /opt/airflow/dbt"
```

---

## Testing

```bash
source venv/bin/activate
python -m pytest tests/ -v
```

Tests are split across two files:

- `test_transform.py` — validates `validate_response` (input shape, missing fields, wrong types) and `transform_records` (output schema, row count, city broadcast, bad date handling, weather field flattening)
- `test_postgres_loader.py` — validates `parse_source_file_ts` (valid filename, date/time parsing, full path, missing prefix, malformed timestamp)

Shared fixtures live in `conftest.py`. The CI workflow in `.github/workflows/ci.yml` runs the full suite on every push and pull request to master.

---

## Failure Handling

The pipeline is designed to fail loudly at the point of failure rather than pass bad data downstream.

**API or network failure** — the `extract` task raises an exception if the API call fails or returns an unexpected response. Airflow retries the task twice with a 5-minute delay before marking the DAG run as failed.

To simulate: set `OPENWEATHER_API_KEY=invalid` in `.env`, restart the containers, and trigger the DAG. The `extract` task will fail with a non-200 response error. Downstream tasks do not run.

**Schema validation failure** — the `transform` task validates the structure of the API response before processing. If required fields (`list`, `city`) are missing or malformed, the task fails immediately and downstream tasks do not run.

To simulate: temporarily add `del data[0]["city"]` in `transform.py` before `validate_response` is called. The `transform` task will raise a `ValueError` with a clear message identifying the missing field.

**Volume anomaly failure** — the `volume_anomaly_check` task compares the current run's row count against a 7-run rolling average. If the current run loads more than 50% fewer rows than the rolling average, the DAG fails before dbt runs. The error message includes the `dag_run_id` so the anomalous run can be identified and inspected in the warehouse.

To simulate: temporarily set the threshold to 110% (`rolling_avg * 1.1`) and trigger the DAG. It will fail at `volume_anomaly_check` with a clear message including the run ID. Restore to `rolling_avg * 0.5` after verifying.

**Data quality failure** — the `dbt_test` task runs after `dbt_run` and enforces contracts on the staging model including uniqueness, not-null checks, range validation, and freshness. If any test fails, the DAG fails at `dbt_test` and the mart is not updated.

To simulate: run `UPDATE raw.weather_forecast SET weather_id = NULL WHERE city_id = 5128581 LIMIT 1;` in the warehouse, then trigger the DAG. The `dbt_test` task will fail on the `not_null` test for `weather_id`. Restore with `UPDATE raw.weather_forecast SET weather_id = 500 WHERE weather_id IS NULL;`.

This was observed in practice when overlapping forecast data caused a uniqueness violation, which was resolved by deduplicating in the staging model using `ROW_NUMBER()`.

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

**Schema drift from new or optional API fields** — the `raw.weather_forecast` table schema is inferred from the first CSV loaded via pandas `to_sql`. When the OpenWeatherMap API returns a field not present in the original table (e.g., `snow_3h` when snow is first forecasted, or a newly added field like `main_dew_point`), the load task would previously fail with:

```
psycopg2.errors.UndefinedColumn: column "main_dew_point" of relation "weather_forecast" does not exist
```

**Current behavior** — `postgres_loader.py` now handles this gracefully. On each load, `align_columns_to_table` queries `information_schema` to compare the DataFrame columns against the actual table columns. Any unknown columns are dropped before the insert and a warning is logged:

```
WARNING - Dropping 1 unknown column(s) not present in raw.weather_forecast: ['main_dew_point'] — run ALTER TABLE to start capturing this data
```

The pipeline does not fail. The new field is ignored until a deliberate decision is made to capture it.

**To approve a new column** — once the warning is observed in the Airflow logs, run the appropriate `ALTER TABLE` in the warehouse:

```sql
ALTER TABLE raw.weather_forecast ADD COLUMN main_dew_point numeric;
```

The next DAG run will pick up the column automatically with no code changes required. At production scale this pattern would be replaced by a migration tool like Alembic that versions schema changes as auditable migration scripts.

---

## Incident Log

### June 2026 — cascading failure from schema change and backfill

**What happened:**
3 consecutive DAG runs failed at `load_raw_table` because the OpenWeatherMap API began returning a new field (`main_dew_point`) that did not exist in `raw.weather_forecast`. The extract and transform tasks succeeded each time and CSVs were written to `data/raw/`, but the Postgres load failed before any rows were inserted.

**Fix 1 — schema:**
`ALTER TABLE raw.weather_forecast ADD COLUMN main_dew_point numeric` was run in the warehouse. `align_columns_to_table` was added to `postgres_loader.py` to handle future unknown columns gracefully rather than failing.

**Fix 2 — backfill:**
`make backfill` was run to load the 3 missed CSVs. Because `skip_if_loaded` uses the filename as the key, only the unloaded files were inserted — no duplicates.

**Second issue — null city metadata:**
The backfill also picked up older CSVs from before city columns were added to the extract logic. Those files loaded successfully but contributed 320 rows with null `city_id`, `city_name`, and related city columns.

**Caught by dbt tests:**
The `dbt_test` task failed on not-null constraints for `city_id`, preventing the mart from being updated with bad data. This was the intended behavior — the pipeline failed loudly rather than propagating nulls downstream.

**Fix 3 — data patch:**
The 320 rows were patched directly in `raw.weather_forecast` using a CTE UPDATE that sourced city values from valid rows with matching structure. The original CSVs were left untouched as the permanent record of what the API returned at that time. After patching, `dbt_run` and `dbt_test` both passed and the incremental model picked up all backfilled rows automatically.
