# SandWACH Configuration
# Hardcoded values for personal use

import os

# Load environment variables from .env file
def load_env():
    env_path = os.path.join(os.path.dirname(__file__), '.env')
    if os.path.exists(env_path):
        with open(env_path) as f:
            for line in f:
                if line.strip() and not line.startswith('#'):
                    key, value = line.strip().split('=', 1)
                    os.environ[key] = value

load_env()

# Accuweather API Configuration
API_KEY = os.getenv('ACCUWEATHER_API_KEY')  # Load from environment variable
LOCATION_KEY = "327347"  # Boulder, CO location key
API_BASE_URL = "http://dataservice.accuweather.com"

# Temperature Thresholds (°F)
HOT_TEMP_THRESHOLD = 75  # Above this, recommend AC
COLD_TEMP_THRESHOLD = 55  # Below this, recommend heating
MILD_TEMP_MIN = 60
MILD_TEMP_MAX = 75

# Scheduling
EVENING_ANALYSIS_HOUR = 20  # 8 PM
MORNING_ANALYSIS_HOUR = 7   # 7 AM
CHECK_INTERVAL_MINUTES = 60  # Check every hour

# API Configuration
API_HOST = "localhost"
API_PORT = 8080
API_KEY_REQUIRED = os.getenv('API_KEY_REQUIRED')  # Load from environment variable

# File Paths
WEATHER_CACHE_FILE = "weather_cache.json"
DATABASE_FILE = "sandwach.db"

# Notification Settings
NOTIFICATION_TITLE = "SandWACH Climate Control"
EMAIL_FROM = "sandwach@localhost"
EMAIL_TO = "user@localhost"  # Replace with actual email

# ntfy.sh Configuration
NTFY_ENABLED = os.getenv('NTFY_ENABLED', 'false').lower() == 'true'
NTFY_SERVER = os.getenv('NTFY_SERVER', 'https://ntfy.sh')
NTFY_TOPIC = os.getenv('NTFY_TOPIC', 'sandwach')  # Your ntfy topic
NTFY_AUTH_TOKEN = os.getenv('NTFY_AUTH_TOKEN', '')  # Optional auth token

# System Settings
LOG_LEVEL = "INFO"
CACHE_DURATION_HOURS = 1

# Temperature Thresholds (°F) for Sleep Logic
AC_THRESHOLD_SLEEP = 65
WINDOWS_OPEN_TEMP_SLEEP = 65  # Example: comfortable temp to open windows
WINDOWS_CLOSED_TEMP_SLEEP = 50 # Example: getting too cold, close windows
FAN_ON_TEMP_SLEEP = 10
HEATING_THRESHOLD_SLEEP = 10

# Time-based Rule Configuration (in hours from now)
AC_TIME_HORIZON_SLEEP = 2       # Check for temp drop within 2 hours
WINDOWS_OPEN_TIME_HORIZON = 2   # Check for temp drop within 2 hours
WINDOWS_CLOSED_TIME_HORIZON = 9 # Check until 5 AM (assuming check at 8 PM)
HEATING_TIME_HORIZON = 7        # Check until 3 AM (assuming check at 8 PM)