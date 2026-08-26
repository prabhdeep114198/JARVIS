"""
Weather Skill for JARVIS / Alexa.
Fetches real-time weather and forecast worldwide using free Open-Meteo API
or OpenWeatherMap API with zero required credentials.
"""

import json
import urllib.parse
import urllib.request
import config

# WMO Weather interpretation codes (WW)
WMO_CODES = {
    0: "clear skies",
    1: "mainly clear skies",
    2: "partly cloudy skies",
    3: "overcast clouds",
    45: "foggy conditions",
    48: "depositing rime fog",
    51: "light drizzle",
    53: "moderate drizzle",
    55: "dense drizzle",
    61: "slight rain",
    63: "moderate rain",
    65: "heavy rain",
    71: "slight snowfall",
    73: "moderate snowfall",
    75: "heavy snowfall",
    77: "snow grains",
    80: "slight rain showers",
    81: "moderate rain showers",
    82: "violent rain showers",
    85: "slight snow showers",
    86: "heavy snow showers",
    95: "a thunderstorm",
    96: "a thunderstorm with slight hail",
    99: "a thunderstorm with heavy hail"
}


def get_weather(city: str = None) -> str:
    """
    Fetch current weather and forecast for a given city.
    Uses free Open-Meteo API without requiring any API keys.
    """
    target_city = (city or config.DEFAULT_CITY).strip().title()
    
    # 1. Try Open-Meteo Free Global API
    try:
        # Step 1: Geocoding lookup
        geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={urllib.parse.quote(target_city)}&count=1&language=en&format=json"
        req = urllib.request.Request(geo_url, headers={"User-Agent": "JarvisAssistant/1.0"})
        with urllib.request.urlopen(req, timeout=5) as response:
            geo_data = json.loads(response.read().decode())

        if not geo_data.get("results"):
            return f"I couldn't find weather information for {target_city}. Please check the city name."

        result = geo_data["results"][0]
        lat = result["latitude"]
        lon = result["longitude"]
        city_resolved = result.get("name", target_city)
        country = result.get("country", "")

        # Step 2: Forecast query
        weather_url = (
            f"https://api.open-meteo.com/v1/forecast?"
            f"latitude={lat}&longitude={lon}&"
            f"current=temperature_2m,relative_humidity_2m,apparent_temperature,weather_code,wind_speed_10m&"
            f"daily=temperature_2m_max,temperature_2m_min&"
            f"timezone=auto"
        )
        w_req = urllib.request.Request(weather_url, headers={"User-Agent": "JarvisAssistant/1.0"})
        with urllib.request.urlopen(w_req, timeout=5) as response:
            w_data = json.loads(response.read().decode())

        current = w_data.get("current", {})
        temp = round(current.get("temperature_2m", 0))
        feels_like = round(current.get("apparent_temperature", temp))
        humidity = current.get("relative_humidity_2m", 0)
        wind = round(current.get("wind_speed_10m", 0))
        code = current.get("weather_code", 0)
        condition = WMO_CODES.get(code, "fair conditions")

        daily = w_data.get("daily", {})
        high = round(daily.get("temperature_2m_max", [temp])[0])
        low = round(daily.get("temperature_2m_min", [temp])[0])

        location_name = f"{city_resolved}, {country}" if country else city_resolved

        # Alexa-styled natural response
        speech = (
            f"Right now in {location_name}, it's {temp} degrees Celsius with {condition}. "
            f"Today you can expect a high of {high} degrees and a low of {low} degrees."
        )
        return speech

    except Exception:
        # Fallback to OpenWeatherMap if configured
        if config.OPENWEATHER_API_KEY and config.OPENWEATHER_API_KEY != "your_openweathermap_api_key":
            try:
                owm_url = f"https://api.openweathermap.org/data/2.5/weather?q={urllib.parse.quote(target_city)}&appid={config.OPENWEATHER_API_KEY}&units=metric"
                with urllib.request.urlopen(owm_url, timeout=5) as response:
                    owm_data = json.loads(response.read().decode())
                if owm_data.get("cod") == 200:
                    temp = round(owm_data["main"]["temp"])
                    desc = owm_data["weather"][0]["description"]
                    return f"In {target_city}, it's currently {temp} degrees Celsius with {desc}."
            except Exception:
                pass

        return f"Sorry, I was unable to retrieve the weather for {target_city} at this moment."
