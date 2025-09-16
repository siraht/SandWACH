#!/usr/bin/env python3
"""
Comprehensive test script for SandWACH notifications
Tests both morning and evening notification formats with realistic fake data
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import NTFY_ENABLED, NTFY_SERVER, NTFY_TOPIC, NTFY_AUTH_TOKEN
from weather import load_weather_cache
from decisions import analyze_sleep_conditions, analyze_daytime_conditions

def send_ntfy_notification(message, title=None):
    """Send notification via ntfy.sh"""
    if not NTFY_ENABLED:
        print("❌ ntfy.sh notifications are disabled")
        return False

    try:
        import requests

        url = f"{NTFY_SERVER}/{NTFY_TOPIC}"
        headers = {'Content-Type': 'text/plain'}

        if NTFY_AUTH_TOKEN:
            headers['Authorization'] = f'Bearer {NTFY_AUTH_TOKEN}'

        if title:
            headers['Title'] = title

        print(f"📱 Sending to: {url}")
        print(f"📋 Title: {title}")
        print(f"📄 Message preview: {message[:100]}...")

        response = requests.post(url, data=message, headers=headers, timeout=10)

        if response.status_code == 200:
            print("✅ ntfy.sh notification sent successfully")
            return True
        else:
            print(f"❌ Failed to send ntfy.sh notification: {response.status_code}")
            print(f"❌ Response: {response.text}")
            return False

    except ImportError:
        print("❌ requests library not available for ntfy.sh notifications")
        return False
    except Exception as e:
        print(f"❌ ntfy.sh notification error: {e}")
        return False

def create_fake_weather_data():
    """Create realistic fake weather data for testing"""
    return {
        "current": {
            "Temperature": {"Value": 72.0},
            "WeatherText": "Partly cloudy",
            "RelativeHumidity": 65,
            "Wind": {"Speed": {"Value": 8.0}},
            "EpochTime": 1234567890
        },
        "forecast": [
            {
                "Date": "2024-09-15T20:00:00-06:00",
                "Temperature": {"Minimum": {"Value": 58.0}, "Maximum": {"Value": 78.0}},
                "Day": {"IconPhrase": "Partly sunny"},
                "Night": {"IconPhrase": "Clear"}
            },
            {
                "Date": "2024-09-16T08:00:00-06:00",
                "Temperature": {"Minimum": {"Value": 62.0}, "Maximum": {"Value": 85.0}},
                "Day": {"IconPhrase": "Sunny"},
                "Night": {"IconPhrase": "Partly cloudy"}
            }
        ]
    }

def test_evening_notification():
    """Test evening (sleep) notification"""
    print("\n" + "="*60)
    print("🌙 TESTING EVENING NOTIFICATION")
    print("="*60)

    # Create fake weather data
    fake_weather = create_fake_weather_data()

    # Analyze sleep conditions
    try:
        result = analyze_sleep_conditions(fake_weather)

        if result.get('error'):
            message = f"❌ Evening analysis error: {result['error']}"
        else:
            # Format the notification message like the real app
            message = f"""🌙 SandWACH Evening Climate Analysis
📍 Location: Boulder, CO
🕐 Time: 8:00 PM

🌡️ Current Conditions: {fake_weather['current']['Temperature']['Value']}°F, {fake_weather['current']['WeatherText']}
💧 Humidity: {fake_weather['current']['RelativeHumidity']}%

📊 Overnight Forecast (8 hours):
• Low: {fake_weather['forecast'][0]['Temperature']['Minimum']['Value']}°F
• High: {fake_weather['forecast'][0]['Temperature']['Maximum']['Value']}°F
• Conditions: {fake_weather['forecast'][0]['Night']['IconPhrase']}

🎯 Recommendations:
{result.get('recommendations', 'No specific recommendations')}

