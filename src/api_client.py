import pandas as pd
import json
import os
import logging
from utils import call_api

# API Key stored as OS variable
api_key = os.environ["OPENWEATHER_API_KEY"]

# Start a logger
logger = logging.getLogger(__name__)

## Function to get LAT and LON for a given city. Returned as a dictionary
def get_lat_lon(location) -> dict:

    city_name = location.get('city')
    
    # Assemble location for API call
    q_parts = [str(location.get("city").strip())]

    if state := location.get("state"):
        q_parts.append(state.strip())
    if country := location.get("country"):
        q_parts.append(country.strip().upper())
    
    
    # Variables to pass to api_call() function
    params = {"q": ",".join(q_parts), "limit": "1", "appid": api_key}
    url = "http://api.openweathermap.org/geo/1.0/direct"

    # Call API function and return JSON object
    data = call_api(url, params)

    # Pull Coordinates from response, include city to easier identify output
    coords = {
        "city": location.get("city").strip(),
        "lat": data[0]["lat"],
        "lon": data[0]["lon"]
    }
    
    return coords


## Function to call cities by name and return weather
def call_and_append(df, city):
    
    # Normalize city for consistent duplicate checks
    city_check = city.strip().lower()

    # If df already has the city, return df unchanged
    if 'city' in df.columns:
        existing_cities = df['city'].dropna().astype(str).str.strip().str.lower()
        if city_check in set(existing_cities):
            return df

    # Variables to pass to api_call() function
    params = {"q": city, "appid": api_key, "units": "imperial"}
    url = "https://api.openweathermap.org/data/2.5/forecast"


    # Call API function and return JSON object
    data = call_api(url, params)

    # Build new df from API
    new_df = pd.json_normalize(data["list"], sep="_")

    # Normalize and clean JSON object
    df_weather = pd.json_normalize(new_df['weather'].str[0]).add_prefix("weather_")
    new_df = new_df.drop(columns=['weather']).join(df_weather)

    new_df['dt_txt'] = pd.to_datetime(new_df['dt_txt'])
    new_df['city'] = city.strip() 

    # Append and return
    return pd.concat([df, new_df], ignore_index=True)


## Function to call API via lon and lat
# def call_by_coords():