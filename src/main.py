import pandas as pd
from api_client import get_lat_lon, call_and_append

def main():

    df = pd.DataFrame()
    
    location = {
        "city": "New York",
    }

    print(get_lat_lon(location))

    df = call_and_append(df, "New York")
    print(df['city'].unique())



if __name__ == "__main__":
    main()