import pandas as pd

## Function to call cities by name and return weather
def transform_records(data):

    # Normalize as Pandas DF
    df = pd.json_normalize(data['list'], sep="_")

    df["weather"] = df["weather"].apply(
        lambda x: x[0] if isinstance(x, list) and len(x) > 0 else {}
    )

    df_weather = pd.json_normalize(df["weather"]).add_prefix("weather_")
    df = df.drop(columns=["weather"]).join(df_weather)

    # Convert column to date_time
    df["dt_txt"] = pd.to_datetime(df["dt_txt"])

    # Add flattened city keys
    city_df = pd.json_normalize(data.get("city", {}), sep="_").add_prefix("city_")
    df = df.assign(**city_df.iloc[0].to_dict())

    # Append and return
    return df