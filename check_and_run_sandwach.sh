#!/bin/bash

# SandWACH Health Check and Auto-Restart Script for Unraid
# This script checks if SandWACH is running and starts it if not

# Load environment variables
ENV_FILE="$(dirname "$0")/.env"
if [ -f "$ENV_FILE" ]; then
    export $(grep -v '^#' "$ENV_FILE" | xargs)
fi

# Default SandWACH directory if not set in environment
SANDWACH_DIR="${SANDWACH_DIR:-/mnt/user/appdata/sandWACH}"
MAIN_PY="$SANDWACH_DIR/main.py"
LOG_FILE="$SANDWACH_DIR/sandwach.log"
PID_FILE="$SANDWACH_DIR/sandwach.pid"

# Function to check if SandWACH is running
is_sandwach_running() {
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if ps -p "$PID" > /dev/null 2>&1; then
            return 0  # Running
        else
            rm -f "$PID_FILE"  # Remove stale PID file
            return 1  # Not running
        fi
    else
        return 1  # Not running (no PID file)
    fi
}

# Function to start SandWACH
start_sandwach() {
    echo "Starting SandWACH..."
    
    # Check if the directory exists
    if [ ! -d "$SANDWACH_DIR" ]; then
        echo "Error: SandWACH directory not found: $SANDWACH_DIR"
        exit 1
    fi
    
    # Check if main.py exists
    if [ ! -f "$MAIN_PY" ]; then
        echo "Error: main.py not found at: $MAIN_PY"
        exit 1
    fi
    
    # Change to SandWACH directory
    cd "$SANDWACH_DIR" || {
        echo "Error: Cannot change to directory: $SANDWACH_DIR"
        exit 1
    }
    
    # Start SandWACH in background with nohup
    # Set PYTHONPATH to include the SandWACH directory
    export PYTHONPATH="$SANDWACH_DIR:$PYTHONPATH"
    nohup python3 main.py > "$LOG_FILE" 2>&1 &
    PID=$!
    
    # Save PID to file
    echo "$PID" > "$PID_FILE"
    
    echo "SandWACH started with PID: $PID"
    echo "Log file: $LOG_FILE"
    echo "PID file: $PID_FILE"
    
    # Wait a moment and check if it's still running
    sleep 2
    if ps -p "$PID" > /dev/null 2>&1; then
        echo "SandWACH started successfully"
    else
        echo "Error: SandWACH failed to start"
        echo "Check log file: $LOG_FILE"
        exit 1
    fi
}

# Function to stop SandWACH
stop_sandwach() {
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if ps -p "$PID" > /dev/null 2>&1; then
            echo "Stopping SandWACH (PID: $PID)..."
            kill "$PID"
            sleep 2
            
            # Force kill if still running
            if ps -p "$PID" > /dev/null 2>&1; then
                echo "Force killing SandWACH..."
                kill -9 "$PID"
            fi
            
            rm -f "$PID_FILE"
            echo "SandWACH stopped"
        else
            echo "SandWACH is not running"
            rm -f "$PID_FILE"
        fi
    else
        echo "SandWACH is not running (no PID file)"
    fi
}

# Function to show status
show_status() {
    if is_sandwach_running; then
        PID=$(cat "$PID_FILE")
        echo "SandWACH is running (PID: $PID)"
        echo "Log file: $LOG_FILE"
    else
        echo "SandWACH is not running"
    fi
}

# Main script logic
case "${1:-status}" in
    "start")
        if is_sandwach_running; then
            echo "SandWACH is already running"
            show_status
        else
            start_sandwach
        fi
        ;;
    "stop")
        stop_sandwach
        ;;
    "restart")
        stop_sandwach
        sleep 2
        start_sandwach
        ;;
    "status")
        show_status
        ;;
    "check")
        if is_sandwach_running; then
            echo "SandWACH is running"
        else
            echo "SandWACH is not running - starting it..."
            start_sandwach
        fi
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|status|check}"
        echo ""
        echo "Commands:"
        echo "  start   - Start SandWACH if not running"
        echo "  stop    - Stop SandWACH if running"
        echo "  restart - Stop and restart SandWACH"
        echo "  status  - Show current status"
        echo "  check   - Check if running, start if not (default)"
        echo ""
        echo "Default action: check"
        exit 1
        ;;
esac