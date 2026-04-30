import time
import board
import busio
import adafruit_mlx90614

# Impor kelas HeartRateMonitor dari file heartrate_monitor.py
from heartrate_monitor import HeartRateMonitor

# ==================================================
# --- PENGATURAN UTAMA ---
# Ubah nilai variabel di bawah ini sesuai kebutuhan
# ==================================================
DURASI_TOTAL = 60  # Durasi total program berjalan (dalam detik)
INTERVAL_BACA = 1  # Jeda waktu antar pembacaan data (dalam detik)
# ==================================================

# --- Inisialisasi Heart Rate Monitor (MAX30102) ---
print("INFO: Menginisialisasi sensor Detak Jantung (MAX30102)...")
# 'print_result' dimatikan agar output tidak ganda dan dikontrol dari script utama.
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

# --- Blok Utama ---
# Gunakan try...finally untuk memastikan sensor berhenti dengan benar
try:
    # Mulai sensor detak jantung di thread terpisah
    print("INFO: Memulai thread sensor Detak Jantung...")
    hrm.start_sensor()
    time.sleep(2) # Beri waktu agar sensor siap

    print("\n" + "="*50)
    print(f"INFO: Membaca data setiap {INTERVAL_BACA} detik selama {DURASI_TOTAL} detik.")
    print("Tekan Ctrl+C untuk berhenti lebih awal.")
    print("="*50 + "\n")
    
    waktu_mulai = time.time()
    
    # Loop utama untuk membaca data
    while time.time() - waktu_mulai <= DURASI_TOTAL:
        # 1. Ambil data suhu dari MLX90614
        object_temp = mlx.object_temperature
        
        # 2. Ambil data BPM terakhir dari thread HeartRateMonitor
        current_bpm = hrm.bpm
        
        # Format output agar lebih rapi saat BPM belum terdeteksi
        bpm_display = f"{current_bpm:.2f}" if current_bpm > 0 else 0
        
        # 3. Tampilkan data gabungan
        print(f"Waktu: {time.strftime('%H:%M:%S')} | ?? BPM: {bpm_display} | ??? Suhu Objek: {object_temp:.2f} �C")
        
        # Tunggu sesuai interval sebelum pembacaan berikutnya
        time.sleep(INTERVAL_BACA)

except KeyboardInterrupt:
    print("\nINFO: Program dihentikan oleh pengguna.")

except Exception as e:
    print(f"\nERROR: Terjadi kesalahan saat eksekusi: {e}")

finally:
    # Bagian ini akan selalu dieksekusi untuk memastikan pembersihan
    print("\nINFO: Menghentikan thread sensor Detak Jantung...")
    hrm.stop_sensor()
    print("INFO: Semua sensor telah berhenti. Program selesai.")