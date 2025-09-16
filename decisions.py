#!/usr/bin/env python3
"""
SandWACH Decision Engine
Simple temperature analysis and climate control recommendations
"""

from datetime import datetime, timedelta
from config import (
    # Import new sleep config
    AC_THRESHOLD_SLEEP, WINDOWS_OPEN_TEMP_SLEEP, WINDOWS_CLOSED_TEMP_SLEEP,
    FAN_ON_TEMP_SLEEP, HEATING_THRESHOLD_SLEEP, AC_TIME_HORIZON_SLEEP,
    WINDOWS_OPEN_TIME_HORIZON, WINDOWS_CLOSED_TIME_HORIZON,
    HEATING_TIME_HORIZON,

    # Existing config
    HOT_TEMP_THRESHOLD, COLD_TEMP_THRESHOLD,
    MILD_TEMP_MIN, MILD_TEMP_MAX
)

def analyze_sleep_conditions(weather_data):
    """
    Analyze overnight temperature forecast for sleeping recommendations
    using a priority-based, time-aware rule set.
    """
    if not weather_data or 'forecast' not in weather_data:
        return {"error": "No weather data available"}

    forecast = weather_data['forecast']
    now = datetime.now()

    # --- Helper functions for time-series analysis ---
    def get_temp_at_hour(target_hour):
        for hour_data in forecast:
            hour_dt = datetime.fromtimestamp(hour_data['time'])
            if hour_dt.hour == target_hour:
                return hour_data['temperature']
        return None

    def temp_drops_below(temp, within_hours):
        for i in range(min(within_hours, len(forecast))):
            if forecast[i]['temperature'] < temp:
                return True
        return False

    # Get temperatures for sleep analysis (next 12 hours for overnight)
    sleep_temps = get_forecast_temperatures(weather_data, 12)

    # Analyze temperature trends
    min_temp = min(sleep_temps) if sleep_temps else None
    max_temp = max(sleep_temps) if sleep_temps else None
    avg_temp = sum(sleep_temps) / len(sleep_temps) if sleep_temps else None

    avg_str = f"{avg_temp:.1f}" if avg_temp is not None else "N/A"
    print(f"Sleep analysis - Min: {min_temp}°F, Max: {max_temp}°F, Avg: {avg_str}°F")

    # --- Rule Evaluation ---
    recommendations = {
        "type": "sleep",
        "temperature_analysis": {
            "min_temp": min_temp,
            "max_temp": max_temp,
            "avg_temp": round(avg_temp, 1) if avg_temp else None
        },
        "actions": []
    }

    # Rule 1: Heating (Highest Priority)
    # If the temperature is going to drop below 10°F by 3 AM
    temp_at_3am = get_temp_at_hour(3)
    if temp_at_3am is not None and temp_at_3am < HEATING_THRESHOLD_SLEEP:
        recommendations["actions"].append({
            "action": "heating",
            "reason": f"Temperature will drop to {temp_at_3am}°F by 3 AM.",
            "priority": "high"
        })
        return recommendations # Stop further checks

    # Rule 2: AC
    # Recommend AC if the temperature does not drop below 65°F within 2 hours
    if not temp_drops_below(AC_THRESHOLD_SLEEP, AC_TIME_HORIZON_SLEEP):
         recommendations["actions"].append({
            "action": "ac",
            "reason": f"Temperature will not drop below {AC_THRESHOLD_SLEEP}°F in the next {AC_TIME_HORIZON_SLEEP} hours.",
            "priority": "high"
        })
         return recommendations # Stop further checks

    # Rule 3: Windows Open
    # If temp drops to window-open temp within 2hrs and does not drop below window-closed temp by 5am
    temp_at_5am = get_temp_at_hour(5)
    if temp_drops_below(WINDOWS_OPEN_TEMP_SLEEP, WINDOWS_OPEN_TIME_HORIZON) and \
       (temp_at_5am is None or temp_at_5am >= WINDOWS_CLOSED_TEMP_SLEEP):
        recommendations["actions"].append({
            "action": "windows_open",
            "reason": f"Temperatures will be ideal for open windows tonight.",
            "priority": "medium"
        })
        return recommendations

    # Rule 4: Windows Closed, Fan On
    # if at any point in the evening the temp drops below 10°F
    if temp_drops_below(FAN_ON_TEMP_SLEEP, HEATING_TIME_HORIZON):
         recommendations["actions"].append({
            "action": "windows_closed_fan_on",
            "reason": f"It will get very cold tonight (below {FAN_ON_TEMP_SLEEP}°F), but heating is not yet required.",
            "priority": "medium"
        })
         return recommendations

    # Default Fallback Recommendation
    if not recommendations["actions"]:
        recommendations["actions"].append({
            "action": "monitor",
            "reason": "Conditions are mild. No specific action required.",
            "priority": "low"
        })

    return recommendations

