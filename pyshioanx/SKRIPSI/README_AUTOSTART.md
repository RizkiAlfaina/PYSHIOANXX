# Setup Autostart Web PHP di Raspberry Pi

Tutorial lengkap untuk setup autostart aplikasi web PHP [`SKRIPSI/page1.php`](SKRIPSI/page1.php ) saat Raspberry Pi dinyalakan.

## 📋 Prerequisites

- Raspberry Pi dengan Raspberry Pi OS
- Desktop environment (LXDE/LXDE-pi)
- Akses terminal/SSH

## 🚀 Step-by-Step Installation

### Step 1: Install PHP CLI

```bash
# Update sistem
sudo apt update && sudo apt upgrade -y

# Install PHP CLI untuk built-in server
sudo apt install php-cli -y

# Install dependencies tambahan
sudo apt install chromium-browser unclutter -y

# Verifikasi instalasi
php --version
```

### Step 2: Buat Script Web Server

```bash
# Buat script web server
nano /home/umudiyah/start_web_server.sh
```

Isi file dengan:

```bash
#!/bin/bash
# filepath: /home/umudiyah/start_web_server.sh

# Kill existing PHP server
pkill -f "php -S"

# Start PHP built-in server dari direktori project
cd /home/umudiyah/pyshioanx/SKRIPSI
php -S localhost:8000 > /tmp/php_server.log 2>&1 &

echo "Web server started at http://localhost:8000"
echo "Project running from: /home/umudiyah/pyshioanx/SKRIPSI"
```

```bash
# Buat executable
chmod +x /home/umudiyah/start_web_server.sh
```

### Step 3: Buat Script Kiosk Autostart

```bash
# Buat script kiosk
nano /home/umudiyah/start_kiosk.sh
```

Isi file dengan:

```bash
#!/bin/bash
# filepath: /home/umudiyah/start_kiosk.sh

# Logging untuk debugging
exec > /tmp/kiosk.log 2>&1
echo "Starting kiosk at $(date)"

# Tunggu desktop ready
sleep 20

# Set display environment
export DISPLAY=:0

# Disable screensaver dan power management
xset s off
xset -dpms
xset s noblank

# Hide mouse cursor setelah 1 detik inaktivitas
unclutter -idle 1 &

# Start web server
echo "Starting web server..."
/home/umudiyah/start_web_server.sh

# Wait for server to start
sleep 5

# Test server readiness
if curl -s http://localhost:8000/page1.php > /dev/null; then
    echo "Web server is ready"
else
    echo "ERROR: Web server not responding"
fi

# Kill existing browser instances
pkill -f chromium-browser

# Start browser dalam fullscreen kiosk mode
echo "Starting browser..."
chromium-browser \
    --kiosk \
    --no-sandbox \
    --disable-infobars \
    --disable-session-crashed-bubble \
    --disable-restore-session-state \
    --start-fullscreen \
    --no-first-run \
    --disable-default-apps \
    http://localhost:8000/page1.php &

echo "Kiosk started successfully"
```

```bash
# Buat executable
chmod +x /home/umudiyah/start_kiosk.sh
```

### Step 4: Test Manual

```bash
# Test web server
/home/umudiyah/start_web_server.sh

# Buka browser manual (jika sudah di desktop)
chromium-browser http://localhost:8000/page1.php

# Test script kiosk (di desktop environment)
/home/umudiyah/start_kiosk.sh
```

### Step 5: Setup Boot ke Desktop

```bash
# Set graphical target (desktop mode)
sudo systemctl set-default graphical.target

# Konfigurasi autologin dengan raspi-config
sudo raspi-config
```

**Di raspi-config:**
1. Pilih **System Options** (atau **Boot Options**)
2. Pilih **Boot / Auto Login**
3. Pilih **Desktop Autologin**
4. Finish dan reboot jika diminta

### Step 6: Setup Autostart Application

#### Opsi A: LXDE Autostart (Recommended)

```bash
# Buat directory jika belum ada
mkdir -p ~/.config/lxsession/LXDE-pi

# Edit file autostart
nano ~/.config/lxsession/LXDE-pi/autostart
```

Isi dengan:

```bash
# Default LXDE autostart commands
@lxpanel --profile LXDE-pi
@pcmanfm --desktop --profile LXDE-pi
@xscreensaver -no-splash

# Autostart kiosk application
@/home/umudiyah/start_kiosk.sh
```

#### Opsi B: Desktop Entry Autostart

```bash
# Buat directory autostart
mkdir -p ~/.config/autostart

# Buat desktop entry
nano ~/.config/autostart/kiosk.desktop
```

Isi dengan:

