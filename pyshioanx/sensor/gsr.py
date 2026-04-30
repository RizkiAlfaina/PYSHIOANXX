import time
import busio
import digitalio
import board
import adafruit_mcp3xxx.mcp3008 as MCP
from adafruit_mcp3xxx.analog_in import AnalogIn

# ---- Inisialisasi Antarmuka SPI ----
# Membuat objek SPI bus
spi = busio.SPI(clock=board.SCK, MISO=board.MISO, MOSI=board.MOSI)

# Membuat objek chip select (CS) menggunakan pin GPIO 8 (Pin 24)
cs = digitalio.DigitalInOut(board.D8)

# Membuat objek MCP3008
# Pustaka akan otomatis menggunakan VDD (3.3V) sebagai tegangan referensi
mcp = MCP.MCP3008(spi, cs)

# Membuat channel input analog pada pin CH0 (Pin 1) dari MCP3008
chan0 = AnalogIn(mcp, MCP.P0)

print("Mulai membaca nilai GSR. Tekan CTRL+C untuk berhenti.")
print("-" * 40)

try:
    while True:
        # ---- Mirip dengan Arduino Loop ----
        sum_adc = 0
        
        # Ambil 10 kali pembacaan untuk mendapatkan nilai rata-rata yang stabil
        for _ in range(10):
            sum_adc += chan0.value # Baca nilai mentah ADC (0-65535)
            time.sleep(0.01) # Jeda 10 ms antar pembacaan

        # Hitung rata-rata nilai ADC
        gsr_average_adc = sum_adc / 10
        
        # Konversi nilai rata-rata ADC ke Tegangan
        # Pustaka sudah tahu tegangan referensi adalah 3.3V dari VDD
        voltage = (gsr_average_adc * mcp.reference_voltage) / 65535.0
        
        # Hindari error pembagian dengan nol jika tidak ada tegangan
        if voltage > 0:
            # Hitung resistansi dalam Ohm
            resistansi = (3.3 - voltage) * 200000 / voltage
            
            # Hitung konduktansi (kebalikan dari resistansi)
            konduktansi = 1.0 / resistansi
            
            # Konversi konduktansi ke microSiemens (�S)
            konduktansi_uS = konduktansi * 1000000
        else:
            resistansi = float('inf') # Resistansi tak terhingga jika tidak ada tegangan
            konduktansi_uS = 0

        # ---- Tampilkan semua hasil ----
        print(f"ADC Rata-rata: {int(gsr_average_adc)}")
        print(f"Tegangan (V): {voltage:.3f}")
        print(f"Resistansi (Ohm): {resistansi:,.2f}")
        print(f"Konduktansi (�S): {konduktansi_uS:.3f}")

        # Menentukan status berdasarkan rentang konduktansi (�S)
        if 0 <= konduktansi_uS <= 1.25:
            print("Status: Normal\n")
        elif 1.25 < konduktansi_uS <= 2.50:
            print("Status: Rentang Menengah\n")
        elif 2.50 < konduktansi_uS <= 3.75:
            print("Status: Rentang Tinggi\n")
        elif 3.75 < konduktansi_uS <= 5.00:
            print("Status: Rentang Sangat Tinggi\n")
        else:
            print("Status: Di luar rentang yang diharapkan\n")
            
        time.sleep(0.5) # Jeda setengah detik sebelum loop berikutnya

except KeyboardInterrupt:
    print("\nProgram dihentikan oleh pengguna.")
    spi.deinit()