import logging
import json
import pandas as pd
from datetime import datetime
from src.utils import RAW_DATA_DIR

logger = logging.getLogger(__name__)

def load_records(records, output_path) -> str:
    logger.info("Starting load")

    logger.info(f"Writing records to {output_path}")
    with open(output_path, "w", encoding="utf-8", newline="") as f:
        records.to_csv(f, index=False)

    logger.info(f"{len(records)} loaded")

    return str(output_path)