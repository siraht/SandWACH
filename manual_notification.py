#!/usr/bin/env python3
"""
Manual notification trigger for SandWACH
This simulates what the app would send at scheduled times
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import NTFY_ENABLED, NTFY_SERVER, NTFY_TOPIC, NTFY_AUTH_TOKEN

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

        print(f"📱 Sending notification to: {url}")
        print(f"📋 Title: {title}")
        print(f"📄 Message: {message[:200]}...")

        response = requests.post(url, data=message, headers=headers, timeout=10)

        if response.status_code == 200:
            print("✅ Notification sent successfully!")
            return True
        else:
            print(f"❌ Failed to send notification: {response.status_code}")
            print(f"❌ Response: {response.text}")
            return False

    except Exception as e:
        print(f"❌ Notification error: {e}")
        return False

def send_evening_notification():
    """Send a realistic evening notification"""
    message = """🌙 SandWACH Evening Climate Analysis
📍 Location: Boulder, CO
🕐 Time: 8:00 PM

🌡️ Current Conditions: 72°F, Partly cloudy
💧 Humidity: 65%

📊 Overnight Forecast (8 hours):
• Low: 58°F
• High: 78°F
• Conditions: Clear

🎯 Recommendations:
• Keep windows open tonight - comfortable sleeping temperatures expected
• No AC needed - temperatures will stay in comfortable range
• Fan may be helpful for airflow if desired

🔄 Analysis complete. Good night! 🛌"""

    return send_ntfy_notification(message, "SandWACH - Evening Climate Control")

def send_morning_notification():
    """Send a realistic morning notification"""
    message = """☀️ SandWACH Morning Climate Analysis
📍 Location: Boulder, CO
🕐 Time: 7:00 AM

🌡️ Current Conditions: 62°F, Clear skies
💧 Humidity: 70%

📊 Daytime Forecast (12 hours):
• Low: 62°F
• High: 85°F
• Conditions: Sunny

🎯 Recommendations:
• Open windows early to cool the house
• AC recommended by afternoon (temps will reach 85°F)
• Consider closing windows around 11 AM to trap cool air

🔄 Analysis complete. Have a great day! ☀️"""

    return send_ntfy_notification(message, "SandWACH - Morning Climate Control")

if __name__ == "__main__":
    import datetime

    print("🚀 SandWACH Manual Notification Trigger")
    print("="*50)

    current_hour = datetime.datetime.now().hour

    if current_hour >= 12 and current_hour < 20:
        print("🕐 It's afternoon. You can choose which notification to send:")
        print("1. Evening notification (simulating 8 PM)")
        print("2. Morning notification (simulating 7 AM)")
        print("3. Both notifications")

        choice = input("\nEnter choice (1-3): ").strip()

        if choice == "1":
            send_evening_notification()
        elif choice == "2":
            send_morning_notification()
        elif choice == "3":
            print("\nSending both notifications...")
            send_evening_notification()
            send_morning_notification()
        else:
            print("Invalid choice. Sending evening notification...")
            send_evening_notification()

    elif current_hour >= 20:
        print("🌙 It's evening. Sending evening notification...")
        send_evening_notification()
    else:
        print("☀️ It's morning. Sending morning notification...")
        send_morning_notification()

    print("\n💡 To run the actual SandWACH app: python3 sandwach.py")
    print("💡 The app will automatically send notifications at 7 AM and 8 PM")