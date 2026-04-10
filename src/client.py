import requests
import logging

# Start a logger
logger = logging.getLogger(__name__)

# API Call
def get_json(url, params):
    logger.info("Calling API")

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
    
    except requests.exceptions.Timeout:
        logger.error("API request timed out")
        raise

    except requests.exceptions.HTTPError as e:
        logger.error(f"HTTP error: {e}")
        raise

    except requests.exceptions.RequestException as e:
        logger.error(f"Request failed: {e}")
        raise

    except ValueError:
        logger.error("Invalid JSON response")
        raise

    # Catch ValueError
    if not data:
        logger.error(f"No results for {params.get('q')}")
        raise ValueError(f"No results for {params.get('q')}")

    logger.info("API Call successful")
    return data