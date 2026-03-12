import pandas as pd

## Function to call cities by name and return weather
def transform_records(data):
    
    df = pd.json_normalize(data)
    # Build new df from API
    # df = pd.json_normalize(data["data"], sep="_")

    # # Normalize and clean JSON object
    # df_weather = pd.json_normalize(new_df['weather'].str[0]).add_prefix("weather_")
    # df = df.drop(columns=['weather']).join(df_weather)

    # df['dt_txt'] = pd.to_datetime(new_df['dt_txt'])
    # df['city'] = city.strip() 

    # Append and return
    return df