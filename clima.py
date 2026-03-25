import pandas as pd
import requests
import sqlite3
from datetime import datetime

# 1. Ubicación (Manual o Automática)
def get_location():
    try:
        # Intentar obtener ubicación por IP
        res = requests.get('https://ipapi.co/json/', timeout=5).json()
        if 'latitude' in res:
            return res['latitude'], res['longitude'], res['city']
    except:
        pass
    return 15.7278, -88.5944, "Puerto Barrios"

lat, lon, city = get_location()
print(f"📍 Ubicación: {city} ({lat}, {lon})")

# 2. Parámetros de la API (JSON directo)
url = "https://api.open-meteo.com/v1/forecast"
params = {
    "latitude": lat,
    "longitude": lon,
    "hourly": [
        "temperature_2m", "relative_humidity_2m", "dewpoint_2m", "apparent_temperature",
        "precipitation_probability", "precipitation", "rain", "showers", "snowfall",
        "snow_depth", "weather_code", "pressure_msl", "surface_pressure", "cloud_cover",
        "visibility", "evapotranspiration", "et0_fao_evapotranspiration", "vapor_pressure_deficit",
        "wind_speed_10m", "wind_direction_10m", "wind_gusts_10m"
    ],
    "timezone": "auto",
    "forecast_days": 1  # Esto nos da exactamente de 00:00 a 23:59 de HOY
}

try:
    # 3. Petición y conversión
    response = requests.get(url, params=params)
    data = response.json()

    if "hourly" not in data:
        print(f"❌ Error de API: {data.get('reason', 'Desconocido')}")
        exit()

    # Crear el DataFrame desde el diccionario "hourly"
    df = pd.DataFrame(data["hourly"])
    
    # Renombrar 'time' a 'date' para mantener consistencia con tu DB
    df.rename(columns={'time': 'date'}, inplace=True)
    
    # Formatear la fecha para SQLite
    df['date'] = pd.to_datetime(df['date']).dt.strftime('%Y-%m-%d %H:%M:%S')

    # 4. Guardar en SQLite
    with sqlite3.connect('monitoreo_agricola.db') as conn:
        # Usamos 'replace' para que si lo corres hoy otra vez, actualice los datos de hoy
        df.to_sql('pronostico_clima', conn, if_exists='replace', index=False)

    print("---")
    print(f"✅ ¡Éxito! Registradas las 24 horas de hoy en {city}")
    print(df[['date', 'temperature_2m', 'et0_fao_evapotranspiration']].head(3))
    print("...")
    print(df[['date', 'temperature_2m', 'et0_fao_evapotranspiration']].tail(1))

except Exception as e:
    print(f"❌ Error crítico: {e}")