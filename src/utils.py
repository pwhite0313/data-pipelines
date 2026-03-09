import requests
import logging

# Setup logger
logger = logging.getLogger(__name__)

## Function to avoid redundent code and make API call function

def call_api(url, params):
    logger.info("Calling API")

    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()
    data = response.json()

    # # Catch ValueError
    if not data:
        raise ValueError(f"No results for {params.get(q)}")
    
    logger.info("API call complete")

    # Return JSON object
    return data