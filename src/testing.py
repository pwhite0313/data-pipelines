cities = ['New York', 'Chicago', 'Los Angeles', 'Boston']

params = {"q": "New York", "appid": 'xxxx', "units": "imperial"}

del params["q"]

api_params = []

for city in cities:
    api_params.append({'q': city, **params})

print(api_params)