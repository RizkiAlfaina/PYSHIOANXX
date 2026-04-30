#!/bin/bash
# filepath: /home/umudiyah/pyshioanx/start_all_services.sh

# Log wrapper untuk debugging
exec >> /tmp/integrated_services.wrapper.log 2>&1
echo "Starting integrated YOLO + RF services at $(date)"

# Aktivasi virtual environment
source /home/umudiyah/pyshioanx/.venv/bin/activate

# Function untuk membersihkan proses lama
cleanup_old_processes() {
    echo "Cleaning up old processes..."
    pkill -f "python.*flaskapp.py" || true
    pkill -f "python.*rf.py" || true
    pkill -f "gunicorn.*flaskapp:app" || true
    pkill -f "gunicorn.*rf:app" || true
    pkill -f "python.*deploy2.py" || true  # Cleanup deploy2.py juga
    sleep 2
}

# Bersihkan proses lama terlebih dahulu
cleanup_old_processes

# === START YOLO SERVICE (Port 5003) ===
echo "Starting YOLO Flask service on port 5003..."

# Masuk ke folder YOLO
cd /home/umudiyah/pyshioanx/yolo/new || exit 1

# Jalankan YOLO service dengan Gunicorn (seperti start_flaskapp.sh)
gunicorn -w 1 -k gthread --threads 2 -b 0.0.0.0:5003 --timeout 120 \
  --access-logfile /tmp/yolo_service.access.log \
  --error-logfile /tmp/yolo_service.error.log \
  --pid /tmp/yolo_service.pid \
  flaskapp:app &

echo "YOLO Flask service started on port 5003. PID file: /tmp/yolo_service.pid"

# === START RANDOM FOREST SERVICE (Port 5002) ===
echo "Starting Random Forest service on port 5002..."

# Masuk ke folder RF
cd /home/umudiyah/pyshioanx/rf || exit 1

# Jalankan RF service dengan Gunicorn
gunicorn -w 1 -k gthread --threads 2 -b 0.0.0.0:5002 --timeout 120 \
  --access-logfile /tmp/rf_service.access.log \
  --error-logfile /tmp/rf_service.error.log \
  --pid /tmp/rf_service.pid \
  rf:app &

echo "Random Forest service started on port 5002. PID file: /tmp/rf_service.pid"

# Kembali ke direktori utama
cd /home/umudiyah/pyshioanx

echo ""
echo "✅ All integrated services started successfully!"
echo "📍 Services running:"
echo "   - YOLO Flask service: http://localhost:5003 (PID: /tmp/yolo_service.pid)"
echo "   - Random Forest service: http://localhost:5002 (PID: /tmp/rf_service.pid)"
echo ""
echo "📋 Log files:"
echo "   - YOLO access: /tmp/yolo_service.access.log"
echo "   - YOLO error: /tmp/yolo_service.error.log"
echo "   - RF access: /tmp/rf_service.access.log"
echo "   - RF error: /tmp/rf_service.error.log"
echo "   - Wrapper: /tmp/integrated_services.wrapper.log"
echo ""
echo "🛑 To stop services, run: ./stop_all_services.sh"