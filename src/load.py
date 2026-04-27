import logging
import json
import pandas as pd
from datetime import datetime
from src.utils import RAW_DATA_DIR

logger = logging.getLogger(__name__)

def load_records(records, output_path=None) -> str:
    if output_path is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = RAW_DATA_DIR / f"output_{timestamp}.csv"

    logger.info("Starting load")

    logger.info(f"Writing records to {output_path}")
    with open(output_path, "w", encoding="utf-8", newline="") as f:
        records.to_csv(f, index=False)

    logger.info("%s loaded", len(records))

    return str(output_path)