# Integrasi Sensor dengan Web Interface

## Deskripsi
Sistem ini mengintegrasikan pembacaan sensor hardware (MAX30102, MLX90614, MCP3008) dengan web interface untuk menampilkan data physiological secara real-time.

## File yang Terlibat

### Backend (Python)
- `sensor/mlx_max_gsr_copy.py` - Script utama untuk membaca sensor
- `SKRIPSI/start_sensor.sh` - Script bash untuk memulai sistem

### Frontend (PHP/Web)
- `SKRIPSI/page4.php` - Halaman scanning (60 detik)
- `SKRIPSI/page5.php` - Halaman hasil rata-rata
- `SKRIPSI/page6.php` - Halaman prediksi anxiety
- `SKRIPSI/read_sensor_data.php` - API untuk membaca data sensor

### Data
- `SKRIPSI/sensor_data.json` - File untuk menyimpan data sensor real-time

## Cara Penggunaan

### 1. Persiapan Hardware
Pastikan semua sensor terhubung dengan benar:
- MAX30102 (Heart Rate) → I2C
- MLX90614 (Temperature) → I2C  
- MCP3008 (GSR) → SPI

### 2. Menjalankan Sistem

#### Opsi A: Manual
```bash
cd /home/umudiyah/pyshioanx/sensor
python3 mlx_max_gsr_copy.py
```

#### Opsi B: Menggunakan Script
```bash
cd /home/umudiyah/pyshioanx/SKRIPSI
./start_sensor.sh
```

### 3. Menggunakan Web Interface
1. Buka browser dan navigasi ke halaman web Anda
2. Mulai dari `page4.php` untuk scanning
3. Sistem akan:
   - Membaca data sensor setiap 1 detik selama 60 detik
   - Menampilkan data real-time di web interface
   - Menghitung rata-rata dari data valid
   - Menyimpan hasil ke file JSON

### 4. Flow Data
```
Hardware Sensors → Python Script → JSON File → PHP API → Web Interface
```

## Fitur

### Pembacaan Sensor Real-time
- **Heart Rate**: Dibaca dari MAX30102, dibatasi maksimal 150 BPM
- **Skin Temperature**: Dibaca dari MLX90614 dalam Celsius
- **Skin Conductance**: Dibaca dari MCP3008 dalam microSiemens

### Filtering Data
- Data dengan nilai 0 diabaikan dalam perhitungan rata-rata
- Pembacaan tetap disimpan untuk keperluan debugging
- Status GSR dikategorikan: Normal, Menengah, Tinggi, Sangat Tinggi

### Web Interface
- Progress bar menunjukkan scanning 60 detik
- Data ditampilkan real-time selama scanning
- Hasil rata-rata ditampilkan setelah selesai
- Integrasi dengan sistem prediksi anxiety

## File JSON Structure
```json
{
  "current_reading": {
    "timestamp": "14:30:15",
    "heart_rate": 75.2,
    "skin_temperature": 36.1,
    "skin_conductance": 0.456,
    "voltage": 0.123,
    "resistance": 150000,
    "gsr_status": "Normal"
  },
  "total_readings": 60,
  "duration": 60,
  "is_complete": true,
  "averages": {
    "heart_rate": 75.5,
    "skin_temperature": 36.0,
    "skin_conductance": 0.445,
    "voltage": 0.120,
    "resistance": 152000,
    "gsr_status": "Normal"
  },
  "valid_data_count": 57,
  "invalid_data_count": 3,
  "all_readings": [...]
}
```

## Troubleshooting

### Sensor Tidak Terdeteksi
- Periksa koneksi hardware
- Pastikan alamat I2C dan pin SPI benar
- Jalankan `i2cdetect -y 1` untuk cek I2C devices

### File JSON Tidak Ter-update
- Periksa permission folder SKRIPSI
- Pastikan path dalam script Python benar
- Cek log error di terminal

### Web Interface Tidak Menampilkan Data
- Pastikan `read_sensor_data.php` dapat diakses
- Cek browser console untuk error JavaScript
- Verifikasi path file JSON dalam PHP

### Data Tidak Akurat
- Pastikan sensor sudah stabil (tunggu 2-3 detik)
- Periksa kalibrasi sensor
- Verifikasi threshold filtering data

## Dependencies
- Python: `adafruit-circuitpython-mlx90614`, `adafruit-circuitpython-mcp3xxx`
- Hardware: Raspberry Pi dengan GPIO enabled
- Web Server: Apache/Nginx dengan PHP support
