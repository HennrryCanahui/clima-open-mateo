import requests
import pandas as pd

url = "https://api.open-meteo.com/v1/forecast"
params = {
    "latitude": 15.7278,
    "longitude": -88.5944,
    "hourly": "temperature_2m,relative_humidity_2m,precipitation",
    "timezone": "auto"
}

response = requests.get(url, params=params)
data = response.json()

if "hourly" in data:
    df = pd.DataFrame(data["hourly"])
    df["time"] = pd.to_datetime(df["time"])
    print(df.head())
else:
    print("Error en la respuesta:", data)