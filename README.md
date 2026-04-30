# PhysioAnx - Physiological Anxiety Assessment System

![PhysioAnx Logo](SKRIPSI/assets/logo.png)

## 📋 Deskripsi Sistem

PhysioAnx adalah sistem penilaian kecemasan berbasis data fisiologis yang menggunakan kombinasi sensor biometrik dan computer vision. Sistem ini mengintegrasikan:

- **Sensor Fisiologis**: Heart Rate (HR), Skin Temperature (ST), Galvanic Skin Response (GSR)
- **Computer Vision**: Deteksi ekspresi wajah menggunakan YOLO
- **Machine Learning**: Random Forest untuk klasifikasi tingkat kecemasan dengan metode late fusion

## 🏗️ Arsitektur Sistem

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Web Interface │    │   Sensor Data   │    │  YOLO Detection │
│   (PHP Pages)   │────│   Collection    │────│   (Port 5003)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │  Random Forest  │
                    │  Fusion Model   │
                    │   (Port 5002)   │
                    └─────────────────┘
                                 │
                    ┌─────────────────┐
                    │ Google Sheets   │
                    │   Database      │
                    └─────────────────┘
```

## 🚀 Instalasi dan Setup

### 1. Persiapan Environment

```bash
# Clone atau pastikan berada di direktori pyshioanx
cd /home/umudiyah/pyshioanx

# Install Python dependencies
pip install -r requirements.txt

# Pastikan PHP dan Apache/Nginx sudah terinstall untuk menjalankan web interface
```

### 2. Konfigurasi Google Sheets

- Pastikan file `pengumpulan/service_account.json` sudah ada
- Google Sheets URL sudah dikonfigurasi di `rf/rf.py`
- Spreadsheet memiliki kolom: Timestamp, HR, ST, GSR, Predicted Label, YOLO Data, YOLO Confidence, Voltage

### 3. Setup Hardware Sensor

- Pastikan sensor MAX30102 (Heart Rate), MLX90614 (Temperature), dan GSR terhubung
- Konfigurasi pin dan komunikasi sensor di folder `sensor/`

## 🔧 Menjalankan Sistem

### Metode 1: Otomatis (Recommended)

```bash
# Jalankan semua service sekaligus
./start_all_services.sh
```

### Metode 2: Manual

```bash
# 1. Start Random Forest API (Port 5002)
cd rf/
python rf.py

# 2. Start YOLO Detection Service (Port 5003)
cd ../yolo/
python yolo_detect_ori.py

# 3. Setup Web Server untuk PHP
# Pastikan Apache/Nginx mengarah ke folder SKRIPSI/
```

### Verifikasi Service

```bash
# Test Random Forest API
curl http://localhost:5002/

# Test YOLO Service
curl http://localhost:5003/api/yolo_status

