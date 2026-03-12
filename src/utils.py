import os

# API Key stored as OS variable
api_key = os.environ["OPENWEATHER_API_KEY"]

# Variables to pass to api_call() function
params = {"q": "New York", "appid": api_key, "units": "imperial"}
endpoint = "https://api.openweathermap.org/data/2.5/forecast"

