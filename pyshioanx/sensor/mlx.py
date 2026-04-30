import time
import board
import busio
import adafruit_mlx90614

# --- Variabel Konfigurasi ---
waktu_baca = 1      # Atur jeda (detik) antara setiap pembacaan sensor
durasi_total = 60   # BARU: Atur total durasi (detik) program akan berjalan

# --- Inisialisasi Sensor ---
print("Menginisialisasi sensor MLX90614...")
try:
    i2c = busio.I2C(board.SCL, board.SDA)
    mlx = adafruit_mlx90614.MLX90614(i2c)
    print("Sensor MLX90614 berhasil diinisialisasi.")
except Exception as e:
    print(f"Gagal menginisialisasi MLX90614. Periksa kabel. Error: {e}")
    exit()

# DIUBAH: Pesan startup diperbarui untuk menyertakan total durasi
print(f"\nMembaca data suhu setiap {waktu_baca} detik selama {durasi_total} detik...")
print("-" * 40)

# --- Loop Utama ---
waktu_mulai = time.time()  # BARU: Catat waktu mulai program
try:
    while True:
        # BARU: Cek apakah durasi total telah terlampaui
        if time.time() - waktu_mulai > durasi_total:
            print(f"\nDurasi {durasi_total} detik telah tercapai. Program berhenti.")
            break # Keluar dari loop while

        try:
            ambient_temp = mlx.ambient_temperature
            object_temp = mlx.object_temperature

            # Tampilkan hasil
            print(f"Waktu: {time.strftime('%H:%M:%S')} | Suhu Objek: {object_temp:.2f} �C | Suhu Sekitar: {ambient_temp:.2f} �C")

        except Exception as e:
            print(f"Gagal membaca data suhu. Error: {e}")

        # Tunggu sesuai variabel waktu_baca
        time.sleep(waktu_baca)

except KeyboardInterrupt:
    print("\nProgram dihentikan oleh pengguna sebelum durasi selesai.")