# Test PHP Web Interface
# Buka browser: http://localhost/page1.php
```

## 📱 Alur Penggunaan Sistem

### 1. **Page1.php** - Halaman Utama
```
┌─────────────────────────────────────┐
│           🏠 HOME PAGE              │
│                                     │
│         [PhysioAnx Logo]            │
│                                     │
│            PRESS                    │
│           [CHECK]                   │
│      to assess anxiety category     │
│                                     │
│         🕐 Real-time Clock          │
│         📅 Current Date             │
│                                     │
│    by: Biomedical Engineering ITERA │
└─────────────────────────────────────┘
```

**Fungsi:**
- Display real-time clock (WIB timezone)
- Entry point ke sistem
- Clean localStorage saat kembali ke halaman ini

**Navigasi:** Klik `CHECK` → Page2.php

---

### 2. **Page2.php** - Halaman Instruksi
```
┌─────────────────────────────────────┐
│         📋 INSTRUCTIONS             │
│                                     │
│  ENSURE THE PATIENT                 │
│  PLACES THEIR HAND                  │
│  ON THE DETECTOR                    │
│  AREA AND LOOKS                     │
│  AT THE CAMERA                      │
│                                     │
│         [Hand Diagram]              │
│                                     │
│  [Back]  [Logo]  [Next]            │
└─────────────────────────────────────┘
```

**Fungsi:**
- Memberikan instruksi kepada pengguna
- Menampilkan diagram penempatan tangan
- Persiapan sebelum assessment

**Navigasi:** 
- `Back` → Page1.php
- `Next` → Assessment.php

---

### 3. **Assessment.php** - Proses Penilaian
```
┌─────────────────────────────────────┐
│         🎥 ASSESSMENT               │
│                                     │
│    ┌─────────────────────────┐     │
│    │                         │     │
│    │    📹 Video Stream      │     │
│    │  (localhost:5003/webapp)│     │
│    │                         │     │
│    └─────────────────────────┘     │
│                                     │
│  State 1: [START] Button            │
│  State 2: Progress Bar (60s)        │
│  State 3: [RESULT] Button           │
│                                     │
│   💓HR    🌡️SC    🌡️ST             │
│   [--]    [---]   [--]              │
└─────────────────────────────────────┘
```

#### **3.1 State 1: Standby**
- Menampilkan video stream dari YOLO service
- Tombol `START` tersedia
- Sensor data menampilkan "-"

#### **3.2 State 2: Scanning (60 detik)**
```
Flow Scanning:
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│ Klik START  │───▶│ Start YOLO  │───▶│Start Sensor │
└─────────────┘    └─────────────┘    └─────────────┘
         │                                    │
         ▼                                    ▼
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│Progress Bar │    │Collect Data │    │Real-time    │
│Animation    │────│Every 1s     │────│Display      │
│(60 seconds) │    │(after 3s)   │    │HR,ST,GSR    │
└─────────────┘    └─────────────┘    └─────────────┘
```

**Proses Detail:**
1. **POST** `http://localhost:5003/api/start_yolo_scan` - Start YOLO scanning
2. **PHP** `sensor_control.php?action=start` - Start sensor collection
3. **Timer** 60 detik dengan progress bar animation
4. **Interval** Setiap 1 detik: fetch data dari `read_sensor_data.php`
5. **Storage** Simpan readings untuk kalkulasi rata-rata

#### **3.3 State 3: Result Ready**
- Progress bar selesai (100%)
- Tombol `RESULT` tersedia
- Data sensor menampilkan nilai terakhir/rata-rata

---

### 4. **Proses Prediksi** (Klik RESULT)

```
RESULT Button Clicked
         │
         ▼
┌─────────────────────────────────────┐
│     🔄 PROCESSING STATE             │
│                                     │
│ 1. Validasi Data Sensor             │
│    ✓ HR, ST, GSR values             │
│                                     │
│ 2. Test YOLO Connectivity           │
│    GET localhost:5003/api/status    │
│                                     │
│ 3. Get YOLO Results                 │
│    GET localhost:5003/api/get_result│
│                                     │
│ 4. Test RF Connectivity             │
│    GET localhost:5002/              │
│                                     │
│ 5. Send Fusion Prediction           │
│    POST localhost:5002/predict      │
│                                     │
│ 6. Redirect to Page6                │
└─────────────────────────────────────┘
```

#### **API Request Flow:**

**4.1 YOLO Result Request:**
```json
GET http://localhost:5003/api/get_yolo_result

Response:
{
  "status": "success",
  "yolo_data": {
    "class_counts": [count0, count1, count2, count3],
    "avg_confidence": 0.xxx,
    "dominant_class_name": "normal/mild/moderate/severe"
  }
}
```

**4.2 Random Forest Prediction:**
```json
POST http://localhost:5002/predict

Request Body:
{
  "yolo_data": {
    "class_counts": [x, y, z, w],
    "avg_confidence": 0.xxx
  },
  "sensor_data": {
    "HR": 75.0,
    "ST": 36.5,
    "GSR": 0.123,
    "voltage": 3.3
  }
}

Response:
{
  "status": "success",
  "predicted_class": 1,
  "predicted_label": "mild to moderate",
  "rf_probabilities": [0.1, 0.7, 0.15, 0.05],
  "dnn_probabilities": [0.2, 0.6, 0.15, 0.05],
  "yolo_probabilities": [0.8, 0.1, 0.05, 0.05]
}
```

---

### 5. **Page6.php** - Hasil Akhir
```
┌─────────────────────────────────────┐
│        🎯 ANXIETY CATEGORY          │
│                                     │
│  [🏠] ← Home                [Logo] │
│                                     │
│        ANXIETY CATEGORY             │
│    ┌─────────────────────────┐     │
│    │                         │     │
│    │    MILD TO MODERATE     │     │
│    │                         │     │
│    └─────────────────────────┘     │
│                                     │
│   💓75    🌡️0.123   🌡️36.50       │
│   HR      SC        ST              │
└─────────────────────────────────────┘
```

