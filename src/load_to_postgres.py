from __future__ import annotations

import os
from pathlib import Path
from datetime import datetime, timezone
import logging

import pandas as pd
from pandas.api.types import (
    is_integer_dtype,
    is_float_dtype,
    is_datetime64_any_dtype,
    is_bool_dtype,
)
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

from logging_config import setup_logging


RAW_SCHEMA = "raw"
RAW_TABLE = "weather_forecast"

setup_logging()
logger = logging.getLogger(__name__)


def get_engine() -> Engine:
    db_url = os.getenv("POSTGRES_DBT_URL") or os.getenv("DATABASE_URL")

    if not db_url:
        logger.error("Missing database connection environment variable")
        raise ValueError("Missing POSTGRES_DBT_URL or DATABASE_URL environment variable")

    logger.info("Creating database engine")
    return create_engine(db_url)


def parse_source_file_ts(file_name: str) -> datetime:
    stem = Path(file_name).stem

    if not stem.startswith("output_"):
        raise ValueError(f"Unexpected file name format: {file_name}")

    ts_part = stem.replace("output_", "", 1)
    return datetime.strptime(ts_part, "%Y%m%d_%H%M%S")


def file_already_loaded(engine: Engine, source_file_name: str) -> bool:
    logger.info("Checking if file was already loaded: %s", source_file_name)

    query = text(
        f"""
        SELECT 1
        FROM {RAW_SCHEMA}.{RAW_TABLE}
        WHERE source_file_name = :source_file_name
        LIMIT 1
        """
    )

    with engine.connect() as conn:
        result = conn.execute(query, {"source_file_name": source_file_name}).first()

    already_loaded = result is not None
    logger.info("File already loaded: %s", already_loaded)

    return already_loaded


def normalize_weather_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    logger.info(
        "Normalizing dataframe with %s rows and %s columns",
        len(df),
        len(df.columns),
    )

    expected_columns = [
        "dt",
        "pop",
        "dt_txt",
        "visibility",
        "sys_pod",
        "main_temp",
        "main_temp_kf",
        "main_humidity",
        "main_pressure",
        "main_temp_max",
        "main_temp_min",
        "main_sea_level",
        "main_feels_like",
        "main_grnd_level",
        "wind_deg",
        "wind_gust",
        "wind_speed",
        "clouds_all",
        "rain_3h",
        "snow_3h",
        "weather_id",
        "weather_icon",
        "weather_main",
        "weather_description",
        "city_id",
        "city_name",
        "city_sunset",
        "city_country",
        "city_sunrise",
        "city_timezone",
        "city_population",
        "city_coord_lat",
        "city_coord_lon",
    ]

    missing = [col for col in expected_columns if col not in df.columns]

    if missing:
        logger.error("Missing required columns: %s", missing)
        raise ValueError(f"Missing required columns: {missing}")

    numeric_columns = [
        "pop",
        "main_temp",
        "main_temp_kf",
        "main_temp_max",
        "main_temp_min",
        "main_feels_like",
        "wind_gust",
        "wind_speed",
        "rain_3h",
        "snow_3h",
        "city_coord_lat",
        "city_coord_lon",
    ]

    integer_columns = [
        "dt",
        "visibility",
        "main_humidity",
        "main_pressure",
        "main_sea_level",
        "main_grnd_level",
        "wind_deg",
        "clouds_all",
        "weather_id",
        "city_id",
        "city_sunset",
        "city_sunrise",
        "city_timezone",
        "city_population",
    ]

    text_columns = [
        "sys_pod",
        "weather_icon",
        "weather_main",
        "weather_description",
        "city_name",
        "city_country",
    ]

    for col in numeric_columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    for col in integer_columns:
        df[col] = pd.to_numeric(df[col], errors="coerce").astype("Int64")

    df["dt_txt"] = pd.to_datetime(df["dt_txt"], errors="coerce")

    for col in text_columns:
        df[col] = df[col].astype("string").str.strip()

    logger.info("Dataframe normalization complete")
    return df


def infer_postgres_type(series: pd.Series) -> str:
    if is_integer_dtype(series):
        return "BIGINT"

    if is_float_dtype(series):
        return "DOUBLE PRECISION"

    if is_datetime64_any_dtype(series):
        return "TIMESTAMP"

    if is_bool_dtype(series):
        return "BOOLEAN"

    return "TEXT"


def add_missing_columns(
    engine: Engine,
    schema: str,
    table: str,
    df: pd.DataFrame,
) -> None:
    logger.info("Checking for missing columns on %s.%s", schema, table)

    with engine.begin() as conn:
        db_cols = pd.read_sql(
            text(
                """
                SELECT column_name
                FROM information_schema.columns
                WHERE table_schema = :schema
                  AND table_name = :table
                """
            ),
            conn,
            params={"schema": schema, "table": table},
        )["column_name"].tolist()

        missing_cols = sorted(set(df.columns) - set(db_cols))

        if not missing_cols:
            logger.info("No missing columns found")
            return

        logger.warning("Missing columns found: %s", missing_cols)

        for col in missing_cols:
            sql_type = infer_postgres_type(df[col])

            conn.execute(
                text(
                    f'ALTER TABLE "{schema}"."{table}" '
                    f'ADD COLUMN IF NOT EXISTS "{col}" {sql_type}'
                )
            )

            logger.info("Added missing column: %s %s", col, sql_type)


def load_weather_csv_to_raw_table(
    file_path: str,
    dag_run_id: str | None = None,
    skip_if_loaded: bool = True,
) -> str:
    logger.info("Starting raw table load")
    logger.info("Input file path: %s", file_path)
    logger.info("DAG run ID: %s", dag_run_id)

    path = Path(file_path)

    if not path.exists():
        logger.error("File not found: %s", file_path)
        raise FileNotFoundError(f"File not found: {file_path}")

    engine = get_engine()
    source_file_name = path.name
    source_file_ts = parse_source_file_ts(source_file_name)

    logger.info("Source file name: %s", source_file_name)
    logger.info("Source file timestamp: %s", source_file_ts)

    if skip_if_loaded and file_already_loaded(engine, source_file_name):
        message = f"Skipped already loaded file: {source_file_name}"
        logger.warning(message)
        return message

    logger.info("Reading CSV")
    df = pd.read_csv(path)
    logger.info("Rows read from CSV: %s", len(df))

    df = normalize_weather_dataframe(df)

    df["source_file_name"] = source_file_name
    df["source_file_ts"] = source_file_ts
    df["ingested_at"] = datetime.now(timezone.utc).replace(tzinfo=None)
    df["dag_run_id"] = dag_run_id

    add_missing_columns(
        engine=engine,
        schema=RAW_SCHEMA,
        table=RAW_TABLE,
        df=df,
    )

    logger.info("Writing rows to %s.%s", RAW_SCHEMA, RAW_TABLE)

    df.to_sql(
        name=RAW_TABLE,
        con=engine,
        schema=RAW_SCHEMA,
        if_exists="append",
        index=False,
        method="multi",
        chunksize=1000,
    )

    message = f"Loaded {len(df)} rows from {source_file_name} into {RAW_SCHEMA}.{RAW_TABLE}"
    logger.info(message)

    return message


if __name__ == "__main__":
    import argparse

    logger.info("load_to_postgres.py started from CLI")

    parser = argparse.ArgumentParser()
    parser.add_argument("--file-path", required=True)
    parser.add_argument("--dag-run-id", required=False, default=None)

    args = parser.parse_args()

    result = load_weather_csv_to_raw_table(
        file_path=args.file_path,
        dag_run_id=args.dag_run_id,
    )

    logger.info("Result: %s", result)
    print(result)