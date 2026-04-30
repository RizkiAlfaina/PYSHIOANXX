#!/bin/bash

# Script untuk menjalankan service dengan pencegahan duplikasi yang lebih kuat
# Usage: ./start_services_robust.sh

echo "🚀 Starting services with robust duplication prevention..."

# Function to force kill all related processes
force_cleanup() {
    echo "🔥 Force cleaning up ALL related processes..."
    pkill -9 -f "python.*flaskapp.py" 2>/dev/null || true
    pkill -9 -f "python.*rf.py" 2>/dev/null || true
    pkill -9 -f "flaskapp.py" 2>/dev/null || true
    pkill -9 -f "rf.py" 2>/dev/null || true
    sleep 3
    
    # Double check - kill by port if still running
    YOLO_PIDS=$(lsof -ti:5003 2>/dev/null)
    RF_PIDS=$(lsof -ti:5002 2>/dev/null)
    
    if [ ! -z "$YOLO_PIDS" ]; then
        echo "🔥 Force killing processes on port 5003: $YOLO_PIDS"
        kill -9 $YOLO_PIDS 2>/dev/null || true
    fi
    
    if [ ! -z "$RF_PIDS" ]; then
        echo "🔥 Force killing processes on port 5002: $RF_PIDS"
        kill -9 $RF_PIDS 2>/dev/null || true
    fi
    
    sleep 2
}

# Function to check if any related processes are running
check_no_duplicates() {
    local count=$(ps aux | grep -E "(flaskapp|rf\.py)" | grep -v grep | wc -l)
    echo "📊 Found $count related processes running"
    return $count
}

# Aggressive cleanup first
force_cleanup

# Verify cleanup worked
if ! check_no_duplicates; then
    echo "✅ All processes cleaned up successfully"
else
    echo "❌ Some processes still running. Exiting to prevent conflicts."
    exit 1
fi

# Start services one by one with verification
VENV_PYTHON="/home/umudiyah/pyshioanx/.venv/bin/python"

echo "🎯 Starting YOLO Flask app on port 5003..."
cd /home/umudiyah/pyshioanx/yolo/new
$VENV_PYTHON flaskapp.py > /tmp/yolo.log 2>&1 &
YOLO_PID=$!
echo "YOLO started with PID: $YOLO_PID"

# Wait and verify YOLO started properly
sleep 8
if ! kill -0 $YOLO_PID 2>/dev/null; then
    echo "❌ YOLO failed to start. Check /tmp/yolo.log"
    exit 1
fi

# Check for duplicate YOLO processes
YOLO_COUNT=$(ps aux | grep -E "flaskapp" | grep -v grep | wc -l)
if [ $YOLO_COUNT -gt 1 ]; then
    echo "❌ Duplicate YOLO processes detected! Count: $YOLO_COUNT"
    exit 1
fi

echo "🌲 Starting Random Forest API on port 5002..."
cd /home/umudiyah/pyshioanx/rf
$VENV_PYTHON rf.py > /tmp/rf.log 2>&1 &
RF_PID=$!
echo "RF started with PID: $RF_PID"

# Wait and verify RF started properly
sleep 10
if ! kill -0 $RF_PID 2>/dev/null; then
    echo "❌ RF failed to start. Check /tmp/rf.log"
    exit 1
fi

# Final check for any duplicates
TOTAL_COUNT=$(ps aux | grep -E "(flaskapp|rf\.py)" | grep -v grep | wc -l)
if [ $TOTAL_COUNT -ne 2 ]; then
    echo "❌ Wrong number of processes running: $TOTAL_COUNT (expected 2)"
    ps aux | grep -E "(flaskapp|rf\.py)" | grep -v grep
    exit 1
fi

echo "✅ Both services started successfully without duplicates!"
echo "📍 Running processes:"
ps aux | grep -E "(flaskapp|rf\.py)" | grep -v grep

echo ""
echo "🌐 Services ready:"
echo "   - YOLO: http://localhost:5003"
echo "   - RF: http://localhost:5002"
echo ""
echo "📋 Logs:"
echo "   - YOLO: /tmp/yolo.log"
echo "   - RF: /tmp/rf.log"