**Parameter URL yang diterima:**
- `prediction`: Label hasil prediksi
- `hr`: Heart Rate (tanpa desimal)
- `st`: Skin Temperature (2 desimal)
- `gsr`: Galvanic Skin Response (3 desimal)
- `yolo_class`: Dominant class dari YOLO
- `yolo_confidence`: Confidence YOLO (3 desimal)
- `rf_confidence`: Confidence Random Forest (3 desimal)

**Fungsi:**
- Display hasil prediksi kecemasan
- Tampilkan data sensor yang digunakan
- Tombol Home untuk kembali ke Page1 (clear localStorage)

---

## 🔧 API Endpoints

### Random Forest Service (Port 5002)
```bash
# Health check
GET http://localhost:5002/
Response: "Random Forest Prediction API - Ready for YOLO + Sensor data fusion!"

# Prediction
POST http://localhost:5002/predict
Content-Type: application/json
Body: {yolo_data, sensor_data}
```

### YOLO Service (Port 5003)
```bash
# Start scanning
POST http://localhost:5003/api/start_yolo_scan

# Get status
GET http://localhost:5003/api/yolo_status

# Get results
GET http://localhost:5003/api/get_yolo_result

# Video stream
GET http://localhost:5003/webapp
```

### Sensor Control (PHP)
```bash
# Start sensor
GET sensor_control.php?action=start

# Stop sensor
GET sensor_control.php?action=stop

# Read data
GET read_sensor_data.php
```

## 📊 Data Flow

### 1. Sensor Data Collection
```
Hardware Sensors → Python Scripts → JSON Files → PHP Reader → Frontend Display
     │                   │              │           │              │
   MAX30102         sensor/*.py    sensor/data/   read_sensor_   assessment.php
   MLX90614                        *.json         data.php
   GSR Sensor
```

### 2. YOLO Detection
```
Camera → YOLO Model → Class Detection → Probability Distribution → Fusion Model
  │         │             │                    │                      │
Video    yolo.pt      4 Classes           [p0,p1,p2,p3]            rf.py
Stream              (0,1,2,3)           (normal→severe)
```

### 3. Machine Learning Pipeline
```
Sensor Data → DNN Model → Probabilities → Late Fusion → Random Forest → Final Prediction
     │           │            │              │              │              │
  [HR,ST,GSR] → model_terbaik → [p0,p1,p2,p3] → Concatenate → fusionrfmodel → Classification
                    .h5                              ↓              .pkl
                                               [DNN_probs +
                                                YOLO_probs]
```

### 4. Data Storage
```
Final Results → Google Sheets Database
     │               │
Prediction Data → [Timestamp, HR, ST, GSR, Label, YOLO_Data, Confidence, Voltage]
                        │
                  service_account.json
```

## 🚨 Troubleshooting

### Common Issues

**1. Service tidak berjalan:**
```bash
# Check port availability
netstat -tlnp | grep :5002
netstat -tlnp | grep :5003

# Restart services
./stop_all_services.sh
./start_all_services.sh
```

**2. Sensor tidak terbaca:**
```bash
# Check sensor connection
python sensor/main.py

# Check permission
sudo chmod +x sensor/*.py
```

**3. YOLO detection error:**
```bash
# Check camera
ls /dev/video*

# Test YOLO standalone
python yolo/yolo_detect_ori.py
```

**4. Google Sheets error:**
```bash
# Verify service account
cat pengumpulan/service_account.json

# Check spreadsheet URL in rf/rf.py
```

### Error Messages

| Error | Cause | Solution |
|-------|-------|----------|
| `YOLO service (port 5003) tidak dapat diakses` | YOLO service down | Run `python yolo/yolo_detect_ori.py` |
| `Random Forest service (port 5002) tidak dapat diakses` | RF service down | Run `python rf/rf.py` |
| `Request timeout` | Service hang | Restart services |
| `Data fisiologis tidak ditemukan` | Sensor not working | Check sensor connection |

## 📝 Maintenance

### Log Files
- Sensor data: `sensor/data/sensor_data_*.json`
- Console output dari masing-masing service
- Google Sheets untuk historical data

### Backup
```bash
# Backup sensor data
cp -r sensor/data/ backup/sensor_data_$(date +%Y%m%d)

# Backup models
cp -r rf/*.pkl pengumpulan/*.h5 backup/models_$(date +%Y%m%d)
```

