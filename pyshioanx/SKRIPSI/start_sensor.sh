#!/bin/bash

# Script untuk menjalankan sensor Python dan menyiapkan data untuk web interface
# File: start_sensor.sh

echo "🚀 Memulai sistem pembacaan sensor..."

# Path ke script Python
PYTHON_SCRIPT="/home/umudiyah/pyshioanx/sensor/mlx_max_gsr_copy.py"
JSON_OUTPUT="/home/umudiyah/pyshioanx/SKRIPSI/sensor_data.json"

# Hapus file JSON lama jika ada
if [ -f "$JSON_OUTPUT" ]; then
    echo "🗑️ Menghapus data sensor lama..."
    rm "$JSON_OUTPUT"
fi

# Buat file JSON kosong untuk inisialisasi
echo "📝 Membuat file data sensor..."
cat > "$JSON_OUTPUT" << EOF
{
  "current_reading": null,
  "total_readings": 0,
  "duration": 60,
  "is_complete": false
}
EOF

echo "✅ File data sensor berhasil dibuat: $JSON_OUTPUT"

# Jalankan script Python dengan virtual environment
echo "🔄 Mengaktifkan virtual environment dan menjalankan script pembacaan sensor..."
echo "⏱️ Scanning akan berlangsung selama 60 detik..."
echo "🌐 Silakan buka web interface untuk melihat data real-time"
echo ""

cd /home/umudiyah/pyshioanx
source .venv/bin/activate
cd sensor
python3 "$PYTHON_SCRIPT"

echo ""
echo "✅ Pembacaan sensor selesai!"
echo "📊 Data telah disimpan ke: $JSON_OUTPUT"
echo "🌐 Data siap digunakan oleh web interface"
