import logging
from src.client import get_json
from src.utils import params, endpoint

logger = logging.getLogger(__name__)

def extract_records() -> list:
    logger.info("Started extraction")

    try:
        data = get_json(endpoint, params)
    except Exception:
        logger.exception("Extraction failed")
        raise

    logger.info("%s records extracted", len(data))
    return data