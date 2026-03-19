import logging
import time
import sys
import json

from logging_config import setup_logging
from extract import extract_records
from transform import transform_records
from load import load_records

logger = logging.getLogger(__name__)

def main():

    start_time = time.time()

    # Setup loggers per file
    setup_logging()
    logger.info("===Starting ingestion pipeline===")

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

        # Pipline run time
        elapsed = time.time() - start_time

        logger.info("Pipeline completed successfully in %.2f seconds", elapsed)

    except Exception as e:
        logger.exception("Pipline failed: %s", e)
        sys.exit(1)


if __name__ == "__main__":
    main()