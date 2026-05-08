import logging
import time
import sys
import json

from src.logging_config import setup_logging
from src.extract import extract_records
from src.transform import transform_records
from src.load import load_records
from src.postgres.extract_to_postgres import load_all_files

logger = logging.getLogger(__name__)

def main():

    start_time = time.time()

    logger.info("=== Starting ingestion pipeline ===")

    # Start API client and extract
    try:
        raw_records = extract_records()
        logger.info("Extracted %s raw records", len(raw_records))

        # Log empty response and exit
        if not raw_records:
            logger.warning("No records returned")
            return

        # Transform
        clean_records = transform_records(raw_records)
        logger.info("Transformed %s records", len(clean_records))
    
        # Load
        output_path = load_records(clean_records)
        logger.info("Loaded records to %s", output_path)

        # Extract from raw directory and move to postgrres
        # TODO: Porcess only files not in DB -- Find unique key to overwrite
        # -- Overwite prefered since weather data can be updated.
        
        dag_run_id = f"manual_{int(start_time)}"
        load_all_files(dag_run_id=dag_run_id)
        logger.info("Files in data/raw loaded to Postgres")


        # Pipline run time
        elapsed = time.time() - start_time

        logger.info("=== Pipeline completed successfully in %.2f second s===", elapsed)

    except Exception as e:
        logger.exception("Pipline failed: %s", e)
        sys.exit(1)


if __name__ == "__main__":
    setup_logging()
    main()