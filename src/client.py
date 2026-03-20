import requests
import json
import logging

# Start a logger
logger = logging.getLogger(__name__)

# API Call
def get_json(url, params):
    logger.info("Calling API")

    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()

    # Catch ValueError
    if not response:
        raise ValueError(f"No results for {params.get(q)}")

    logger.info("API Call successful")
    return response.json()


    
