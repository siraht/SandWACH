#!/usr/bin/env python3
"""
SandWACH Decision Engine
Simple temperature analysis and climate control recommendations
"""

from config import (
    HOT_TEMP_THRESHOLD, COLD_TEMP_THRESHOLD,
    MILD_TEMP_MIN, MILD_TEMP_MAX
)

def analyze_sleep_conditions(weather_data):
    """
    Analyze overnight temperature forecast for sleeping recommendations
    Returns: dict with recommendations
    """
    if not weather_data or 'forecast' not in weather_data:
        return {"error": "No weather data available"}

    # Get temperatures for next 8 hours (overnight period)
    overnight_temps = get_forecast_temperatures(weather_data, 8)

    if not overnight_temps:
        return {"error": "No forecast data available"}

    # Analyze temperature trends
    min_temp = min(overnight_temps)
    max_temp = max(overnight_temps)
    avg_temp = sum(overnight_temps) / len(overnight_temps)

    print(f"Sleep analysis - Min: {min_temp}°F, Max: {max_temp}°F, Avg: {avg_temp:.1f}°F")

    recommendations = {
        "type": "sleep",
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
            "reason": f"Overnight high of {max_temp}°F exceeds comfort threshold",
            "priority": "high"
        })

    if min_temp <= COLD_TEMP_THRESHOLD:
        recommendations["actions"].append({
            "action": "heating",
            "reason": f"Overnight low of {min_temp}°F below comfort threshold",
            "priority": "high"
        })

    if MILD_TEMP_MIN <= avg_temp <= MILD_TEMP_MAX and not recommendations["actions"]:
        recommendations["actions"].append({
            "action": "windows",
            "reason": f"Average temperature {avg_temp:.1f}°F is comfortable for open windows",
            "priority": "medium"
        })

    # Default recommendation if no specific actions
    if not recommendations["actions"]:
        recommendations["actions"].append({
            "action": "monitor",
            "reason": f"Temperatures are moderate, continue monitoring",
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
