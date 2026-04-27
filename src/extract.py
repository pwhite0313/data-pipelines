import logging
from src.client import get_json
from src.utils import cities, params, endpoint

logger = logging.getLogger(__name__)

def extract_records() -> list:
    logger.info("Started extraction")

    try:
        data = []

        for city in cities:
            api_params = ({'q': city, **params})

            response = get_json(endpoint, api_params)

            data.append(response)
        
    except Exception:
        logger.exception("Extraction failed")
        raise

    logger.info("%s records extracted", len(data))
    return data