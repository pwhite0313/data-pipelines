import os
from pathlib import Path

# API Key stored as OS variable
api_key = os.environ["OPENWEATHER_API_KEY"]

# Output path
# Data directories
PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"

RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)

# Variables to pass to api_call() function
params = {"q": "New York", "appid": api_key, "units": "imperial"}
endpoint = "https://api.openweathermap.org/data/2.5/forecast"