def analyze_daytime_conditions(weather_data):
    """
    Analyze daytime temperature forecast for habitation recommendations
    Returns: dict with recommendations
    """
    if not weather_data or 'forecast' not in weather_data:
        return {"error": "No weather data available"}

    # Get temperatures for next 12 hours (daytime period)
    daytime_temps = get_forecast_temperatures(weather_data, 12)

    if not daytime_temps:
        return {"error": "No forecast data available"}

    # Analyze temperature trends
    min_temp = min(daytime_temps)
    max_temp = max(daytime_temps)
    avg_temp = sum(daytime_temps) / len(daytime_temps)

    print(f"Daytime analysis - Min: {min_temp}°F, Max: {max_temp}°F, Avg: {avg_temp:.1f}°F")

    recommendations = {
        "type": "day",
        "temperature_analysis": {
            "min_temp": min_temp,
            "max_temp": max_temp,
            "avg_temp": round(avg_temp, 1)
        },
        "actions": []
    }

    # Decision logic
    if max_temp >= HOT_TEMP_THRESHOLD:
        recommendations["actions"].append({
            "action": "ac",
            "reason": f"Daytime high of {max_temp}°F requires cooling",
            "priority": "high"
        })

    if min_temp <= COLD_TEMP_THRESHOLD:
        recommendations["actions"].append({
            "action": "heating",
            "reason": f"Daytime low of {min_temp}°F requires heating",
            "priority": "high"
        })

    if MILD_TEMP_MIN <= avg_temp <= MILD_TEMP_MAX and not recommendations["actions"]:
        recommendations["actions"].append({
            "action": "windows",
            "reason": f"Average temperature {avg_temp:.1f}°F is comfortable for natural ventilation",
            "priority": "medium"
        })

    # Default recommendation if no specific actions
    if not recommendations["actions"]:
        recommendations["actions"].append({
            "action": "comfortable",
            "reason": f"Current conditions are comfortable, no action needed",
            "priority": "low"
        })

    return recommendations

def get_forecast_temperatures(weather_data, hours_ahead):
    """Extract forecast temperatures from weather data"""
    if not weather_data or 'forecast' not in weather_data:
        return []

    return [
        hour['temperature']
        for hour in weather_data['forecast'][:hours_ahead]
    ]

def format_notification_message(recommendations):
    """
    Format recommendations into a human-readable notification message
    Returns: string message for notification
    """
    if "error" in recommendations:
        return f"SandWACH Error: {recommendations['error']}"

    analysis = recommendations["temperature_analysis"]
    actions = recommendations["actions"]

    if recommendations["type"] == "sleep":
        period = "overnight"
    else:
        period = "daytime"

    message = f"{period.title()} Climate Control\n"
    message += f"Temps: {analysis['min_temp']}°F - {analysis['max_temp']}°F\n\n"

    for action in actions:
        priority_icon = "🔴" if action["priority"] == "high" else "🟡" if action["priority"] == "medium" else "🟢"
        message += f"{priority_icon} {action['action'].upper()}: {action['reason']}\n"

    return message

# Test functions
if __name__ == "__main__":
    print("Testing decision engine...")

    # Mock weather data for testing
    mock_weather = {
        "current": {"temperature": 72, "conditions": "Clear", "timestamp": 1234567890},
        "forecast": [
            {"time": 1234567890 + i*3600, "temperature": 70 + i, "conditions": "Clear", "precipitation_probability": 0}
            for i in range(12)
        ],
        "fetched_at": 1234567890
    }

    print("\n=== Sleep Analysis ===")
    sleep_rec = analyze_sleep_conditions(mock_weather)
    print(format_notification_message(sleep_rec))

    print("\n=== Daytime Analysis ===")
    day_rec = analyze_daytime_conditions(mock_weather)
    print(format_notification_message(day_rec))
