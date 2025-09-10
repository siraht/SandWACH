#!/usr/bin/env python3
"""
SandWACH Weather Module
Simple Accuweather API client with caching
"""

import json
import time
import requests
from config import (
    API_KEY, LOCATION_KEY, API_BASE_URL,
    WEATHER_CACHE_FILE, CACHE_DURATION_HOURS
)

def fetch_weather_data():
    """
    Fetch current weather and forecast from Accuweather API
    Returns: dict with current and forecast data, or None on error
    """
    try:
        # Check cache first
        cached_data = load_weather_cache()
        if cached_data and is_cache_valid(cached_data):
            print("Using cached weather data")
            return cached_data

        print("Fetching fresh weather data from API")

        # Fetch current conditions
        current_url = f"{API_BASE_URL}/currentconditions/v1/{LOCATION_KEY}"
        params = {"apikey": API_KEY, "details": "true"}
        print(f"Requesting: {current_url}")
        print(f"Params: {params}")
        current_response = requests.get(current_url, params=params, timeout=30)
        print(f"Response URL: {current_response.url}")
        print(f"Response Status: {current_response.status_code}")
        try:
            current_response.raise_for_status()
            current_data = current_response.json()[0]
        except requests.HTTPError as http_err:
            print(f"HTTP Error: {http_err}")
            print(f"Response Text: {current_response.text}")
            raise

        # DEBUG: Print raw current conditions response
        print("=== RAW CURRENT CONDITIONS RESPONSE ===")
        print(json.dumps(current_response.json(), indent=2))
        print("=== END RAW CURRENT ===")

        # Fetch hourly forecast (12 hours for analysis)
        forecast_url = f"{API_BASE_URL}/forecasts/v1/hourly/12hour/{LOCATION_KEY}"
        forecast_response = requests.get(forecast_url, params=params, timeout=30)
        forecast_response.raise_for_status()
        forecast_data = forecast_response.json()

        # DEBUG: Print raw forecast response
        print("=== RAW FORECAST RESPONSE ===")
        print(json.dumps(forecast_response.json(), indent=2))
        print("=== END RAW FORECAST ===")

        # Combine data
        weather_data = {
            "current": {
                "temperature": current_data["Temperature"]["Imperial"]["Value"],
                "conditions": current_data["WeatherText"],
                "humidity": current_data.get("RelativeHumidity", 0),
                "timestamp": current_data["EpochTime"]
            },
            "forecast": [
                {
                    "time": hour["EpochDateTime"],
                    "temperature": hour["Temperature"]["Value"],
                    "conditions": hour["IconPhrase"],
                    "precipitation_probability": hour.get("PrecipitationProbability", 0)
                }
                for hour in forecast_data
            ],
            "fetched_at": int(time.time())
        }

        # Cache the data
        save_weather_cache(weather_data)

        return weather_data

    except requests.RequestException as e:
        print(f"API request failed: {e}")
        # DEBUG: Print response details on error
        if hasattr(e, 'response') and e.response:
            print("=== ERROR RESPONSE DETAILS ===")
            print(f"Status Code: {e.response.status_code}")
            print(f"Headers: {dict(e.response.headers)}")
            try:
                print(f"Response Body: {e.response.text}")
            except:
                print("Could not read response body")
            print("=== END ERROR RESPONSE ===")
        # Return cached data as fallback
        cached_data = load_weather_cache()
        if cached_data:
            print("Using cached data as fallback")
            return cached_data
        return None
    except Exception as e:
        print(f"Unexpected error in weather fetch: {e}")
        return None

def load_weather_cache():
    """Load cached weather data from file"""
    try:
        with open(WEATHER_CACHE_FILE, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return None

def save_weather_cache(data):
    """Save weather data to cache file"""
    try:
        with open(WEATHER_CACHE_FILE, 'w') as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        print(f"Failed to save cache: {e}")

def is_cache_valid(cached_data):
    """Check if cached data is still valid"""
    if not cached_data or 'fetched_at' not in cached_data:
        return False

    cache_age_hours = (time.time() - cached_data['fetched_at']) / 3600
    return cache_age_hours < CACHE_DURATION_HOURS

def get_current_temperature(weather_data):
    """Extract current temperature from weather data"""
    if weather_data and 'current' in weather_data:
        return weather_data['current']['temperature']
    return None

def get_forecast_temperatures(weather_data, hours_ahead=6):
    """Get forecast temperatures for next N hours"""
    if not weather_data or 'forecast' not in weather_data:
        return []

    return [
        hour['temperature']
        for hour in weather_data['forecast'][:hours_ahead]
    ]

# Test function
if __name__ == "__main__":
    print("Testing weather module...")
    data = fetch_weather_data()
    if data:
        print(f"Current temp: {get_current_temperature(data)}°F")
        forecast = get_forecast_temperatures(data, 3)
        print(f"Next 3 hours: {forecast}")
    else:
        print("Failed to fetch weather data")
