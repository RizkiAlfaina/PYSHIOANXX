# Physiological Anxiety Assessment — Alur Sistem dan Operasional

Dokumen ini menjelaskan alur sistem end-to-end dari page1.php hingga page6.php, termasuk referensi baris kode yang dijalankan, skrip kiosk untuk auto-start, serta cara menjalankan dan men-troubleshoot sistem.

## Ringkasan Arsitektur

- Mode kiosk membuka browser Chromium fullscreen ke `page1.php`.
- Server PHP built-in melayani halaman `page1.php` s/d `page6.php` dan endpoint API lokal.
- Page4 menginisiasi skrip sensor Python, membaca data dari file JSON `sensor_data.json`, menghitung rata-rata, lalu menyimpan ke `localStorage`.
- Page5 mengirim rata-rata (HR, GSR, ST) ke API model ML lokal `POST 127.0.0.1:5000/predict`.
- Page6 menampilkan kategori kecemasan serta metrik yang diukur.

## Auto-start Kiosk (Skrip)

- `/home/umudiyah/start_kiosk.sh`
	- Logging: line 5
	- Tunggu desktop siap: line 9
	- Set DISPLAY: line 12
	- Matikan screensaver/DPMS: lines 15–17
	- Sembunyikan kursor: line 20
	- Mulai web server (panggil `start_web_server.sh`): lines 23–24
	- Tunggu server: line 27
	- Tes `http://localhost:8000/page1.php`: lines 30–34
	- Tutup Chromium lama: line 37
	- Buka Chromium fullscreen ke `page1.php`: lines 41–50

- `/home/umudiyah/start_web_server.sh`
	- Kill PHP server lama: line 5
	- `cd` ke `SKRIPSI`: line 8
	- Jalankan `php -S localhost:8000`: line 9
	- Info server & path: lines 11–12

## Alur Halaman (dengan referensi baris)

### page1.php (halaman pembuka)

- Memuat Tailwind & font: lines 7–8
- Logo: lines 15–17
- Teks “PRESS”: line 19
- Tombol ke `page2.php`: lines 21–23
- Teks deskripsi: line 25
- Jam/tanggal/hari realtime (Asia/Jakarta):
	- Fungsi update: lines 40–65
	- Inisialisasi + interval 1 detik: lines 67–69

Navigasi: klik “CHECK” (line 21) → `page2.php`.

### page2.php (instruksi)

- Teks instruksi besar: lines 16–22
- Ilustrasi tangan: lines 25–27
- Navigasi:
	- Back ke `page1.php`: lines 31–33
	- Next ke `page3.php`: lines 35–37

Navigasi: klik “Next” (line 35) → `page3.php`.

### page3.php (preview kamera + START)

- Preview kamera (element video): lines 16–20
- Tombol “START” ke `page4.php`: lines 22–24
- Akses webcam (getUserMedia):
	- Ambil elemen: line 59
	- Minta izin kamera: lines 60–67
	- Fallback tidak didukung: lines 67–69

Navigasi: klik “START” (line 22) → `page4.php`.

### page4.php (pemindaian 60 detik + akuisisi sensor)

- UI video: lines 21–25
- Progress bar: lines 27–31
- Tiga metrik placeholder: lines 34–64
- Inisialisasi webcam: lines 68–73
- Variabel & status: lines 80–87
- Mulai sensor via backend:
	- `startSensorScript()` fetch `sensor_control.php?action=start`: lines 88–105 (request di line 89)
	- Flag `sensorStarted = true` saat sukses: lines 93–95
- Hentikan sensor: `stopSensorScript()` → `sensor_control.php?action=stop`: lines 107–120 (request di line 108)
- Ambil data sensor periodik (1 dtk): `updateSensorData()`
	- GET `read_sensor_data.php`: lines 124–126
	- Gunakan `result.data.current_reading`: lines 127–134
	- Push ke array jika valid: lines 136–138
	- Update tampilan angka: lines 141–143
	- Fallback tampil ‘-’: lines 145–156
