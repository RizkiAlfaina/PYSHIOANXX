import time
import board
import busio
import digitalio
import adafruit_mlx90614
import adafruit_mcp3xxx.mcp3008 as MCP
from adafruit_mcp3xxx.analog_in import AnalogIn
import json
import os
from datetime import datetime

# Impor kelas HeartRateMonitor dari file heartrate_monitor.py
from heartrate_monitor import HeartRateMonitor

# ==================================================
# --- PENGATURAN UTAMA ---
# ==================================================
JUMLAH_PEMBACAAN = 100  # Jumlah total pembacaan yang diinginkan
INTERVAL_BACA = 1  # Jeda waktu antar pembacaan data (dalam detik)

# Path untuk menyimpan data di folder sensor (local storage)
LOCAL_DATA_DIR = "/home/umudiyah/pyshioanx/sensor/data"
# Buat folder data jika belum ada
os.makedirs(LOCAL_DATA_DIR, exist_ok=True)

# Generate filename dengan timestamp
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
JSON_OUTPUT_PATH = f"{LOCAL_DATA_DIR}/sensor_data_{timestamp}.json"
CSV_OUTPUT_PATH = f"{LOCAL_DATA_DIR}/sensor_data_{timestamp}.csv"

print(f"INFO: Data akan disimpan ke:")
print(f"  📄 JSON: {JSON_OUTPUT_PATH}")
print(f"  📊 CSV: {CSV_OUTPUT_PATH}")
print("="*70)

# --- Inisialisasi Heart Rate Monitor (MAX30102) ---
print("INFO: Menginisialisasi sensor Detak Jantung (MAX30102)...")
hrm = HeartRateMonitor(print_result=False)

# --- Inisialisasi Sensor Suhu (MLX90614) ---
print("INFO: Menginisialisasi sensor Suhu (MLX90614)...")
try:
    i2c = busio.I2C(board.SCL, board.SDA)
    mlx = adafruit_mlx90614.MLX90614(i2c)
    print("INFO: Sensor Suhu berhasil diinisialisasi.")
except Exception as e:
    print(f"ERROR: Gagal menginisialisasi MLX90614. Periksa kabel. Error: {e}")
    exit()

# --- Inisialisasi Sensor GSR (MCP3008) ---
print("INFO: Menginisialisasi sensor GSR (MCP3008)...")
try:
    # Membuat objek SPI bus
    spi = busio.SPI(clock=board.SCK, MISO=board.MISO, MOSI=board.MOSI)
    
    # Membuat objek chip select (CS) menggunakan pin GPIO 8 (Pin 24)
    cs = digitalio.DigitalInOut(board.D8)
    
    # Membuat objek MCP3008
    mcp = MCP.MCP3008(spi, cs)
    
    # Membuat channel input analog pada pin CH0 (Pin 1) dari MCP3008
    chan0 = AnalogIn(mcp, MCP.P0)
    print("INFO: Sensor GSR berhasil diinisialisasi.")
except Exception as e:
    print(f"ERROR: Gagal menginisialisasi MCP3008/GSR. Periksa kabel. Error: {e}")
    exit()