```ini
[Desktop Entry]
Type=Application
Name=Kiosk PHP Application
Comment=Auto-start PHP web application in kiosk mode
Exec=/home/umudiyah/start_kiosk.sh
Hidden=false
NoDisplay=false
X-GNOME-Autostart-enabled=true
```

### Step 7: Update Sensor Control Path

```bash
# Edit sensor control PHP
nano /home/umudiyah/pyshioanx/SKRIPSI/sensor_control.php
```

Pastikan path sudah benar:

```php
$json_file = '/home/umudiyah/pyshioanx/SKRIPSI/sensor_data.json';
$python_script = '/home/umudiyah/pyshioanx/sensor/mlx_max_gsr_copy.py';
$pid_file = '/home/umudiyah/pyshioanx/SKRIPSI/sensor_pid.txt';
```

### Step 8: Test Autostart

```bash
# Reboot untuk test autostart
sudo reboot
```

## 📂 Struktur File

```
/home/umudiyah/
├── start_web_server.sh          # Script untuk start PHP server
├── start_kiosk.sh               # Script untuk start kiosk mode
└── pyshioanx/
    └── SKRIPSI/
        ├── page1.php            # Landing page (autostart)
        ├── page2.php            # Page 2
        ├── page3.php            # Page 3
        ├── page4.php            # Scanning page (60 detik)
        ├── page5.php            # Results page
        ├── page6.php            # Final results
        ├── sensor_control.php   # API untuk control sensor
        ├── read_sensor_data.php # API untuk baca data sensor
        └── assets/
            └── logo.png         # Logo aplikasi
```

## 🎯 Hasil Akhir

Setelah setup selesai, ketika Raspberry Pi dihidupkan:

1. ✅ **Boot otomatis ke desktop**
2. ✅ **Start PHP server** dari direktori [`SKRIPSI`](SKRIPSI )
3. ✅ **Buka Chromium dalam fullscreen**
4. ✅ **Load page1.php langsung**
5. ✅ **Aplikasi siap digunakan tanpa keyboard/mouse**

**URL yang akan terbuka:** `http://localhost:8000/page1.php`

## 🛠️ Troubleshooting

### Jika Autostart Tidak Jalan

```bash
# Cek log kiosk
cat /tmp/kiosk.log

# Cek log PHP server
cat /tmp/php_server.log

# Cek boot target
systemctl get-default

# Cek autostart file
cat ~/.config/lxsession/LXDE-pi/autostart
```

### Jika Web Server Error

```bash
# Test manual web server
cd /home/umudiyah/pyshioanx/SKRIPSI
php -S localhost:8000

# Cek file ada
ls -la /home/umudiyah/pyshioanx/SKRIPSI/page1.php

# Test akses
curl http://localhost:8000/page1.php
```

### Jika Browser Tidak Muncul

```bash
# Test display
export DISPLAY=:0
echo $DISPLAY

# Test browser manual
chromium-browser http://localhost:8000/page1.php

# Cek process running
ps aux | grep chromium
ps aux | grep php
```

### Reset/Stop Autostart

```bash
# Temporary disable autostart
mv ~/.config/lxsession/LXDE-pi/autostart ~/.config/lxsession/LXDE-pi/autostart.backup

# Stop running processes
pkill -f chromium-browser
pkill -f "php -S"

# Re-enable autostart
mv ~/.config/lxsession/LXDE-pi/autostart.backup ~/.config/lxsession/LXDE-pi/autostart
```

## 🔧 Kustomisasi

### Mengubah Port Web Server

Edit [`start_web_server.sh`](start_web_server.sh ):

```bash
# Ubah port dari 8000 ke port lain (misal 9000)
php -S localhost:9000 > /tmp/php_server.log 2>&1 &
```

Dan update URL di [`start_kiosk.sh`](start_kiosk.sh ):

```bash
http://localhost:9000/page1.php
```

### Mengubah Starting Page

Edit [`start_kiosk.sh`](start_kiosk.sh ):

```bash
# Ubah page1.php ke halaman lain
http://localhost:8000/page2.php
```

### Mengubah Browser Options

Edit [`start_kiosk.sh`](start_kiosk.sh ), tambahkan options:

```bash
chromium-browser \
    --kiosk \
    --no-sandbox \
    --disable-infobars \
    --start-fullscreen \
    --disable-features=TranslateUI \
    --disable-popup-blocking \
    http://localhost:8000/page1.php &
```

## 📞 Support

Jika mengalami masalah:

1. **Cek log files** di [`/tmp/kiosk.log`](/tmp/kiosk.log ) dan [`/tmp/php_server.log`](/tmp/php_server.log )
2. **Test manual** semua script sebelum autostart
3. **Pastikan permissions** file executable (`chmod +x`)
4. **Verifikasi path** file dan direktori

---

**Created by:** Umudiyah  
**Date:** August 2025  
**Version:** 1.0
