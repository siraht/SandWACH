#!/bin/bash

# SandWACH Health Check and Auto-Restart Script for Unraid
# This script checks if SandWACH is running and starts it if not

# Load environment variables
ENV_FILE="$(dirname "$0")/.env"
if [ -f "$ENV_FILE" ]; then
    export $(grep -v '^#' "$ENV_FILE" | xargs)
fi

# Default SandWACH directory if not set in environment
if [ -n "$SANDWACH_DIR" ]; then
    : # Use the environment variable
elif [ -f "$(dirname "$0")/sandwach.py" ]; then
    SANDWACH_DIR="$(dirname "$0")"
elif [ -f "./sandwach.py" ]; then
    SANDWACH_DIR="."
elif [ -f "/home/travis/WebDev/SandWACH/sandwach.py" ]; then
    SANDWACH_DIR="/home/travis/WebDev/SandWACH"
else
    echo "Error: Cannot find SandWACH directory"
    exit 1
fi
MAIN_PY="$SANDWACH_DIR/sandwach.py"
LOG_FILE="$SANDWACH_DIR/sandwach.log"
PID_FILE="$SANDWACH_DIR/sandwach.pid"

# Function to check if SandWACH is running
is_sandwach_running() {
    # First check if there's a running python3 sandwach.py process
    if pgrep -f "python3.*sandwach.py" > /dev/null 2>&1; then
        return 0  # Running
    fi
    
    # Also check PID file if it exists
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if ps -p "$PID" > /dev/null 2>&1; then
            return 0  # Running
        else
            rm -f "$PID_FILE"  # Remove stale PID file
        fi
    fi
    
    return 1  # Not running
}

# Function to start SandWACH
start_sandwach() {
    echo "Starting SandWACH..."
    
    # Check if the directory exists
    if [ ! -d "$SANDWACH_DIR" ]; then
        echo "Error: SandWACH directory not found: $SANDWACH_DIR"
        exit 1
    fi
    
    # Check if sandwach.py exists
    if [ ! -f "$MAIN_PY" ]; then
        echo "Error: sandwach.py not found at: $MAIN_PY"
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
    nohup python3 sandwach.py > "$LOG_FILE" 2>&1 &
    PID=$!
    
    # Wait a moment to get the actual process PID
    sleep 2
    # Find the python3 sandwach.py process
    ACTUAL_PID=$(pgrep -f "python3.*sandwach.py")
    if [ -n "$ACTUAL_PID" ]; then
        PID=$ACTUAL_PID
    fi
    
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
    # Try to find running processes
    RUNNING_PIDS=$(pgrep -f "python3.*sandwach.py")
    
    if [ -n "$RUNNING_PIDS" ]; then
        echo "Stopping SandWACH processes..."
        for PID in $RUNNING_PIDS; do
            if ps -p "$PID" > /dev/null 2>&1; then
                echo "Stopping SandWACH (PID: $PID)..."
                kill "$PID"
                sleep 2
                
                # Force kill if still running
                if ps -p "$PID" > /dev/null 2>&1; then
                    echo "Force killing SandWACH (PID: $PID)..."
                    kill -9 "$PID"
                fi
            fi
        done
        
        # Also clean up PID file if it exists
        if [ -f "$PID_FILE" ]; then
            rm -f "$PID_FILE"
        fi
        
        echo "SandWACH stopped"
    else
        echo "SandWACH is not running"
        # Clean up stale PID file if it exists
        if [ -f "$PID_FILE" ]; then
            rm -f "$PID_FILE"
        fi
    fi
}

# Function to show status
show_status() {
    if is_sandwach_running; then
        # Try to get PID from file first
        if [ -f "$PID_FILE" ]; then
            PID=$(cat "$PID_FILE")
        else
            # Get PID from process list
            PID=$(pgrep -f "python3.*sandwach.py")
        fi
        echo "SandWACH is running (PID: $PID)"
        echo "Log file: $LOG_FILE"
        echo "Directory: $SANDWACH_DIR"
    else
        echo "SandWACH is not running"
    fi
}

# Main script logic
case "${1:-check}" in
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
        echo "  check   - Check if running, start if not (default action)"
        echo ""
        echo "Default action: check (auto-start if not running)"
        exit 1
        ;;
esac