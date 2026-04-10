import logging
import pandas as pd

logger = logging.getLogger(__name__)

## Function to call cities by name and return weather
def transform_records(data):

    logger.info("Transformation started")
    
    if not isinstance(data,dict) or "list" not in data:
        logger.error("Invalid structure: missing expected 'list'")
    try:
        # Normalize as Pandas DF
        df = pd.json_normalize(data['list'], sep="_")
    
    except Exception:
        logger.exception("Failed to normalize main data")
        raise

    try:
        df["weather"] = df["weather"].apply(
            lambda x: x[0] if isinstance(x, list) and len(x) > 0 else {}
        )

        df_weather = pd.json_normalize(df["weather"]).add_prefix("weather_")
        df = df.drop(columns=["weather"]).join(df_weather)

    except:
        logger.exception("Failed to process data")

    # Convert column to date_time
    df["dt_txt"] = pd.to_datetime(df["dt_txt"])

    try:
        city_data = data.get("city", {})

        if city_data:   
            # Add flattened city keys
            city_df = pd.json_normalize(data.get("city", {}), sep="_").add_prefix("city_")
            df = df.assign(**city_df.iloc[0].to_dict())

    except:
        logger.warning("No city data found")
        raise

    logger.info("Transformed to Pandas DF of shape: %s", df.shape)

    # Append and return
    return df