#!/bin/bash

echo "🧪 Testing Sensor Control API..."

cd /home/umudiyah/pyshioanx/SKRIPSI

echo "📍 Testing Status..."
php -r "parse_str('action=status', \$_GET); ob_start(); include 'sensor_control.php'; echo ob_get_clean();"

echo ""
echo "🚀 Testing Start..."
php -r "parse_str('action=start', \$_GET); ob_start(); include 'sensor_control.php'; echo ob_get_clean();"

echo ""
echo "⏳ Waiting 5 seconds..."
sleep 5

echo ""
echo "📊 Checking data file..."
if [ -f "sensor_data.json" ]; then
    echo "✅ JSON file exists:"
    head -20 sensor_data.json
else
    echo "❌ JSON file not found"
fi

echo ""
echo "🛑 Testing Stop..."
php -r "parse_str('action=stop', \$_GET); ob_start(); include 'sensor_control.php'; echo ob_get_clean();"

echo ""
echo "🏁 Test completed!"
