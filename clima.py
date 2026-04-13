import openmeteo_requests
import pandas as pd
import requests_cache
from retry_requests import retry

# Setup the Open-Meteo API client with cache and retry on error
cache_session = requests_cache.CachedSession('.cache', expire_after = 3600)
retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
openmeteo = openmeteo_requests.Client(session = retry_session)

# Make sure all required weather variables are listed here
# The order of variables in hourly or daily is important to assign them correctly below
url = "https://api.open-meteo.com/v1/forecast"
params = {
	"latitude": 15.7278,
	"longitude": -88.5944,
	"hourly": ["temperature_2m", "apparent_temperature", "dew_point_2m", "soil_temperature_0cm", "soil_temperature_54cm", "precipitation_probability", "et0_fao_evapotranspiration", "soil_moisture_0_to_1cm", "soil_moisture_27_to_81cm", "wind_speed_10m", "cloud_cover", "cloud_cover_high", "pressure_msl", "surface_pressure", "visibility"],
}
responses = openmeteo.weather_api(url, params = params)

# Process first location. Add a for-loop for multiple locations or weather models
response = responses[0]
print(f"Coordinates: {response.Latitude()}°N {response.Longitude()}°E")
print(f"Elevation: {response.Elevation()} m asl")
print(f"Timezone difference to GMT+0: {response.UtcOffsetSeconds()}s")

# Process hourly data. The order of variables needs to be the same as requested.
hourly = response.Hourly()
hourly_temperature_2m = hourly.Variables(0).ValuesAsNumpy()
hourly_apparent_temperature = hourly.Variables(1).ValuesAsNumpy()
hourly_dew_point_2m = hourly.Variables(2).ValuesAsNumpy()
hourly_soil_temperature_0cm = hourly.Variables(3).ValuesAsNumpy()
hourly_soil_temperature_54cm = hourly.Variables(4).ValuesAsNumpy()
hourly_precipitation_probability = hourly.Variables(5).ValuesAsNumpy()
hourly_et0_fao_evapotranspiration = hourly.Variables(6).ValuesAsNumpy()
hourly_soil_moisture_0_to_1cm = hourly.Variables(7).ValuesAsNumpy()
hourly_soil_moisture_27_to_81cm = hourly.Variables(8).ValuesAsNumpy()
hourly_wind_speed_10m = hourly.Variables(9).ValuesAsNumpy()
hourly_cloud_cover = hourly.Variables(10).ValuesAsNumpy()
hourly_cloud_cover_high = hourly.Variables(11).ValuesAsNumpy()
hourly_pressure_msl = hourly.Variables(12).ValuesAsNumpy()
hourly_surface_pressure = hourly.Variables(13).ValuesAsNumpy()
hourly_visibility = hourly.Variables(14).ValuesAsNumpy()

hourly_data = {"date": pd.date_range(
	start = pd.to_datetime(hourly.Time(), unit = "s", utc = True),
	end =  pd.to_datetime(hourly.TimeEnd(), unit = "s", utc = True),
	freq = pd.Timedelta(seconds = hourly.Interval()),
	inclusive = "left"
)}

hourly_data["temperature_2m"] = hourly_temperature_2m
hourly_data["apparent_temperature"] = hourly_apparent_temperature
hourly_data["dew_point_2m"] = hourly_dew_point_2m
hourly_data["soil_temperature_0cm"] = hourly_soil_temperature_0cm
hourly_data["soil_temperature_54cm"] = hourly_soil_temperature_54cm
hourly_data["precipitation_probability"] = hourly_precipitation_probability
hourly_data["et0_fao_evapotranspiration"] = hourly_et0_fao_evapotranspiration
hourly_data["soil_moisture_0_to_1cm"] = hourly_soil_moisture_0_to_1cm
hourly_data["soil_moisture_27_to_81cm"] = hourly_soil_moisture_27_to_81cm
hourly_data["wind_speed_10m"] = hourly_wind_speed_10m
hourly_data["cloud_cover"] = hourly_cloud_cover
hourly_data["cloud_cover_high"] = hourly_cloud_cover_high
hourly_data["pressure_msl"] = hourly_pressure_msl
hourly_data["surface_pressure"] = hourly_surface_pressure
hourly_data["visibility"] = hourly_visibility

hourly_dataframe = pd.DataFrame(data = hourly_data)
print("\nHourly data\n", hourly_dataframe)
