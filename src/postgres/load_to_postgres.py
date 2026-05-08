from __future__ import annotations

import os
from pathlib import Path
from datetime import datetime, timezone
import logging

import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

from src.logging_config import setup_logging


RAW_SCHEMA = "raw"
RAW_TABLE = "weather_forecast"

setup_logging()
logger = logging.getLogger(__name__)


def get_engine() -> Engine:
    db_url = os.getenv("POSTGRES_DBT_URL") or os.getenv("DATABASE_URL")

    if not db_url:
        user = os.getenv("WAREHOUSE_USER")
        password = os.getenv("WAREHOUSE_PASSWORD")
        host = os.getenv("WAREHOUSE_HOST")
        port = os.getenv("WAREHOUSE_PORT", "5432")
        db = os.getenv("WAREHOUSE_DB")

        if not all([user, password, host, db]):
            logger.error("Missing one or more warehouse connection environment variables")
            raise ValueError(
                "Missing one or more warehouse connection environment variables: "
                "WAREHOUSE_USER, WAREHOUSE_PASSWORD, WAREHOUSE_HOST, WAREHOUSE_DB"
            )

        db_url = f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{db}"
        logger.info("Built database URL from individual environment variables")

    logger.info("Creating database engine")
    return create_engine(db_url)


def parse_source_file_ts(file_name: str) -> datetime:
    stem = Path(file_name).stem

    if not stem.startswith("output_"):
        raise ValueError(f"Unexpected file name format: {file_name}")

    ts_part = stem.replace("output_", "", 1)
    return datetime.strptime(ts_part, "%Y%m%d_%H%M%S")


def ensure_raw_schema(engine: Engine) -> None:
    with engine.begin() as conn:
        conn.execute(text(f"CREATE SCHEMA IF NOT EXISTS {RAW_SCHEMA}"))


def file_already_loaded(engine: Engine, source_file_name: str) -> bool:
    logger.info("Checking if file was already loaded: %s", source_file_name)

    with engine.connect() as conn:
        table_exists = conn.execute(text("""
            SELECT 1 FROM information_schema.tables
            WHERE table_schema = :schema AND table_name = :table
            LIMIT 1
        """), {"schema": RAW_SCHEMA, "table": RAW_TABLE}).first()

        if not table_exists:
            logger.info("Table does not exist yet — treating as not loaded")
            return False

        result = conn.execute(text(
            f"SELECT 1 FROM {RAW_SCHEMA}.{RAW_TABLE} WHERE source_file_name = :source_file_name LIMIT 1"
        ), {"source_file_name": source_file_name}).first()

    already_loaded = result is not None
    logger.info("File already loaded: %s", already_loaded)
    return already_loaded


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
    ensure_raw_schema(engine)
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

    ## Metadata from file
    df["source_file_name"] = source_file_name
    df["source_file_ts"] = source_file_ts
    df["ingested_at"] = datetime.now(timezone.utc).replace(tzinfo=None)
    df["dag_run_id"] = dag_run_id

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