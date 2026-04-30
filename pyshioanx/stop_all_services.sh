#!/bin/bash

# Script untuk menghentikan semua service dengan PID files (seperti start_flaskapp.sh)
# Usage: ./stop_all_services.sh

echo "🛑 Stopping all integrated services..."

# Function to stop service by PID file
stop_service_by_pidfile() {
    local pid_file=$1
    local service_name=$2
    
    if [ -f "$pid_file" ]; then
        local pid=$(cat "$pid_file")
        if kill -0 "$pid" 2>/dev/null; then
            echo "🔴 Stopping $service_name (PID: $pid)..."
            kill "$pid"
            sleep 3
            # Force kill if still running
            if kill -0 "$pid" 2>/dev/null; then
                echo "⚡ Force killing $service_name..."
                kill -9 "$pid"
            fi
            echo "✅ $service_name stopped"
        else
            echo "⚠️  $service_name (PID: $pid) was not running"
        fi
        rm -f "$pid_file"
    else
        echo "⚠️  No PID file found for $service_name"
    fi
}

# Stop services by PID files
stop_service_by_pidfile "/tmp/yolo_service.pid" "YOLO Flask service"
stop_service_by_pidfile "/tmp/rf_service.pid" "Random Forest service"

# Also cleanup any remaining processes (backup cleanup)
echo "🧹 Cleaning up any remaining processes..."
pkill -f "gunicorn.*flaskapp:app" 2>/dev/null || true
pkill -f "gunicorn.*rf:app" 2>/dev/null || true
pkill -f "python.*flaskapp.py" 2>/dev/null || true
pkill -f "python.*rf.py" 2>/dev/null || true

# Check if ports are freed
sleep 2
if ! lsof -Pi :5003 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo "✅ Port 5003 is now free"
else
    echo "⚠️  Port 5003 still in use"
fi

if ! lsof -Pi :5002 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo "✅ Port 5002 is now free"
else
    echo "⚠️  Port 5002 still in use"
fi

echo ""
echo "✅ All integrated services stopped successfully!"
echo "📋 Log files preserved in /tmp/ for debugging if needed"