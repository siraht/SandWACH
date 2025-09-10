#!/usr/bin/env python3
"""
SandWACH Main Application
Scheduling loop and notification system
"""

import time
import subprocess
import threading
from datetime import datetime

from config import (
    EVENING_ANALYSIS_HOUR, MORNING_ANALYSIS_HOUR,
    CHECK_INTERVAL_MINUTES, NOTIFICATION_TITLE
)
from weather import fetch_weather_data
from decisions import analyze_sleep_conditions, analyze_daytime_conditions, format_notification_message
from api import start_api_server

def send_system_notification(message):
    """Send system notification using notify-send"""
    try:
        subprocess.run([
            'notify-send',
            NOTIFICATION_TITLE,
            message
        ], check=True)
        print("System notification sent successfully")
    except subprocess.CalledProcessError as e:
        print(f"Failed to send system notification: {e}")
    except FileNotFoundError:
        print("notify-send not found, falling back to print")
        print(f"NOTIFICATION: {message}")

def send_email_notification(message):
    """Send email notification (placeholder for future implementation)"""
    print(f"Email notification would be sent: {message}")
    # TODO: Implement SMTP email sending if needed

def perform_evening_analysis():
    """Perform evening sleep analysis and send notification"""
    print("\n" + "="*50)
    print("EVENING ANALYSIS - SLEEP RECOMMENDATIONS")
    print("="*50)

    try:
        # Fetch weather data
        weather_data = fetch_weather_data()
        if not weather_data:
            error_msg = "SandWACH Error: Unable to fetch weather data for evening analysis"
            send_system_notification(error_msg)
            return

        # Analyze sleep conditions
        recommendations = analyze_sleep_conditions(weather_data)
        if "error" in recommendations:
            error_msg = f"SandWACH Error: {recommendations['error']}"
            send_system_notification(error_msg)
            return

        # Format and send notification
        message = format_notification_message(recommendations)
        send_system_notification(message)

        print("Evening analysis completed successfully")

    except Exception as e:
        error_msg = f"SandWACH Error: Evening analysis failed - {str(e)}"
        print(error_msg)
        send_system_notification(error_msg)

def perform_morning_analysis():
    """Perform morning daytime analysis and send notification"""
    print("\n" + "="*50)
    print("MORNING ANALYSIS - DAYTIME RECOMMENDATIONS")
    print("="*50)

    try:
        # Fetch weather data
        weather_data = fetch_weather_data()
        if not weather_data:
            error_msg = "SandWACH Error: Unable to fetch weather data for morning analysis"
            send_system_notification(error_msg)
            return

        # Analyze daytime conditions
        recommendations = analyze_daytime_conditions(weather_data)
        if "error" in recommendations:
            error_msg = f"SandWACH Error: {recommendations['error']}"
            send_system_notification(error_msg)
            return

        # Format and send notification
        message = format_notification_message(recommendations)
        send_system_notification(message)

        print("Morning analysis completed successfully")

    except Exception as e:
        error_msg = f"SandWACH Error: Morning analysis failed - {str(e)}"
        print(error_msg)
        send_system_notification(error_msg)

def should_run_evening_analysis():
    """Check if it's time for evening analysis (around 8 PM)"""
    current_hour = datetime.now().hour
    return current_hour == EVENING_ANALYSIS_HOUR

def should_run_morning_analysis():
    """Check if it's time for morning analysis (around 7 AM)"""
    current_hour = datetime.now().hour
    return current_hour == MORNING_ANALYSIS_HOUR

def main_loop():
    """Main scheduling loop"""
    print("SandWACH starting up...")
    print(f"Evening analysis at {EVENING_ANALYSIS_HOUR}:00")
    print(f"Morning analysis at {MORNING_ANALYSIS_HOUR}:00")
    print(f"Check interval: {CHECK_INTERVAL_MINUTES} minutes")
    print("Press Ctrl+C to stop")

    last_evening_run = None
    last_morning_run = None

    while True:
        current_time = datetime.now()
        current_hour = current_time.hour
        current_date = current_time.date()

        # Check for evening analysis
        if should_run_evening_analysis():
            if last_evening_run != current_date:
                perform_evening_analysis()
                last_evening_run = current_date

        # Check for morning analysis
        elif should_run_morning_analysis():
            if last_morning_run != current_date:
                perform_morning_analysis()
                last_morning_run = current_date

        # Periodic weather check (every hour)
        if current_time.minute == 0:
            print(f"[{current_time.strftime('%H:%M:%S')}] SandWACH running - waiting for analysis time")

        # Sleep for check interval
        time.sleep(CHECK_INTERVAL_MINUTES * 60)

def start_background_api_server():
    """Start API server in background thread"""
    api_thread = threading.Thread(target=start_api_server, daemon=True)
    api_thread.start()
    print("API server started in background")

def main():
    """Main entry point"""
    try:
        # Start API server in background
        start_background_api_server()

        # Give API server time to start
        time.sleep(2)

        # Start main scheduling loop
        main_loop()

    except KeyboardInterrupt:
        print("\nSandWACH stopped by user")
    except Exception as e:
        print(f"SandWACH error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
