import time
import board
import busio
import digitalio
import adafruit_mlx90614
import adafruit_mcp3xxx.mcp3008 as MCP
from adafruit_mcp3xxx.analog_in import AnalogIn
import json
import os

# Impor kelas HeartRateMonitor dari file heartrate_monitor.py
from heartrate_monitor import HeartRateMonitor

# ==================================================
# --- PENGATURAN UTAMA ---
# Ubah nilai variabel di bawah ini sesuai kebutuhan
# ==================================================
DURASI_TOTAL = 60  # Durasi total program berjalan (dalam detik)
INTERVAL_BACA = 1  # Jeda waktu antar pembacaan data (dalam detik)
JSON_OUTPUT_PATH = "/home/umudiyah/pyshioanx/SKRIPSI/sensor_data.json"  # Path untuk menyimpan data JSON
# ==================================================

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
    print(f"INFO: Membaca data setiap {INTERVAL_BACA} detik selama {DURASI_TOTAL} detik.")
    print("Tekan Ctrl+C untuk berhenti lebih awal.")
    print("="*70 + "\n")
    
    waktu_mulai = time.time()
    
    # Variabel untuk menyimpan data untuk perhitungan rata-rata
    data_bpm = []
    data_suhu = []
    data_gsr = []
    data_tegangan = []
    data_resistansi = []
    
    # Variabel untuk menyimpan semua pembacaan real-time (untuk PHP)
    all_readings = []
    
    # Loop utama untuk membaca data
    while time.time() - waktu_mulai <= DURASI_TOTAL:
        # 1. Ambil data suhu dari MLX90614
        object_temp = mlx.object_temperature
        
        # 2. Ambil data BPM terakhir dari thread HeartRateMonitor
        current_bpm = hrm.bpm
        
        # Batasi BPM maksimal 150
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
        
        # 5. Tampilkan data gabungan dan simpan timestamp
        current_time = time.strftime('%H:%M:%S')
        
        # Simpan semua pembacaan untuk PHP (termasuk yang bernilai 0)
        reading_data = {
            "timestamp": current_time,
            "heart_rate": current_bpm,
            "skin_temperature": round(object_temp, 2),
            "skin_conductance": round(konduktansi_uS, 3),
            "voltage": round(voltage, 3),
            "resistance": round(resistansi, 0) if resistansi != float('inf') else 0,
            "gsr_status": gsr_status
        }
        all_readings.append(reading_data)
        
        # Update file JSON secara real-time untuk PHP
        json_data = {
            "current_reading": reading_data,
            "total_readings": len(all_readings),
            "duration": DURASI_TOTAL,
            "is_complete": False
        }
        
        try:
            with open(JSON_OUTPUT_PATH, 'w') as f:
                json.dump(json_data, f, indent=2)
        except Exception as e:
            print(f"Warning: Gagal menulis ke file JSON: {e}")
        
        # Tampilkan data di terminal
        print(f"Waktu: {current_time}")
        print(f"  💓 BPM: {bpm_display}")
        print(f"  🌡️ Suhu Objek: {object_temp:.2f} °C")
        print(f"  ⚡ GSR: {konduktansi_uS:.3f} μS ({gsr_status})")
        print(f"  🔋 Tegangan: {voltage:.3f}V | Resistansi: {resistansi:,.0f} Ohm")
        print("-" * 50)
        
        # Tunggu sesuai interval sebelum pembacaan berikutnya
        time.sleep(INTERVAL_BACA)
    
    # === PERHITUNGAN RATA-RATA SETELAH LOOP SELESAI ===
    print("\n" + "="*70)
    print("HASIL RATA-RATA SELAMA PENGUKURAN:")
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
        
        print(f"📊 Data valid yang digunakan: {len(data_bpm)} dari {DURASI_TOTAL} pembacaan")
        print(f"📊 Data yang diabaikan (mengandung nilai 0): {DURASI_TOTAL - len(data_bpm)}")
        print()
        print(f"💓 Rata-rata BPM: {rata_bpm:.2f}")
        print(f"🌡️ Rata-rata Suhu Objek: {rata_suhu:.2f} °C")
        print(f"⚡ Rata-rata GSR: {rata_gsr:.3f} μS ({rata_gsr_status})")
        print(f"🔋 Rata-rata Tegangan: {rata_tegangan:.3f}V")
        print(f"🔋 Rata-rata Resistansi: {rata_resistansi:,.0f} Ohm")
        
        # Simpan hasil akhir ke file JSON
        final_data = {
            "current_reading": None,
            "total_readings": len(all_readings),
            "duration": DURASI_TOTAL,
            "is_complete": True,
            "averages": {
                "heart_rate": round(rata_bpm, 2),
                "skin_temperature": round(rata_suhu, 2),
                "skin_conductance": round(rata_gsr, 3),
                "voltage": round(rata_tegangan, 3),
                "resistance": round(rata_resistansi, 0),
                "gsr_status": rata_gsr_status
            },
            "valid_data_count": len(data_bpm),
            "invalid_data_count": DURASI_TOTAL - len(data_bpm),
            "all_readings": all_readings
        }
        
        try:
            with open(JSON_OUTPUT_PATH, 'w') as f:
                json.dump(final_data, f, indent=2)
            print(f"\n✅ Data berhasil disimpan ke: {JSON_OUTPUT_PATH}")
        except Exception as e:
            print(f"\n❌ Gagal menyimpan data ke file JSON: {e}")
            
    else:
        print("⚠️ Tidak ada data valid untuk dihitung rata-ratanya.")
        print("   Semua pembacaan mengandung nilai 0 atau tidak valid.")
        
        # Simpan data kosong ke JSON
        final_data = {
            "current_reading": None,
            "total_readings": len(all_readings),
            "duration": DURASI_TOTAL,
            "is_complete": True,
            "averages": None,
            "valid_data_count": 0,
            "invalid_data_count": DURASI_TOTAL,
            "all_readings": all_readings
        }
        
        try:
            with open(JSON_OUTPUT_PATH, 'w') as f:
                json.dump(final_data, f, indent=2)
            print(f"\n✅ Data (kosong) berhasil disimpan ke: {JSON_OUTPUT_PATH}")
        except Exception as e:
            print(f"\n❌ Gagal menyimpan data ke file JSON: {e}")
    
    print("="*70)

except KeyboardInterrupt:
    print("\nINFO: Program dihentikan oleh pengguna.")

except Exception as e:
    print(f"\nERROR: Terjadi kesalahan saat eksekusi: {e}")

finally:
    # Bagian ini akan selalu dieksekusi untuk memastikan pembersihan
    print("\nINFO: Menghentikan thread sensor Detak Jantung...")
    hrm.stop_sensor()
    print("INFO: Membersihkan koneksi SPI...")
    try:
        spi.deinit()
    except:
        pass
    print("INFO: Semua sensor telah berhenti. Program selesai.")