# --- Blok Utama ---
try:
    # Mulai sensor detak jantung di thread terpisah
    print("INFO: Memulai thread sensor Detak Jantung...")
    hrm.start_sensor()
    time.sleep(2) # Beri waktu agar sensor siap

    print("\n" + "="*70)
    print(f"🕒 PENGAMBILAN DATA DIMULAI - JUMLAH PEMBACAAN: {JUMLAH_PEMBACAAN}")
    print(f"📊 Interval pembacaan: {INTERVAL_BACA} detik")
    print("Tekan Ctrl+C untuk berhenti lebih awal.")
    print("="*70 + "\n")
    
    waktu_mulai = time.time()
    start_time_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Variabel untuk menyimpan data
    data_bpm = []
    data_suhu = []
    data_gsr = []
    data_tegangan = []
    data_resistansi = []
    
    # Variabel untuk menyimpan semua pembacaan real-time
    all_readings = []
    
    # Header untuk CSV
    csv_header = "timestamp,waktu_detik,heart_rate_bpm,skin_temperature_celsius,skin_conductance_uS,voltage_V,resistance_ohm,gsr_status\n"
    
    # Tulis header CSV
    try:
        with open(CSV_OUTPUT_PATH, 'w') as csv_file:
            csv_file.write(csv_header)
    except Exception as e:
        print(f"Warning: Gagal membuat file CSV: {e}")
    
    pembacaan_ke = 0
    
    # Loop utama untuk membaca data sebanyak JUMLAH_PEMBACAAN
    while pembacaan_ke < JUMLAH_PEMBACAAN:
        waktu_sekarang = time.time() - waktu_mulai
        pembacaan_ke += 1
        
        # 1. Ambil data suhu dari MLX90614
        object_temp = mlx.object_temperature
        
        # 2. Ambil data BPM terakhir dari thread HeartRateMonitor
        current_bpm = hrm.bpm
        
        # Cek apakah sensor masih terdeteksi aktif (tambah validasi)
        reading_info = hrm.get_reading()
        if not reading_info['finger_detected']:
            current_bpm = 0  # Reset ke 0 jika tidak ada jari yang terdeteksi
        
        # Batasi BPM maksimal 120
        if current_bpm > 120:
            current_bpm = 120
        
        bpm_display = f"{current_bpm:.2f}" if current_bpm > 0 else 0
        
        # 3. Ambil data GSR dari MCP3008
        sum_adc = 0
        
        # Ambil 10 kali pembacaan untuk mendapatkan nilai rata-rata yang stabil
        for _ in range(10):
            sum_adc += chan0.value # Baca nilai mentah ADC (0-65535)
            time.sleep(0.01) # Jeda 10 ms antar pembacaan

        # Hitung rata-rata nilai ADC
        gsr_average_adc = sum_adc / 10
        
        # Konversi nilai rata-rata ADC ke Tegangan
        voltage = (gsr_average_adc * mcp.reference_voltage) / 65535.0
        
        # Hitung resistansi dan konduktansi GSR
        if voltage > 0:
            resistansi = (3.3 - voltage) * 200000 / voltage
            konduktansi = 1.0 / resistansi
            konduktansi_uS = konduktansi * 1000000
        else:
            resistansi = float('inf')
            konduktansi_uS = 0

        # Menentukan status GSR berdasarkan rentang konduktansi (μS)
        if 0 <= konduktansi_uS <= 1.25:
            gsr_status = "Normal"
        elif 1.25 < konduktansi_uS <= 2.50:
            gsr_status = "Menengah"
        elif 2.50 < konduktansi_uS <= 3.75:
            gsr_status = "Tinggi"
        elif 3.75 < konduktansi_uS <= 5.00:
            gsr_status = "Sangat Tinggi"
        else:
            gsr_status = "Di luar rentang"
        
        # 4. Simpan data untuk perhitungan rata-rata (hanya jika tidak ada yang bernilai 0)
        if current_bpm > 0 and object_temp > 0 and konduktansi_uS > 0 and voltage > 0 and resistansi != float('inf'):
            data_bpm.append(current_bpm)
            data_suhu.append(object_temp)
            data_gsr.append(konduktansi_uS)
            data_tegangan.append(voltage)
            data_resistansi.append(resistansi)
        
        # 5. Simpan data dengan timestamp
        current_time = time.strftime('%H:%M:%S')
        
        # Data untuk JSON
        reading_data = {
            "timestamp": current_time,
            "waktu_detik": round(waktu_sekarang, 1),
            "pembacaan_ke": pembacaan_ke,
            "heart_rate": current_bpm,
            "skin_temperature": round(object_temp, 2),
            "skin_conductance": round(konduktansi_uS, 3),
            "voltage": round(voltage, 3),
            "resistance": round(resistansi, 0) if resistansi != float('inf') else 0,
            "gsr_status": gsr_status
        }
        all_readings.append(reading_data)
        
        # Tulis ke CSV secara real-time
        try:
            resistance_value = resistansi if resistansi != float('inf') else 0
            csv_line = f"{current_time},{waktu_sekarang:.1f},{current_bpm},{object_temp:.2f},{konduktansi_uS:.3f},{voltage:.3f},{resistance_value:.0f},{gsr_status}\n"
            with open(CSV_OUTPUT_PATH, 'a') as csv_file:
                csv_file.write(csv_line)
        except Exception as e:
            print(f"Warning: Gagal menulis ke CSV: {e}")
        
        # Tampilkan progress dan data di terminal
        sisa_pembacaan = JUMLAH_PEMBACAAN - pembacaan_ke
        progress = (pembacaan_ke / JUMLAH_PEMBACAAN) * 100
        
        print(f"📍 Pembacaan #{pembacaan_ke} | Waktu: {current_time} | Sisa: {sisa_pembacaan} pembacaan | Progress: {progress:.1f}%")
        print(f"  💓 BPM: {bpm_display}")
        print(f"  🌡️ Suhu: {object_temp:.2f}°C")
        print(f"  ⚡ GSR: {konduktansi_uS:.3f} μS ({gsr_status})")
        print(f"  🔋 V: {voltage:.3f}V | R: {resistance_value:,.0f} Ω")
        print("-" * 50)
        
        # Tunggu sesuai interval sebelum pembacaan berikutnya
        time.sleep(INTERVAL_BACA)
    
    # === PERHITUNGAN RATA-RATA DAN SIMPAN HASIL FINAL ===
    end_time_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    print("\n" + "="*70)
    print("🏁 PENGAMBILAN DATA SELESAI!")
    print("📊 PERHITUNGAN HASIL RATA-RATA:")
    print("="*70)
    
    if len(data_bpm) > 0:
        rata_bpm = sum(data_bpm) / len(data_bpm)
        rata_suhu = sum(data_suhu) / len(data_suhu)
        rata_gsr = sum(data_gsr) / len(data_gsr)
        rata_tegangan = sum(data_tegangan) / len(data_tegangan)
        rata_resistansi = sum(data_resistansi) / len(data_resistansi)
        
        # Tentukan status rata-rata GSR
        if 0 <= rata_gsr <= 1.25:
            rata_gsr_status = "Normal"
        elif 1.25 < rata_gsr <= 2.50:
            rata_gsr_status = "Menengah"
        elif 2.50 < rata_gsr <= 3.75:
            rata_gsr_status = "Tinggi"
        elif 3.75 < rata_gsr <= 5.00:
            rata_gsr_status = "Sangat Tinggi"
        else:
            rata_gsr_status = "Di luar rentang"
        
        print(f"📊 Data valid: {len(data_bpm)} dari {pembacaan_ke} pembacaan")
        print(f"📊 Data invalid (diabaikan): {pembacaan_ke - len(data_bpm)}")
        print()
        print(f"💓 Rata-rata BPM: {rata_bpm:.2f}")
        print(f"🌡️ Rata-rata Suhu: {rata_suhu:.2f} °C")
        print(f"⚡ Rata-rata GSR: {rata_gsr:.3f} μS ({rata_gsr_status})")
        print(f"🔋 Rata-rata Tegangan: {rata_tegangan:.3f}V")
        print(f"🔋 Rata-rata Resistansi: {rata_resistansi:,.0f} Ohm")
        
        # Simpan hasil final ke JSON
        final_data = {
            "session_info": {
                "start_time": start_time_str,
                "end_time": end_time_str,
                "duration_seconds": waktu_sekarang,
                "total_readings": pembacaan_ke,
                "valid_readings": len(data_bpm),
                "invalid_readings": pembacaan_ke - len(data_bpm)
            },
            "averages": {
                "heart_rate": round(rata_bpm, 2),
                "skin_temperature": round(rata_suhu, 2),
                "skin_conductance": round(rata_gsr, 3),
                "voltage": round(rata_tegangan, 3),
                "resistance": round(rata_resistansi, 0),
                "gsr_status": rata_gsr_status
            },
            "raw_data": all_readings
        }
        
    else:
        print("⚠️ Tidak ada data valid untuk dihitung rata-ratanya.")
        print("   Semua pembacaan mengandung nilai 0 atau tidak valid.")
        
        # Data kosong
        final_data = {
            "session_info": {
                "start_time": start_time_str,
                "end_time": end_time_str,
                "duration_seconds": waktu_sekarang,
                "total_readings": pembacaan_ke,
                "valid_readings": 0,
                "invalid_readings": pembacaan_ke
            },
            "averages": None,
            "raw_data": all_readings
        }
    
    # Simpan ke JSON
    try:
        with open(JSON_OUTPUT_PATH, 'w') as f:
            json.dump(final_data, f, indent=2)
        print(f"\n✅ Data JSON berhasil disimpan ke: {JSON_OUTPUT_PATH}")
    except Exception as e:
        print(f"\n❌ Gagal menyimpan JSON: {e}")
    
    # Cek ukuran file
    try:
        json_size = os.path.getsize(JSON_OUTPUT_PATH) / 1024  # KB
        csv_size = os.path.getsize(CSV_OUTPUT_PATH) / 1024   # KB
        print(f"📁 Ukuran file JSON: {json_size:.1f} KB")
        print(f"📁 Ukuran file CSV: {csv_size:.1f} KB")
    except:
        pass
    
    print("="*70)

