"""
AgriScheme Backend — Weather service.
Uses Open-Meteo free API (no key required) for weather data.
"""
import requests
import logging

logger = logging.getLogger(__name__)

# WMO Weather Code to description + icon mapping
_WMO_CODES = {
    0: ("Clear sky", "☀️"),
    1: ("Mainly clear", "🌤️"),
    2: ("Partly cloudy", "⛅"),
    3: ("Overcast", "☁️"),
    45: ("Foggy", "🌫️"),
    48: ("Depositing fog", "🌫️"),
    51: ("Light drizzle", "🌦️"),
    53: ("Moderate drizzle", "🌦️"),
    55: ("Dense drizzle", "🌧️"),
    56: ("Freezing drizzle", "🌧️"),
    57: ("Dense freezing drizzle", "🌧️"),
    61: ("Slight rain", "🌦️"),
    63: ("Moderate rain", "🌧️"),
    65: ("Heavy rain", "🌧️"),
    66: ("Freezing rain", "🌧️"),
    67: ("Heavy freezing rain", "🌧️"),
    71: ("Slight snow", "🌨️"),
    73: ("Moderate snow", "🌨️"),
    75: ("Heavy snow", "❄️"),
    77: ("Snow grains", "❄️"),
    80: ("Slight showers", "🌦️"),
    81: ("Moderate showers", "🌧️"),
    82: ("Violent showers", "⛈️"),
    85: ("Slight snow showers", "🌨️"),
    86: ("Heavy snow showers", "❄️"),
    95: ("Thunderstorm", "⛈️"),
    96: ("Thunderstorm with hail", "⛈️"),
    99: ("Thunderstorm with heavy hail", "⛈️"),
}

OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"


def _decode_wmo(code):
    """Convert WMO weather code to description and icon."""
    desc, icon = _WMO_CODES.get(code, ("Unknown", "❓"))
    return desc, icon


def get_weather(lat, lon):
    """Fetch current weather + 5-day forecast from Open-Meteo.

    Args:
        lat: Latitude (float)
        lon: Longitude (float)

    Returns:
        dict with current conditions and daily forecast, or None on error.
    """
    try:
        params = {
            "latitude": lat,
            "longitude": lon,
            "current": "temperature_2m,relative_humidity_2m,weather_code,wind_speed_10m",
            "daily": "weather_code,temperature_2m_max,temperature_2m_min,precipitation_sum",
            "timezone": "Asia/Kolkata",
            "forecast_days": 5,
        }

        resp = requests.get(OPEN_METEO_URL, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()

        # Parse current conditions
        current = data.get("current", {})
        current_code = current.get("weather_code", 0)
        desc, icon = _decode_wmo(current_code)

        result = {
            "current": {
                "temperature": current.get("temperature_2m", 0),
                "humidity": current.get("relative_humidity_2m", 0),
                "wind_speed": current.get("wind_speed_10m", 0),
                "weather_code": current_code,
                "description": desc,
                "icon": icon,
            },
            "daily": [],
        }

        # Parse daily forecast
        daily = data.get("daily", {})
        dates = daily.get("time", [])
        codes = daily.get("weather_code", [])
        maxs = daily.get("temperature_2m_max", [])
        mins = daily.get("temperature_2m_min", [])
        precips = daily.get("precipitation_sum", [])

        for i in range(len(dates)):
            d, ic = _decode_wmo(codes[i] if i < len(codes) else 0)
            result["daily"].append({
                "date": dates[i],
                "temp_max": maxs[i] if i < len(maxs) else 0,
                "temp_min": mins[i] if i < len(mins) else 0,
                "precipitation": precips[i] if i < len(precips) else 0,
                "description": d,
                "icon": ic,
            })

        return result

    except requests.RequestException as e:
        logger.error("Open-Meteo API error: %s", e)
        return None
    except (KeyError, ValueError, IndexError) as e:
        logger.error("Weather data parsing error: %s", e)
        return None
