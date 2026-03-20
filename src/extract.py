import logging
from src.client import get_json
from src.utils import api_key, params, endpoint

logger = logging.getLogger(__name__)

def extract_records() -> list:
    logger.info("Started extraction")

    data = get_json(endpoint, params)

    logger.info(f"{len(data)} records extracted")
    return data