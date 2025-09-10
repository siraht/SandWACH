# SandWACH - Simplified Personal Architecture

## Overview

SandWACH is a simplified personal application for automated climate control recommendations based on weather forecasts. Built for speed of development and ease of deployment with minimal complexity.

## Core Requirements

- Fetch weather data from Accuweather API for Boulder, CO
- Analyze nighttime (8 PM) and daytime (7 AM) temperature forecasts
- Provide recommendations for AC, heating, and window usage
- Send system notifications at appropriate times
- Expose single API endpoint for external app integration
- Include basic MCP server for inter-app communication
- Run locally on personal server

## Simplified Architecture

### Tech Stack
- **Language:** Python 3.11
- **HTTP Client:** requests
- **Database:** sqlite3 (built-in)
- **Scheduling:** time.sleep() loop
- **API Framework:** Built-in http.server
- **MCP:** Basic JSON-RPC implementation

### Core Modules

#### 1. weather.py
- Simple Accuweather API client
- Fetches current and forecast data
- Basic caching with file storage
- Error handling with fallbacks

#### 2. decisions.py
- Temperature analysis logic
- Simple rule-based recommendations
- Configurable temperature thresholds
- Returns AC/heating/window suggestions

#### 3. api.py
- Single `/api/recommendations` endpoint
- Basic API key authentication
- MCP server implementation
- JSON responses

#### 4. main.py
- Scheduling loop (runs every hour)
- Calls weather fetcher and decision maker
- Sends notifications at 8 PM and 7 AM
- Starts API server

#### 5. config.py
- Hardcoded configuration values
- API key, location, temperature thresholds
- Notification settings

### Data Storage

#### Simple SQLite Schema
```sql
CREATE TABLE weather_cache (
    timestamp INTEGER,
    data TEXT
);

CREATE TABLE notifications (
    id INTEGER PRIMARY KEY,
    type TEXT, -- 'evening' or 'morning'
    content TEXT,
    sent_at INTEGER
);
```

#### File-Based Storage
- Weather cache: JSON file
- Configuration: Python variables
- No complex database operations

### API Security
- Simple API key authentication for external access
- Input validation for request parameters
- Local network access only

### Deployment
- Simple Python execution: `python main.py`
- No Docker complexity
- Direct system integration

### Error Handling
- Basic try/except blocks
- Print statements for debugging
- Continue operation on failures
- Use cached data as fallback

### Development Approach
- Procedural code over complex patterns
- Direct function calls
- Minimal abstractions
- Fast iteration and testing

## Benefits of Simplification

1. **Rapid Development:** Days instead of weeks
2. **Easy Maintenance:** Simple codebase
3. **Fast Deployment:** No complex setup
4. **Minimal Dependencies:** Standard library + requests
5. **Direct Control:** No framework abstractions

## Implementation Plan

1. Create core modules (weather.py, decisions.py, api.py)
2. Implement main scheduling loop
3. Add basic error handling
4. Test with real Accuweather API
5. Deploy and monitor

This simplified architecture maintains all required functionality while dramatically reducing complexity and development time.
