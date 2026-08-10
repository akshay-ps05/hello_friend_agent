"""
Weather tool.

Returns actual weather information instead of search-result links.
Uses wttr.in, which does not require an API key.
"""

import logging

import httpx
from langchain.tools import tool

logger = logging.getLogger(__name__)

WEATHER_URL = "https://wttr.in/{location}"

TIMEOUT = 10.0


@tool
def search_weather(location: str) -> str:
    """
    Get the current weather and forecast for a location.

    Use this when the user asks about weather, temperature,
    conditions, rain, wind, humidity, or forecast.
    """

    location = location.strip()

    if not location:
        return "Error: location is required."

    try:
        response = httpx.get(
            WEATHER_URL.format(location=location),
            params={
                "format": "j1",
            },
            timeout=TIMEOUT,
        )

        response.raise_for_status()

        data = response.json()

        current = data["current_condition"][0]

        temperature = current.get("temp_C", "unknown")
        feels_like = current.get("FeelsLikeC", "unknown")
        condition = current["weatherDesc"][0]["value"]
        humidity = current.get("humidity", "unknown")
        wind_speed = current.get("windspeedKmph", "unknown")
        wind_direction = current.get("winddir16Point", "unknown")
        visibility = current.get("visibility", "unknown")
        pressure = current.get("pressure", "unknown")

        return (
            f"Weather for {location}\n\n"
            f"Condition: {condition}\n"
            f"Temperature: {temperature}°C\n"
            f"Feels like: {feels_like}°C\n"
            f"Humidity: {humidity}%\n"
            f"Wind: {wind_speed} km/h {wind_direction}\n"
            f"Visibility: {visibility} km\n"
            f"Pressure: {pressure} mb"
        )

    except httpx.TimeoutException:
        return f"Error: weather request timed out for '{location}'."

    except httpx.HTTPError as exc:
        logger.exception("Weather request failed")
        return f"Error: could not get weather for '{location}': {exc}"

    except (KeyError, IndexError, ValueError) as exc:
        logger.exception("Invalid weather response")
        return f"Error: could not understand weather data: {exc}"

    except Exception as exc:
        logger.exception("Unexpected weather error")
        return f"Error: could not get weather for '{location}': {exc}"