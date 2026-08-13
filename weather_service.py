import requests

BASE_URL = "https://api.openweathermap.org/data/2.5/weather"


class WeatherAPIError(Exception):
    pass


def fetch_weather_by_postcode(postcode: str, api_key: str) -> dict:
    params = {
        "zip": f"{postcode},GB",
        "appid": api_key,
        "units": "metric",
    }
    resp = requests.get(BASE_URL, params=params, timeout=10)

    if resp.status_code == 401:
        raise WeatherAPIError("Invalid API key")
    if resp.status_code == 404:
        raise WeatherAPIError(f"No weather data found for postcode '{postcode}'")
    if resp.status_code != 200:
        raise WeatherAPIError(f"OpenWeather API returned status {resp.status_code}")

    data = resp.json()
    return {
        "city_name": data.get("name", "Unknown"),
        "temp_outside": data["main"]["temp"],
        "humidity": data["main"]["humidity"],
        "wind_speed": data["wind"]["speed"],
        "description": data["weather"][0]["description"] if data.get("weather") else "",
        "feels_like": data["main"].get("feels_like"),
    }