- Hitung rata-rata utilitas: lines 160–164
- Selesaikan & redirect: `finishScanAndRedirect()`
	- Hentikan interval: lines 168–170
	- Panggil `stopSensorScript()`: lines 172–174
	- Hitung avg dari array: lines 176–178
	- Jika array kosong, baca avg final dari JSON via `read_sensor_data.php` dan simpan ke `localStorage`: lines 181–196 (redirect line 196)
	- Jika ada data, simpan avg ke `localStorage` dan redirect: lines 207–214
- Orkestrasi:
	- Mulai sensor, tunggu 3 dtk, mulai interval 1 dtk: lines 218–225
	- Progres bar ke 100%: line 232
	- Timer 60 dtk memicu selesai: line 235
	- Bersih-bersih saat unload: lines 238–242

### page5.php (tinjau rata-rata + kirim ke API prediksi)

- Preview kamera: lines 17–21; inisialisasi: lines 60–70
- Ambil nilai dari `localStorage` saat load dan tampilkan: lines 76–91
- Tombol RESULT: element lines 23–25; ref line 95
- `processAndRedirect()`:
	- Validasi data ada: lines 100–103
	- Ubah state tombol: lines 106–107
	- POST ke `http://127.0.0.1:5000/predict`: lines 109–121
	- Cek status HTTP: line 123
	- Parse JSON: line 125
	- Jika `predicted_label` ada → redirect ke `page6.php` dengan query `prediction`, `hr`, `st`, `gsr`: lines 127–132
	- Error handling & pulihkan tombol: lines 136–142
- Pasang event klik: lines 145–146

### page6.php (hasil kategori + tombol Home)

- Ambil parameter URL (XSS-safe): lines 5–8
- Tampilkan kategori: line 35
- Tampilkan metrik HR/GSR/ST: lines 45, 55, 65
- Tombol Home ke `page1.php`: element line 23
- Saat Home diklik: hapus `avgHeartRate`, `avgSkinConductance`, `avgSkinTemp` dari `localStorage` lalu redirect ke page1:
	- Listener & prevent default: lines 76–79
	- Hapus storage: lines 83–85
	- Redirect: line 90

## Endpoint Backend (PHP)

### read_sensor_data.php

- Header CORS/JSON: lines 2–5
- Path JSON: line 7 (`/home/umudiyah/pyshioanx/SKRIPSI/sensor_data.json`)
- Validasi keberadaan file: lines 9–17
- Baca file & validasi JSON: lines 19–39
- Response sukses: lines 41–46

### sensor_control.php

- Header CORS/JSON: lines 2–5
- Param aksi `?action=`: line 11 (`start|stop|status`)
- Path penting: JSON (line 12), skrip Python (line 13), PID (line 14)

- Action `start`: lines 17–58
	- Cek proses berjalan via PID file: lines 19–28
	- Reset file JSON awal: lines 31–38
	- Jalankan Python background dan ambil PID: lines 41–43
	- Simpan PID & response sukses: lines 45–51

- Action `stop`: lines 60–94
	- `kill -15`, cek berhenti, paksa `kill -9` jika perlu: lines 64–79
	- Hapus PID file & response: lines 67–71, 75–79

- Action `status`: lines 96–117
	- Cek proses & PID: lines 99–102
	- Cek keberadaan data: lines 104–109
	- Response status: lines 111–116

## Menjalankan Sistem

Prasyarat:
- Linux dengan desktop X11, Chromium/Chrome.
- PHP (built-in server sudah dipanggil oleh skrip).
- Python venv & skrip sensor tersedia sesuai path di `sensor_control.php`.
- Server API model ML berjalan di `127.0.0.1:5000` dengan endpoint `POST /predict`.

Opsi 1 — Mode kiosk (disarankan):

1) Jalankan skrip kiosk.

```bash
bash /home/umudiyah/start_kiosk.sh
```

2) Setelah 2–5 detik, Chromium akan membuka `http://localhost:8000/page1.php` fullscreen.

