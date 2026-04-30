<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Assessment</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="assets/fonts.css" rel="stylesheet">
    <style>
        body {
            font-family: sans-serif;
        }
        #progressBar {
            transition: width 60s linear;
        }
        .hidden {
            display: none !important;
        }
        .fade-in {
            animation: fadeIn 0.5s ease-in;
        }
        @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }
    </style>
</head>
<body class="text-[#0D3D6F]">

    <div class="min-h-screen w-full flex items-center justify-center">
        <div class="w-full max-w-5xl flex flex-col items-center justify-around p-4 aspect-[1024/600]">

            <img src="assets/logo.png" alt="Logo" class="h-10">

            <!-- Video Container - Persistent across all states -->
            <div class="w-full max-w-md">
                <div class="aspect-[4/3] bg-black rounded-lg overflow-hidden shadow-md border border-slate-400">
                    <img src="http://localhost:5003/webapp" alt="Assessment video" class="w-full h-full object-cover">
                </div>
                
                <!-- State 1: Start Button -->
                <div id="startState" class="flex justify-center mt-6">
                    <button id="startButton" class="bg-[#B3E5FC] text-[#0D3D6F] font-bold text-lg py-2.5 px-12 rounded-full shadow-md hover:opacity-90 transition-opacity">
                        START
                    </button>
                </div>

                <!-- State 2: Progress Bar -->
                <div id="scanningState" class="w-full mt-4 hidden">
                    <div class="w-full bg-sky-100 rounded-full h-3.5 shadow-inner">
                        <div id="progressBar" class="bg-[#B3E5FC] h-3.5 rounded-full" style="width: 0%"></div>
                    </div>
                    <p class="text-center text-lg mt-2 font-semibold">Scanning...</p>
                </div>

                <!-- State 3: Result Button -->
                <div id="resultState" class="flex justify-center mt-6 hidden">
                    <button id="resultButton" class="bg-[#B3E5FC] text-[#0D3D6F] font-bold text-lg py-2.5 px-12 rounded-full shadow-md hover:opacity-90 transition-opacity">
                        RESULT
                    </button>
                </div>
            </div>

            <!-- Sensor Data Display -->
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
        // State management
        let currentState = 'start'; // start, scanning, result
        
        // Sensor data storage
        let heartRateReadings = [];
        let skinConductanceReadings = [];
        let skinTempReadings = [];
        let avgHeartRate, avgSkinConductance, avgSkinTemp;
        
        // Sensor control variables
        let sensorStarted = false;
        let dataInterval = null;
        let startTime = null;
        let scanDuration = 60000; // 60 seconds

        // DOM elements
        const startState = document.getElementById('startState');
        const scanningState = document.getElementById('scanningState');
        const resultState = document.getElementById('resultState');
        const startButton = document.getElementById('startButton');
        const resultButton = document.getElementById('resultButton');
        const progressBar = document.getElementById('progressBar');
        const heartRateEl = document.getElementById('heartRate');
        const skinConductanceEl = document.getElementById('skinConductance');
        const skinTempEl = document.getElementById('skinTemp');

        // State transition functions
        function showState(state) {
            // Hide all states
            startState.classList.add('hidden');
            scanningState.classList.add('hidden');
            resultState.classList.add('hidden');
            
            // Show current state with fade effect
            switch(state) {
                case 'start':
                    startState.classList.remove('hidden');
                    startState.classList.add('fade-in');
                    break;
                case 'scanning':
                    scanningState.classList.remove('hidden');
                    scanningState.classList.add('fade-in');
                    break;
                case 'result':
                    resultState.classList.remove('hidden');
                    resultState.classList.add('fade-in');
                    // Update result display
                    updateResultDisplay();
                    break;
            }
            currentState = state;
        }

        // Sensor control functions
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
                        skinTempEl.textContent = skinTemp > 0 ? skinTemp.toFixed(2) : '-';
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

        function finishScanning() {
            if (dataInterval) {
                clearInterval(dataInterval);
                dataInterval = null;
            }

            stopSensorScript();

            avgHeartRate = calculateAverage(heartRateReadings);
            avgSkinConductance = calculateAverage(skinConductanceReadings);
            avgSkinTemp = calculateAverage(skinTempReadings);
            
            if (heartRateReadings.length === 0 || skinConductanceReadings.length === 0 || skinTempReadings.length === 0) {
                fetch('read_sensor_data.php')
                    .then(response => response.json())
                    .then(result => {
                        if (result.success && result.data && result.data.is_complete && result.data.averages) {
                            const averages = result.data.averages;
                            avgHeartRate = averages.heart_rate || 0;
                            avgSkinConductance = averages.skin_conductance || 0;
                            avgSkinTemp = averages.skin_temperature || 0;
                        }
                        showState('result');
                    })
                    .catch(error => {
                        console.error('Error getting final averages:', error);
                        showState('result');
                    });
            } else {
                showState('result');
            }
        }

        function updateResultDisplay() {
            heartRateEl.textContent = Math.round(avgHeartRate || 0);
            skinConductanceEl.textContent = (avgSkinConductance || 0).toFixed(3);
            skinTempEl.textContent = (avgSkinTemp || 0).toFixed(2);
        }

        // Event handlers
        startButton.addEventListener('click', function() {
            showState('scanning');
            
            // Start YOLO scanning (updated to port 5003)
            fetch('http://localhost:5003/api/start_yolo_scan', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' }
            }).then(response => response.json())
            .then(result => {
                if (result.status === 'success') {
                    console.log('YOLO scanning started:', result.message);
                } else {
                    console.error('Failed to start YOLO scanning:', result.message);
                }
            }).catch(error => {
                console.error('Error starting YOLO scanning:', error);
            });
            
            startSensorScript().then(success => {
                if (success) {
                    console.log('Sensor script started, beginning data collection...');
                    startTime = Date.now();
                    
                    // Start progress bar animation
                    setTimeout(() => { 
                        progressBar.style.width = '100%'; 
                    }, 100);
                    
                    // Start data collection after 3 seconds
                    setTimeout(() => {
                        dataInterval = setInterval(updateSensorData, 1000); 
                    }, 3000);
                    
                    // Finish scanning after 60 seconds
                    setTimeout(finishScanning, scanDuration);
                } else {
                    console.error('Failed to start sensor script');
                    alert('Gagal memulai sensor. Silakan coba lagi.');
                    showState('start');
                }
            });
        });

        resultButton.addEventListener('click', async function() {
            // Debug: Log current values
            console.log('avgHeartRate:', avgHeartRate);
            console.log('avgSkinConductance:', avgSkinConductance);
            console.log('avgSkinTemp:', avgSkinTemp);
            
            // Check if we have valid data (allow 0 values, just not null/undefined)
            if (avgHeartRate === undefined || avgSkinConductance === undefined || avgSkinTemp === undefined) {
                alert("Data fisiologis tidak ditemukan. Harap ulangi proses dari awal.");
                return;
            }
            
            // Use the current displayed values if averages are not set
            const heartRateValue = avgHeartRate !== undefined ? avgHeartRate : parseFloat(heartRateEl.textContent) || 0;
            const skinConductanceValue = avgSkinConductance !== undefined ? avgSkinConductance : parseFloat(skinConductanceEl.textContent) || 0;
            const skinTempValue = avgSkinTemp !== undefined ? avgSkinTemp : parseFloat(skinTempEl.textContent) || 0;
            
            resultButton.textContent = 'PROCESSING...';
            resultButton.disabled = true;

            try {
                // Test connectivity to YOLO service first (fixed timeout)
                console.log('Testing YOLO service connectivity...');
                let yoloTestResponse;
                try {
                    const yoloTestController = new AbortController();
                    const yoloTestTimeout = setTimeout(() => yoloTestController.abort(), 5000);
                    
                    yoloTestResponse = await fetch('http://localhost:5003/api/yolo_status', {
                        method: 'GET',
                        headers: { 'Content-Type': 'application/json' },
                        signal: yoloTestController.signal
                    });
                    
                    clearTimeout(yoloTestTimeout);
                    
                    if (!yoloTestResponse.ok) {
                        throw new Error(`YOLO service returned status: ${yoloTestResponse.status}`);
                    }
                    
                    const testResult = await yoloTestResponse.json();
                    console.log('YOLO service is responsive:', testResult);
                } catch (yoloError) {
                    console.error('YOLO service connectivity test failed:', yoloError);
                    throw new Error(`YOLO service (port 5003) tidak dapat diakses: ${yoloError.message}`);
                }

                // Get YOLO detection result (fixed timeout)
                console.log('Getting YOLO detection results...');
                const yoloController = new AbortController();
                const yoloTimeout = setTimeout(() => yoloController.abort(), 10000);
                
                const yoloResponse = await fetch('http://localhost:5003/api/get_yolo_result', {
                    method: 'GET',
                    headers: { 'Content-Type': 'application/json' },
                    signal: yoloController.signal
                });
                
                clearTimeout(yoloTimeout);
                
                if (!yoloResponse.ok) {
                    throw new Error(`Failed to get YOLO results: HTTP ${yoloResponse.status}`);
                }
                
                const yoloResult = await yoloResponse.json();
                console.log('YOLO result received:', yoloResult);
                
                if (yoloResult.status !== 'success') {
                    throw new Error('Failed to get YOLO results: ' + yoloResult.message);
                }

                // Test connectivity to Random Forest service (fixed timeout)
                console.log('Testing Random Forest service connectivity...');
                let rfTestResponse;
                try {
                    const rfTestController = new AbortController();
                    const rfTestTimeout = setTimeout(() => rfTestController.abort(), 5000);
                    
                    rfTestResponse = await fetch('http://localhost:5002/', {
                        method: 'GET',
                        headers: { 'Content-Type': 'application/json' },
                        signal: rfTestController.signal
                    });
                    
                    clearTimeout(rfTestTimeout);
                    
                    if (!rfTestResponse.ok) {
                        throw new Error(`Random Forest service returned status: ${rfTestResponse.status}`);
                    }
                    
                    const rfTestText = await rfTestResponse.text();
                    console.log('Random Forest service is responsive:', rfTestText);
                } catch (rfError) {
                    console.error('Random Forest service connectivity test failed:', rfError);
                    throw new Error(`Random Forest service (port 5002) tidak dapat diakses: ${rfError.message}`);
                }
                
                // Prepare data for Random Forest prediction
                const rfApiUrl = 'http://localhost:5002/predict';
                const dataToSend = {
                    yolo_data: yoloResult.yolo_data,
                    sensor_data: {
                        HR: parseFloat(heartRateValue),
                        ST: parseFloat(skinTempValue),
                        GSR: parseFloat(skinConductanceValue)
                    }
                };

                console.log('Sending data to Random Forest API:', dataToSend);

                // Final prediction request (fixed timeout)
                const rfController = new AbortController();
                const rfTimeout = setTimeout(() => rfController.abort(), 15000);
                
                const rfResponse = await fetch(rfApiUrl, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(dataToSend),
                    signal: rfController.signal
                });

                clearTimeout(rfTimeout);

                if (!rfResponse.ok) {
                    const errorText = await rfResponse.text();
                    throw new Error(`HTTP Error ${rfResponse.status}: ${errorText}`);
                }

                const result = await rfResponse.json();
                console.log('Random Forest prediction result:', result);

                if (result.status === 'success' && result.predicted_label) {
                    // Format data dengan desimal yang tepat sebelum dikirim ke page6.php
                    const formattedHR = Math.round(heartRateValue); // Tanpa desimal
                    const formattedGSR = skinConductanceValue.toFixed(3); // 3 desimal
                    const formattedST = skinTempValue.toFixed(2); // 2 desimal
                    
                    // Include YOLO and RF data in the redirect
                    const redirectUrl = `page6.php?prediction=${encodeURIComponent(result.predicted_label)}&hr=${encodeURIComponent(formattedHR)}&st=${encodeURIComponent(formattedST)}&gsr=${encodeURIComponent(formattedGSR)}&yolo_class=${encodeURIComponent(result.yolo_data.dominant_class_name || 'normal')}&yolo_confidence=${encodeURIComponent((result.yolo_data.avg_confidence || 0).toFixed(3))}&rf_confidence=${encodeURIComponent((Math.max(...result.rf_probabilities) || 0).toFixed(3))}`;
                    
                    console.log('Redirecting to:', redirectUrl);
                    window.location.href = redirectUrl;
                } else {
                    throw new Error(result.message || 'Invalid response from Random Forest API.');
                }

            } catch (error) {
                console.error("Detailed API Error:", error);
                console.error("Error stack:", error.stack);
                
                // More specific error messages
                let userMessage = "Terjadi kesalahan dalam mendapatkan hasil prediksi:\n\n";
                
                if (error.message.includes('port 5003')) {
                    userMessage += "❌ Server YOLO (port 5003) tidak dapat diakses.\n";
                } else if (error.message.includes('port 5002')) {
                    userMessage += "❌ Server Random Forest (port 5002) tidak dapat diakses.\n";
                } else if (error.name === 'AbortError') {
                    userMessage += "❌ Request timeout - server tidak merespons dalam waktu yang ditentukan.\n";
                } else if (error.message.includes('NetworkError') || error.message.includes('fetch')) {
                    userMessage += "❌ Masalah koneksi jaringan.\n";
                } else {
                    userMessage += `❌ ${error.message}\n`;
                }
                
                userMessage += "\nPastikan semua service berjalan dengan menjalankan:\n./start_all_services.sh";
                
                alert(userMessage);
                resultButton.textContent = 'RESULT';
                resultButton.disabled = false;
            }
        });

        // Cleanup on page unload
        window.addEventListener('beforeunload', function() {
            if (sensorStarted) {
                stopSensorScript();
            }
            if (dataInterval) {
                clearInterval(dataInterval);
            }
        });

        // Initialize page
        showState('start');
    </script>
</body>
</html>