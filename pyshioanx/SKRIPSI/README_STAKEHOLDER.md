# Panduan Singkat untuk Stakeholder

Dokumen ini menjelaskan secara ringkas bagaimana sistem penilaian kecemasan fisiologis berjalan, ditujukan untuk pemangku kepentingan non-teknis.

## Apa yang dilakukan sistem ini?

- Membantu mengevaluasi kategori kecemasan seseorang berdasarkan tiga sinyal fisiologis:
  - Heart Rate (HR) — detak jantung
  - Skin Conductance (GSR) — konduktansi kulit
  - Skin Temperature (ST) — suhu kulit
- Proses berjalan otomatis di layar kiosk: mulai dari instruksi, pemindaian 60 detik, hingga menampilkan hasil.

## Alur Penggunaan (dari sudut pandang pengguna)

1. Halaman awal (Page 1)
   - Layar menampilkan tombol “CHECK”. Pengguna menekan tombol untuk memulai.
2. Instruksi (Page 2)
   - Petunjuk untuk meletakkan tangan pada alat dan melihat ke kamera.
3. Persiapan (Page 3)
   - Kamera menyala. Pengguna menekan “START”.
4. Pemindaian (Page 4)
   - Sistem merekam sinyal selama ±60 detik. Indikator progres berjalan otomatis.
5. Proses Hasil (Page 5)
   - Nilai rata-rata ketiga sinyal diproses oleh model AI lokal.
   - Setelah selesai, otomatis diarahkan ke hasil.
6. Hasil (Page 6)
   - Menampilkan kategori kecemasan dan nilai HR, GSR, ST.
   - Tombol “Home” untuk kembali ke awal dan memulai peserta berikutnya.

## Perangkat dan Komponen

- Layar sentuh atau monitor dengan browser (Chromium) dalam mode penuh (kiosk)
- Sensor fisiologis terhubung ke komputer (HR, GSR, ST)
- Aplikasi web lokal (halaman Page 1–6) dan model AI lokal untuk prediksi

## Operasional Harian

- Perangkat akan otomatis menyalakan server dan membuka aplikasi layar penuh.
- Petugas hanya perlu memastikan sensor terpasang dan siap pakai.
- Pengguna mengikuti petunjuk di layar; tidak diperlukan input manual selain menekan tombol.

## Hasil dan Privasi

- Hasil ditampilkan di layar dan digunakan untuk tujuan asesmen.
- Data sementara dihapus saat kembali ke halaman awal.
- Sistem berjalan sepenuhnya lokal (tanpa internet), sehingga data tidak dikirim ke cloud.

## Jika Terjadi Masalah

- Jika layar tidak menampilkan aplikasi, minta petugas teknis memeriksa koneksi sensor dan menyalakan ulang perangkat.
- Jika hasil tidak muncul, lakukan ulang proses dari awal (tekan Home) atau hubungi petugas teknis.

## Kontak

- Tim Teknik Biomedis ITERA
