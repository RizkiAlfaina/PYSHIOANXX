#!/bin/bash
# filepath: /home/umudiyah/start_kiosk.sh

# Logging
exec > /tmp/kiosk.log 2>&1
echo "Starting kiosk at $(date)"

# Tunggu desktop ready
sleep 3

# Set display
export DISPLAY=:0

# Disable screensaver
xset s off
xset -dpms
xset s noblank

# Hide mouse cursor
unclutter -idle 1 &

# Start web server
echo "Starting web server..."
/home/umudiyah/start_web_server.sh

# Wait for server to start
sleep 2

# Test server
if curl -s http://localhost:8000/page1.php > /dev/null; then
    echo "Web server is ready"
else
    echo "ERROR: Web server not responding"
fi

# Kill existing browser
pkill -f chromium-browser

# Start browser fullscreen
echo "Starting browser..."
chromium-browser \
    --kiosk \
    --no-sandbox \
    --disable-infobars \
    --disable-session-crashed-bubble \
    --disable-restore-session-state \
    --start-fullscreen \
    --no-first-run \
    --disable-default-apps \
    http://localhost:8000/page1.php &

echo "Kiosk started successfully"