🔄 Analysis complete. Good night! 🛌"""

        success = send_ntfy_notification(message, "SandWACH - Evening Climate Control")
        return success

    except Exception as e:
        error_msg = f"❌ Evening notification test failed: {e}"
        print(error_msg)
        return send_ntfy_notification(error_msg, "SandWACH - Test Error")

def test_morning_notification():
    """Test morning (daytime) notification"""
    print("\n" + "="*60)
    print("☀️ TESTING MORNING NOTIFICATION")
    print("="*60)

    # Create fake weather data
    fake_weather = create_fake_weather_data()

    # Analyze daytime conditions
    try:
        result = analyze_daytime_conditions(fake_weather)

        if result.get('error'):
            message = f"❌ Morning analysis error: {result['error']}"
        else:
            # Format the notification message like the real app
            message = f"""☀️ SandWACH Morning Climate Analysis
📍 Location: Boulder, CO
🕐 Time: 7:00 AM

🌡️ Current Conditions: {fake_weather['current']['Temperature']['Value']}°F, {fake_weather['current']['WeatherText']}
💧 Humidity: {fake_weather['current']['RelativeHumidity']}%

📊 Daytime Forecast (12 hours):
• Low: {fake_weather['forecast'][1]['Temperature']['Minimum']['Value']}°F
• High: {fake_weather['forecast'][1]['Temperature']['Maximum']['Value']}°F
• Conditions: {fake_weather['forecast'][1]['Day']['IconPhrase']}

🎯 Recommendations:
{result.get('recommendations', 'No specific recommendations')}

🔄 Analysis complete. Have a great day! ☀️"""

        success = send_ntfy_notification(message, "SandWACH - Morning Climate Control")
        return success

    except Exception as e:
        error_msg = f"❌ Morning notification test failed: {e}"
        print(error_msg)
        return send_ntfy_notification(error_msg, "SandWACH - Test Error")

def test_configuration():
    """Test current ntfy configuration"""
    print("\n" + "="*60)
    print("⚙️ NOTIFICATION CONFIGURATION")
    print("="*60)
    print(f"NTFY_ENABLED: {NTFY_ENABLED}")
    print(f"NTFY_SERVER: {NTFY_SERVER}")
    print(f"NTFY_TOPIC: {NTFY_TOPIC}")
    print(f"NTFY_AUTH_TOKEN: {'Set' if NTFY_AUTH_TOKEN else 'Not set'}")

    # Test basic connectivity
    try:
        import requests
        test_msg = "🔧 SandWACH Configuration Test\n\nIf you see this, your ntfy.sh configuration is working!\n\nTime: " + __import__('datetime').datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        success = send_ntfy_notification(test_msg, "SandWACH - Config Test")
        return success
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False

def main():
    """Run comprehensive notification tests"""
    print("🧪 SandWACH Notification Test Suite")
    print("="*60)
    print("This will send 3 test notifications to verify ntfy.sh functionality")
    print("with realistic SandWACH notification formats.")
    print()

    # Test configuration first
    config_ok = test_configuration()

    if not config_ok:
        print("\n❌ Configuration test failed. Please check your ntfy.sh settings.")
        return

    # Test evening notification
    evening_ok = test_evening_notification()

    # Test morning notification
    morning_ok = test_morning_notification()

    # Summary
    print("\n" + "="*60)
    print("📊 TEST RESULTS SUMMARY")
    print("="*60)
    print(f"Configuration Test: {'✅ PASS' if config_ok else '❌ FAIL'}")
    print(f"Evening Notification: {'✅ PASS' if evening_ok else '❌ FAIL'}")
    print(f"Morning Notification: {'✅ PASS' if morning_ok else '❌ FAIL'}")

    if config_ok and evening_ok and morning_ok:
        print("\n🎉 All tests passed! ntfy.sh notifications should be working.")
        print("💡 If you're still not receiving notifications during normal app usage:")
        print("   1. Check that the app is actually running at scheduled times (7 AM, 8 PM)")
        print("   2. Verify weather data is being fetched successfully")
        print("   3. Check app logs for any errors")
    else:
        print("\n❌ Some tests failed. Please review the error messages above.")

if __name__ == "__main__":
    main()