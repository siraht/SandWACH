#!/usr/bin/env python3
"""
Test script for ntfy.sh notifications
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import NTFY_ENABLED, NTFY_SERVER, NTFY_TOPIC, NTFY_AUTH_TOKEN

def send_ntfy_notification(message, title=None):
    """Send notification via ntfy.sh"""
    if not NTFY_ENABLED:
        print("ntfy.sh notifications are disabled")
        return

    try:
        import requests

        url = f"{NTFY_SERVER}/{NTFY_TOPIC}"
        headers = {'Content-Type': 'text/plain'}

        if NTFY_AUTH_TOKEN:
            headers['Authorization'] = f'Bearer {NTFY_AUTH_TOKEN}'

        if title:
            headers['Title'] = title

        print(f"Sending to: {url}")
        print(f"Message: {message}")
        print(f"Title: {title}")

        response = requests.post(url, data=message, headers=headers, timeout=10)

        if response.status_code == 200:
            print("✅ ntfy.sh notification sent successfully")
        else:
            print(f"❌ Failed to send ntfy.sh notification: {response.status_code}")
            print(f"Response: {response.text}")

    except ImportError:
        print("❌ requests library not available for ntfy.sh notifications")
    except Exception as e:
        print(f"❌ ntfy.sh notification error: {e}")

if __name__ == "__main__":
    print("Testing ntfy.sh integration...")
    print(f"NTFY_ENABLED: {NTFY_ENABLED}")
    print(f"NTFY_SERVER: {NTFY_SERVER}")
    print(f"NTFY_TOPIC: {NTFY_TOPIC}")
    print(f"NTFY_AUTH_TOKEN: {'Set' if NTFY_AUTH_TOKEN else 'Not set'}")
    print()

    test_message = "SandWACH Test Notification\nThis is a test of the ntfy.sh integration.\n\nIf you see this, ntfy.sh is working! 📱"
    send_ntfy_notification(test_message, "SandWACH Test")
