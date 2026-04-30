#!/bin/bash
# filepath: /home/umudiyah/start_web_server.sh

# Kill existing PHP server
pkill -f "php -S"

# Start PHP built-in server dari direktori project
cd /home/umudiyah/pyshioanx/SKRIPSI
php -S localhost:8000 > /tmp/php_server.log 2>&1 &

echo "Web server started at http://localhost:8000"
echo "Project running from: /home/umudiyah/pyshioanx/SKRIPSI"
