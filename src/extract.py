from src.client import get_json
from src.utils import api_key, params, endpoint

def extract_records() -> list:
    data = get_json(endpoint, params)
    return data