<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Scanning...</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="assets/fonts.css" rel="stylesheet">
    <style>
        body {
            font-family: sans-serif;
        }
        #progressBar {
            /* Progress bar akan terisi penuh dalam 60 detik secara mulus */
            transition: width 60s linear;
        }
    </style>
</head>
<body class="text-[#0D3D6F]"> 

    <div class="min-h-screen w-full flex items-center justify-center">

        <div class="w-full max-w-5xl flex flex-col items-center justify-around p-4 aspect-[1024/600]">

            <img src="assets/logo.png" alt="Logo" class="h-10">

            <div class="w-full max-w-lg flex flex-col items-center">
                <div class="aspect-video bg-black rounded-lg overflow-hidden shadow-md border border-slate-400">
                    <img src="http://localhost:5001/webapp" alt="Upload video" class="w-full h-full object-cover">
                </div>
                <div class="w-full mt-4">
                    <div class="w-full bg-sky-100 rounded-full h-3.5 shadow-inner">
                        <div id="progressBar" class="bg-[#B3E5FC] h-3.5 rounded-full" style="width: 0%"></div>
                    </div>
                    <p class="text-center text-lg mt-2 font-semibold">Scanning...</p>
                </div>
            </div>

            <div class="w-full max-w-lg flex flex-row justify-between text-center">
                <div class="flex flex-col items-center gap-y-1.5">
                    <div class="bg-[#B3E5FC] p-2 rounded-lg shadow w-24 h-12 flex items-center justify-center gap-1.5">
                        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 opacity-70" viewBox="0 0 20 20" fill="currentColor">
                            <path fill-rule="evenodd" d="M3.172 5.172a4 4 0 015.656 0L10 6.343l1.172-1.171a4 4 0 115.656 5.656L10 17.657l-6.828-6.829a4 4 0 010-5.656z" clip-rule="evenodd" />
                        </svg>
                        <p id="heartRate" class="font-bold text-base">-</p>
                    </div>
                    <p class="text-xs font-semibold">Heart Rate</p>
                </div>

                <div class="flex flex-col items-center gap-y-1.5">
                    <div class="bg-[#B3E5FC] p-2 rounded-lg shadow w-24 h-12 flex items-center justify-center gap-1.5">
                        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 opacity-70" viewBox="0 0 20 20" fill="currentColor">
                            <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM6.636 10.636a1 1 0 011.414 0L10 12.586l1.95-1.95a1 1 0 111.414 1.414l-2.657 2.657a1.5 1.5 0 01-2.121 0L6.636 12.05a1 1 0 010-1.414z" clip-rule="evenodd" />
                        </svg>
                        <p id="skinConductance" class="font-bold text-base">-</p>
                    </div>
                    <p class="text-xs font-semibold">Skin Conductance</p>
                </div>

                <div class="flex flex-col items-center gap-y-1.5">
                    <div class="bg-[#B3E5FC] p-2 rounded-lg shadow w-24 h-12 flex items-center justify-center gap-1.5">
                        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 opacity-70" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                            <path stroke-linecap="round" stroke-linejoin="round" d="M14.828 14.828a4 4 0 01-5.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                        </svg>
                        <p id="skinTemp" class="font-bold text-base">-</p>
                    </div>
                    <p class="text-xs font-semibold">Skin Temperature</p>
                </div>
            </div>
        </div>
    </div>

    <script>
        // === SEMUA KODE JAVASCRIPT TETAP SAMA SEPERTI ASLINYA ===
        // ... (tempelkan semua kode <script> dari file asli Anda di sini) ...

        const progressBar = document.getElementById('progressBar');
        const heartRateEl = document.getElementById('heartRate');
        const skinConductanceEl = document.getElementById('skinConductance'); 
        const skinTempEl = document.getElementById('skinTemp');

        // Arrays to store all the readings
        let heartRateReadings = [];
        let skinConductanceReadings = [];
        let skinTempReadings = [];
        let startTime = Date.now();
        let scanDuration = 60000; // 60 seconds in milliseconds
        let sensorStarted = false;

        function startSensorScript() {
            return fetch('sensor_control.php?action=start')
                .then(response => response.json())
                .then(result => {
                    if (result.success) {
                        console.log('Sensor started:', result.message);
                        sensorStarted = true;
                        return true;
                    } else {
                        console.error('Failed to start sensor:', result.error);
                        return false;
                    }
                })
                .catch(error => {
                    console.error('Error starting sensor:', error);
                    return false;
                });
        }

        function stopSensorScript() {
            return fetch('sensor_control.php?action=stop')
                .then(response => response.json())
                .then(result => {
                    if (result.success) {
                        console.log('Sensor stopped:', result.message);
                    } else {
                        console.error('Failed to stop sensor:', result.error);
                    }
                })
                .catch(error => {
                    console.error('Error stopping sensor:', error);
                });
        }

        function updateSensorData() {
            // Fetch real sensor data from the Python script via PHP API
            fetch('read_sensor_data.php')
                .then(response => response.json())
                .then(result => {
                    if (result.success && result.data && result.data.current_reading) {
                        const reading = result.data.current_reading;
                        
                        const heartRate = reading.heart_rate > 0 ? reading.heart_rate : 0;
                        const skinConductance = reading.skin_conductance > 0 ? reading.skin_conductance : 0;
                        const skinTemp = reading.skin_temperature > 0 ? reading.skin_temperature : 0;

                        if (heartRate > 0) heartRateReadings.push(heartRate);
                        if (skinConductance > 0) skinConductanceReadings.push(skinConductance);
                        if (skinTemp > 0) skinTempReadings.push(skinTemp);

                        heartRateEl.textContent = heartRate > 0 ? Math.round(heartRate) : '-';
                        skinConductanceEl.textContent = skinConductance > 0 ? skinConductance.toFixed(3) : '-';
                        skinTempEl.textContent = skinTemp > 0 ? skinTemp.toFixed(1) : '-';
                    } else {
                        heartRateEl.textContent = '-';
                        skinConductanceEl.textContent = '-';
                        skinTempEl.textContent = '-';
                    }
                })
                .catch(error => {
                    console.error('Error fetching sensor data:', error);
                    heartRateEl.textContent = '-';
                    skinConductanceEl.textContent = '-';
                    skinTempEl.textContent = '-';
                });
        }

        function calculateAverage(arr) {
            if (arr.length === 0) return 0;
            const sum = arr.reduce((a, b) => a + b, 0);
            return sum / arr.length;
        }

        function finishScanAndRedirect() {
            if (window.dataInterval) {
                clearInterval(window.dataInterval);
            }

            stopSensorScript();

            const avgHeartRate = calculateAverage(heartRateReadings);
            const avgSkinConductance = calculateAverage(skinConductanceReadings);
            const avgSkinTemp = calculateAverage(skinTempReadings);
            
            if (heartRateReadings.length === 0 || skinConductanceReadings.length === 0 || skinTempReadings.length === 0) {
                fetch('read_sensor_data.php')
                    .then(response => response.json())
                    .then(result => {
                        if (result.success && result.data && result.data.is_complete && result.data.averages) {
                            const averages = result.data.averages;
                            localStorage.setItem('avgHeartRate', Math.round(averages.heart_rate || 0));
                            localStorage.setItem('avgSkinConductance', (averages.skin_conductance || 0).toFixed(3));
                            localStorage.setItem('avgSkinTemp', (averages.skin_temperature || 0).toFixed(1));
                        } else {
                            localStorage.setItem('avgHeartRate', Math.round(avgHeartRate || 0));
                            localStorage.setItem('avgSkinConductance', (avgSkinConductance || 0).toFixed(3));
                            localStorage.setItem('avgSkinTemp', (avgSkinTemp || 0).toFixed(1));
                        }
                        window.location.href = 'page5.php';
                    })
                    .catch(error => {
                        console.error('Error getting final averages:', error);
                        localStorage.setItem('avgHeartRate', Math.round(avgHeartRate || 0));
                        localStorage.setItem('avgSkinConductance', (avgSkinConductance || 0).toFixed(3));
                        localStorage.setItem('avgSkinTemp', (avgSkinTemp || 0).toFixed(1));
                        window.location.href = 'page5.php';
                    });
            } else {
                localStorage.setItem('avgHeartRate', Math.round(avgHeartRate));
                localStorage.setItem('avgSkinConductance', avgSkinConductance.toFixed(3));
                localStorage.setItem('avgSkinTemp', avgSkinTemp.toFixed(1));
                window.location.href = 'page5.php';
            }
        }

        startSensorScript().then(success => {
            if (success) {
                console.log('Sensor script started, beginning data collection...');
                setTimeout(() => {
                    const dataInterval = setInterval(updateSensorData, 1000); 
                    window.dataInterval = dataInterval; 
                }, 3000);
            } else {
                console.error('Failed to start sensor script');
                alert('Gagal memulai sensor. Silakan coba lagi.');
            }
        });
        
        // Sedikit jeda sebelum memulai animasi progress bar
        setTimeout(() => { progressBar.style.width = '100%'; }, 100);
        
        // Setelah 60 detik, hitung rata-rata dan pindah halaman
        setTimeout(finishScanAndRedirect, 60000);

        window.addEventListener('beforeunload', function() {
            if (sensorStarted) {
                stopSensorScript();
            }
        });
    </script>
</body>
</html>