Opsi 2 — Manual (untuk debug):

1) Jalankan server PHP dari direktori `SKRIPSI`.

```bash
cd /home/umudiyah/pyshioanx/SKRIPSI
php -S localhost:8000
```

2) Buka browser ke `http://localhost:8000/page1.php`.

3) Pastikan server API ML aktif.

```bash
# Contoh umum (sesuaikan dengan proyek API ML Anda)
python your_ml_api_server.py
```

## Troubleshooting

- “Web server not responding” di log kiosk:
	- Cek `/tmp/php_server.log` dan pastikan port 8000 tidak terpakai.
- Page4 tidak menampilkan angka (tetap “-”):
	- Cek `sensor_control.php?action=status` di browser; pastikan `is_running=true` dan `has_data=true`.
	- Periksa file `sensor_data.json` diperbarui saat pemindaian.
- Page5 gagal memproses (“API Error”):
	- Pastikan API ML aktif di `127.0.0.1:5000/predict` dan menerima JSON `{HR, ST, GSR}`.
- Tombol Home di page6 tidak membersihkan data:
	- Pastikan klik memicu listener (lines 76–91) dan tidak diblokir oleh kebijakan browser.

## Catatan

- Waktu pemindaian default 60 detik (page4.php line 85) dan dapat disesuaikan.
- Data sementara disimpan di `localStorage` (page4 → page5 → page6). Dibersihkan saat menekan Home di page6.
- Semua rujukan baris berdasarkan file di repo saat tanggal dokumen ini dibuat.

---

# Migrasi Tailwind CSS Offline & Font Offline

## Ringkasan Migrasi

### 1. Tailwind CSS Offline
- Tailwind CSS diinstal secara lokal menggunakan CLI standalone (tanpa npm).
- File CSS hasil build: `assets/tailwind.css`.
- Semua file PHP (`page1.php` sampai `page6.php`) kini menggunakan:
  ```html
  <link href="assets/tailwind.css" rel="stylesheet">
  ```
- Untuk update CSS, jalankan:
  ```bash
  ./build-tailwind.sh
  ```

### 2. Font Offline
- File CSS font: `assets/fonts.css`.
- Menggunakan font Poppins dari system (local), fallback ke sans-serif.
- Semua file PHP kini menggunakan:
  ```html
  <link href="assets/fonts.css" rel="stylesheet">
  ```

### 3. File yang Diubah
- `page1.php`, `page2.php`, `page3.php`, `page4.php`, `page5.php`, `page6.php`
  - Menghapus import Tailwind CDN dan Google Fonts
  - Menambahkan link ke file CSS offline

### 4. File Tambahan
- `tailwindcss` (CLI executable)
- `tailwind.config.js` (konfigurasi Tailwind)
- `input.css` (input untuk build Tailwind)
- `assets/tailwind.css` (output CSS Tailwind)
- `assets/fonts.css` (definisi font offline)
- `build-tailwind.sh` (script build otomatis)

### 5. Cara Migrasi
1. Download Tailwind CLI sesuai arsitektur (ARM64 untuk Raspberry Pi):
   ```bash
   curl -sLO https://github.com/tailwindlabs/tailwindcss/releases/latest/download/tailwindcss-linux-arm64
   chmod +x tailwindcss-linux-arm64
   mv tailwindcss-linux-arm64 tailwindcss
   ```
2. Buat file konfigurasi dan input:
   - `tailwind.config.js`
   - `input.css` dengan `@import "tailwindcss";`
3. Build CSS:
   ```bash
   ./tailwindcss -i input.css -o assets/tailwind.css
   ```
4. Buat file font offline `assets/fonts.css` (gunakan system font atau tambahkan file .ttf jika ada).
5. Edit semua file PHP untuk menggunakan file CSS offline.

### 6. Catatan
- Tidak perlu koneksi internet untuk styling dan font.
- Untuk update class Tailwind, rebuild dengan script yang disediakan.

---

## Migrasi dari Nol (Download Resource → Build Offline) — Raspberry Pi/Linux tanpa npm

