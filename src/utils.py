import requests


## Function to avoid redundent code and make API call function

def call_api(url, params):

    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()
    data = response.json()

    # Catch ValueError
    if not data:
        raise ValueError(f"No results for {params.get(q)}")
    
    # Return JSON object
    return data