except KeyboardInterrupt:
    print("\n⏹️ Program dihentikan oleh pengguna sebelum selesai.")
    # Simpan data yang sudah terkumpul
    if 'all_readings' in locals() and all_readings:
        try:
            partial_data = {
                "session_info": {
                    "start_time": start_time_str if 'start_time_str' in locals() else "Unknown",
                    "end_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "duration_seconds": "Interrupted",
                    "total_readings": len(all_readings),
                    "status": "Interrupted by user"
                },
                "raw_data": all_readings
            }
            with open(JSON_OUTPUT_PATH, 'w') as f:
                json.dump(partial_data, f, indent=2)
            print(f"✅ Data parsial berhasil disimpan ke: {JSON_OUTPUT_PATH}")
        except Exception as e:
            print(f"❌ Gagal menyimpan data parsial: {e}")

except Exception as e:
    print(f"\n❌ ERROR: Terjadi kesalahan: {e}")

finally:
    # Pembersihan
    print("\n🧹 Membersihkan koneksi...")
    try:
        hrm.stop_sensor()
        print("✅ Heart rate monitor dihentikan")
    except:
        pass
    
    try:
        spi.deinit()
        print("✅ Koneksi SPI dibersihkan")
    except:
        pass
    
    print("🏁 Program selesai!")
    if 'JSON_OUTPUT_PATH' in locals():
        print(f"📄 Cek hasil di: {LOCAL_DATA_DIR}")