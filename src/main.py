import logging
from logging_config import setup_logging
from extract import extract_records
from transform import transform_records

logger = logging.getLogger(__name__)

def main():

    # Setup loggers per file
    setup_logging()

    logger.info("==Starting ingestion pipeline==")

    raw_records = extract_records()
    logger.info("Extracted %s raw records", len(raw_records))

    print(transform_records(raw_records))
    # clean_records = transform_records(raw_records)
    # logger.info("Transformed %s records", len(clean_records))

    # output_path = load_records(clean_records)
    # logger.info("Loaded records to %s", output_path)

    logger.info("Pipeline completed successfully")


if __name__ == "__main__":
    main()