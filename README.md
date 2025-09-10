# SandWACH - Simplified Weather Climate Control Helper

A minimal Python application that fetches weather data and provides automated climate control recommendations for sleeping and daytime use.

## Features

- 🌤️ Fetches weather data from Accuweather API
- 🛏️ Analyzes overnight temperature forecasts for sleep recommendations
- ☀️ Analyzes daytime temperature forecasts for habitation recommendations
- 🔔 Sends system notifications at appropriate times (8 PM and 7 AM)
- 🌐 Provides single API endpoint for external app integration
- 🔧 Includes basic MCP server support
- 💾 Simple SQLite database for caching and notifications

## Quick Start

### 1. Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Set up database
python setup_db.py

# Configure API key (edit config.py)
# Replace "your_accuweather_api_key_here" with your actual API key
```

### 2. Run

```bash
# Start the application
python main.py
```

The application will:
- Start an API server on localhost:8080
- Run weather analysis at 8 PM (evening) and 7 AM (morning)
- Send system notifications with recommendations

## Configuration

Edit `config.py` to customize:

- **API_KEY**: Your Accuweather API key
- **LOCATION_KEY**: Accuweather location key for Boulder, CO (default: 331999)
- **EVENING_ANALYSIS_HOUR**: Hour for evening analysis (default: 20 = 8 PM)
- **MORNING_ANALYSIS_HOUR**: Hour for morning analysis (default: 7 = 7 AM)
- **API_KEY_REQUIRED**: API key for external access (default: sandwach_secret_key_2025)

## API Usage

### Health Check
```bash
curl http://localhost:8080/health
```

### Get Recommendations
```bash
# Sleep recommendations
curl "http://localhost:8080/api/recommendations?type=sleep" \
  -H "X-API-Key: sandwach_secret_key_2025"

# Daytime recommendations
curl "http://localhost:8080/api/recommendations?type=day" \
  -H "X-API-Key: sandwach_secret_key_2025"
```

### MCP Server
Send JSON-RPC requests to the API server for MCP integration.

## Architecture

### Core Modules

- **config.py**: Configuration settings
- **weather.py**: Accuweather API client with caching
- **decisions.py**: Temperature analysis and recommendations
- **api.py**: HTTP server with API endpoints and MCP support
- **main.py**: Main scheduling loop and notifications
- **setup_db.py**: Database initialization

### Data Flow

1. **Main Loop** runs every hour checking for analysis time
2. **Weather Module** fetches data from Accuweather API (with caching)
3. **Decision Engine** analyzes temperature forecasts
4. **Notification System** sends recommendations via system notifications
5. **API Server** provides external access to recommendations

## Requirements

- Python 3.11+
- Accuweather API key (free tier available)
- Linux system with `notify-send` (for notifications)

## Troubleshooting

### No notifications appearing
- Ensure `notify-send` is installed: `sudo apt install libnotify-bin`
- Check that you're running in a desktop environment

### API errors
- Verify your Accuweather API key is correct
- Check internet connectivity
- Free API tier has rate limits (50 calls/day)

### Permission errors
- Ensure the application can write to the current directory
- Check file permissions for database and cache files

## Development

### Testing Individual Modules

```bash
# Test weather module
python weather.py

# Test decision engine
python decisions.py

# Test API server
python api.py
```

### Database Management

```bash
# Initialize database
python setup_db.py

# Show database info
python setup_db.py info
```

## License

Personal use only.