Panduan ini menjelaskan migrasi styling ke Tailwind CSS offline dan font offline mulai dari nol, termasuk mengunduh resource yang dibutuhkan.

### Prasyarat
- OS Linux (contoh: Raspberry Pi OS). Terminal dengan akses tulis di folder proyek.
- Perintah tersedia: `curl`, `chmod` (opsional: `unzip` jika mengekstrak font sendiri).
- PHP sudah terpasang (untuk melayani file `.php`).

### 1) Tentukan Arsitektur CPU dan Unduh Tailwind CLI
Identifikasi arsitektur untuk memilih binary yang tepat.

```bash
uname -m
```
Mapping umum:
- `aarch64` → gunakan `tailwindcss-linux-arm64`
- `armv7l` → gunakan `tailwindcss-linux-armv7`
- `x86_64` → gunakan `tailwindcss-linux-x64`

Contoh (Raspberry Pi 64-bit / aarch64):
```bash
cd /home/umudiyah/pyshioanx/SKRIPSI
curl -sLO https://github.com/tailwindlabs/tailwindcss/releases/latest/download/tailwindcss-linux-arm64
chmod +x tailwindcss-linux-arm64
mv tailwindcss-linux-arm64 tailwindcss
./tailwindcss -h  # verifikasi CLI berjalan
```
Jika muncul “Exec format error”, Anda mengunduh binary dengan arsitektur yang salah — unduh yang sesuai dengan hasil `uname -m`.

### 2) Siapkan Struktur dan File Dasar
Buat file konfigurasi dan input CSS untuk Tailwind.

```bash
mkdir -p assets/fonts
cat > tailwind.config.js << 'EOF'
/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./*.php", "./**/*.php", "./*.html"],
  theme: { extend: {} },
  plugins: [],
}
EOF

cat > input.css << 'EOF'
@import "tailwindcss";
EOF

# Build CSS Tailwind (sekali jalan)
./tailwindcss -i input.css -o assets/tailwind.css

# Opsional: build dengan minify
# ./tailwindcss -i input.css -o assets/tailwind.css -m

# Opsional: skrip watch untuk rebuild saat ada perubahan halaman
cat > build-tailwind.sh << 'EOF'
#!/bin/bash
set -euo pipefail
./tailwindcss -i input.css -o assets/tailwind.css --watch
EOF
chmod +x build-tailwind.sh
```
Output yang diharapkan: `assets/tailwind.css` terbuat tanpa error.

### 3) Siapkan Font Offline
Ada dua opsi, pilih salah satu:

- Opsi A — Menggunakan file font lokal (disarankan)
  1. Salin file font Poppins (format `.woff2` atau `.ttf`) ke `assets/fonts/`, misal:
     - `assets/fonts/Poppins-Thin.woff2` (200)
     - `assets/fonts/Poppins-Light.woff2` (300)
     - `assets/fonts/Poppins-Regular.woff2` (400)
     - `assets/fonts/Poppins-SemiBold.woff2` (600)
     - `assets/fonts/Poppins-Bold.woff2` (700)
  2. Buat `assets/fonts.css`:
     ```css
     /* assets/fonts.css */
     @font-face { font-family: 'Poppins'; src: url('assets/fonts/Poppins-Thin.woff2') format('woff2'); font-weight: 200; font-style: normal; font-display: swap; }
     @font-face { font-family: 'Poppins'; src: url('assets/fonts/Poppins-Light.woff2') format('woff2'); font-weight: 300; font-style: normal; font-display: swap; }
     @font-face { font-family: 'Poppins'; src: url('assets/fonts/Poppins-Regular.woff2') format('woff2'); font-weight: 400; font-style: normal; font-display: swap; }
     @font-face { font-family: 'Poppins'; src: url('assets/fonts/Poppins-SemiBold.woff2') format('woff2'); font-weight: 600; font-style: normal; font-display: swap; }
     @font-face { font-family: 'Poppins'; src: url('assets/fonts/Poppins-Bold.woff2') format('woff2'); font-weight: 700; font-style: normal; font-display: swap; }

     body { font-family: 'Poppins', sans-serif; background-color: #D7F3F9; }
     ```

