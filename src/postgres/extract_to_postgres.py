import logging
from pathlib import Path
from src.postgres.load_to_postgres import load_weather_csv_to_raw_table

from src.utils import RAW_DATA_DIR

logger = logging.getLogger(__name__)

def load_all_files(dag_run_id=None):

    if dag_run_id == "":
        dag_run_id = None

    csv_files = sorted(RAW_DATA_DIR.glob("output_*.csv"))

    if not csv_files:
        raise FileNotFoundError(f"No output CSV files found in {RAW_DATA_DIR}")

    results = []

    for file_path in csv_files:
        try:
            logger.info("Loading file: %s", file_path)

            result = load_weather_csv_to_raw_table(
                file_path=str(file_path),
                dag_run_id=dag_run_id,
                skip_if_loaded=True,  # dupes handled downstream in load file
            )

            results.append(result)

        except Exception:
            logger.exception("Failed on file: %s", file_path)

    return results


if __name__ == "__main__":
    load_all_files()