import pandas as pd
from api_client import get_lat_lon, call_and_append
from plot import plot_weather

def main():

    df = pd.DataFrame()

    locations = [
        {"city": "New York", "state": "NY", "country": "US"},
        {"city": "Chicago", "state": "IL", "country": "US"},
        {"city": "Miami"},
        {"city": "London"},
        {"city": "Milan"}
    ]

    for i in range(len(locations)):
        print(get_lat_lon(locations[i]))

    for i in range(len(locations)):
        df = call_and_append(df, locations[i].get("city"))
    print(df.head())

    plot_weather(df)




if __name__ == "__main__":
    main()