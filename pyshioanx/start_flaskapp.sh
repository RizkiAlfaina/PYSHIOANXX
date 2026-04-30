#!/bin/bash
# filepath: /home/umudiyah/pyshioanx/start_flaskapp.sh

# Log wrapper
exec >> /tmp/flaskapp.wrapper.log 2>&1
echo "Starting flaskapp (gunicorn) at $(date)"

# Optional: pakai venv
source /home/umudiyah/pyshioanx/.venv/bin/activate

# Masuk ke folder app
cd /home/umudiyah/pyshioanx/yolo/new || exit 1

# Hentikan instance lama (jika ada)
pkill -f "gunicorn.*flaskapp:app" || true
pkill -f "python.*flaskapp.py" || true

# Jalankan Gunicorn (Pi: hemat RAM -> -w 1)
gunicorn -w 1 -k gthread --threads 4 -b 0.0.0.0:5001 --timeout 120 \
  --access-logfile /tmp/flaskapp.access.log \
  --error-logfile /tmp/flaskapp.error.log \
  --pid /tmp/flaskapp.pid \
  flaskapp:app &

echo "Flask app (YOLO) started on port 5001. PID file: /tmp/flaskapp.pid"