- Opsi B — Mengandalkan system font (fallback cepat)
  Buat `assets/fonts.css` yang menggunakan `local()` sehingga memakai font Poppins jika sudah terpasang di OS, jika tidak akan fallback ke sans-serif:
  ```css
  /* assets/fonts.css */
  @font-face { font-family: 'Poppins'; src: local('Poppins'), local('Poppins-Regular'); font-weight: 400; font-style: normal; font-display: swap; }
  @font-face { font-family: 'Poppins'; src: local('Poppins Light'), local('Poppins-Light'); font-weight: 300; font-style: normal; font-display: swap; }
  @font-face { font-family: 'Poppins'; src: local('Poppins Thin'), local('Poppins-Thin'); font-weight: 200; font-style: normal; font-display: swap; }
  @font-face { font-family: 'Poppins'; src: local('Poppins SemiBold'), local('Poppins-SemiBold'); font-weight: 600; font-style: normal; font-display: swap; }
  @font-face { font-family: 'Poppins'; src: local('Poppins Bold'), local('Poppins-Bold'); font-weight: 700; font-style: normal; font-display: swap; }

  body { font-family: 'Poppins', sans-serif; background-color: #D7F3F9; }
  ```

Catatan: Opsi A menjamin font konsisten tanpa internet. Opsi B hanya berfungsi jika font tersedia di sistem.

### 4) Ubah Semua Halaman PHP untuk Offline
Di setiap `page1.php` sampai `page6.php`, di dalam `<head>`:
- Hapus baris CDN Tailwind dan import Google Fonts seperti:
  ```html
  <script src="https://cdn.tailwindcss.com"></script>
  <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:...');
    /* ... */
  </style>
  ```
- Tambahkan dua baris berikut:
  ```html
  <link href="assets/tailwind.css" rel="stylesheet">
  <link href="assets/fonts.css" rel="stylesheet">
  ```

Opsional (otomasi cepat, pastikan backup dulu):
```bash
# Contoh mengganti di page1.php (sesuaikan pola untuk file lain)
# Gunakan editor/IDE untuk kontrol lebih baik agar tidak menghapus style lain yang Anda perlukan.
```

### 5) Verifikasi
- Pastikan file `assets/tailwind.css` dan `assets/fonts.css` ada.
- Jalankan server PHP dan buka `http://localhost:8000/page1.php`.
- Cek tampilan: warna latar sesuai, komponen Tailwind bekerja, dan font Poppins terpakai.

### 6) Rebuild Saat Ada Perubahan Kelas Tailwind
Jika Anda menambah/mengubah class Tailwind di file `.php`, rebuild CSS:
```bash
# sekali jalan
./tailwindcss -i input.css -o assets/tailwind.css
# atau watch
./build-tailwind.sh
```

### Troubleshooting
- “Exec format error” saat menjalankan `./tailwindcss` → Unduh binary sesuai arsitektur (`uname -m`).
- “Permission denied” → `chmod +x tailwindcss` / `chmod +x build-tailwind.sh`.
- Style tidak berubah → `assets/tailwind.css` belum ter-update, jalankan rebuild; pastikan `content` di `tailwind.config.js` mencakup path `.php` Anda.
- Font tidak tampil → Periksa path dan nama file di `assets/fonts.css`. Gunakan format `woff2` jika tersedia. Pastikan `<link href="assets/fonts.css">` ada di `<head>` semua halaman.

### Status di Repo Ini
- File berikut sudah tersedia: `tailwindcss`, `tailwind.config.js`, `input.css`, `assets/tailwind.css`, `assets/fonts.css`.
- Semua halaman `page1.php`–`page6.php` sudah diarahkan ke CSS offline.
- Anda bisa langsung menggunakan, atau mengikuti langkah di atas untuk re-setup dari nol.

