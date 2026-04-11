import logging
import pandas as pd

logger = logging.getLogger(__name__)

def validate_response(data):

    if not isinstance(data, dict):
        raise ValueError("API response must be a dictionary")
    
    if "list" not in data:
        raise ValueError("API response missing 'list' key")
    
    if not isinstance(data["list"], list):
        raise ValueError("'list' must be a list inside the 'data' dictionary")
    
    if "city" in data and not isinstance(data["city"], dict):
        raise ValueError("'city', was found but is not a dictionary")

## Function to call cities by name and return weather
def transform_records(data):

    logger.info("Transformation started")
    
    try:
        validate_response(data)
    except:
        logger.exception("Validation failed")
        raise

    df = pd.json_normalize(data['list'], sep="_")

    # Extract first weather object from list (API returns weather as a list of dicts)
    # If missing or invalid, default to empty dict to avoid downstream errors
    df["weather"] = df["weather"].apply(
        lambda x: x[0] if isinstance(x, list) and len(x) > 0 else {}
    )

    df_weather = pd.json_normalize(df["weather"]).add_prefix("weather_")
    df = df.drop(columns=["weather"]).join(df_weather)

    # Convert column to date_time
    df["dt_txt"] = pd.to_datetime(df["dt_txt"], errors="coerce")
    df = df.dropna(subset=["dt_txt"])

    city_data = data.get("city", {})

    if city_data:
        # Add flattened city keys
        city_df = pd.json_normalize(data.get("city", {}), sep="_").add_prefix("city_")
        df = df.assign(**city_df.iloc[0].to_dict())

    logger.info("Transformed to Pandas DF of shape: %s", df.shape)

    # Append and return
    return df