<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Assessment Result</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="assets/fonts.css" rel="stylesheet">
    <style>
        body {
            font-family: sans-serif;
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
                <button id="resultButton" class="bg-[#B3E5FC] text-[#0D3D6F] font-bold text-lg py-2.5 px-12 rounded-full shadow-md hover:opacity-90 transition-opacity mt-6">
                    RESULT
                </button>
            </div>

            <div class="w-full max-w-lg flex flex-row justify-between text-center">
                <div class="flex flex-col items-center gap-y-1.5">
                    <div class="bg-[#B3E5FC] p-2 rounded-lg shadow w-24 h-12 flex items-center justify-center gap-1.5">
                        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 opacity-70" viewBox="0 0 20 20" fill="currentColor">
                            <path fill-rule="evenodd" d="M3.172 5.172a4 4 0 015.656 0L10 6.343l1.172-1.171a4 4 0 115.656 5.656L10 17.657l-6.828-6.829a4 4 0 010-5.656z" clip-rule="evenodd" />
                        </svg>
                        <p id="avgHeartRate" class="font-bold text-base">0</p>
                    </div>
                    <p class="text-xs font-semibold">Heart Rate</p>
                </div>

                <div class="flex flex-col items-center gap-y-1.5">
                    <div class="bg-[#B3E5FC] p-2 rounded-lg shadow w-24 h-12 flex items-center justify-center gap-1.5">
                        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 opacity-70" viewBox="0 0 20 20" fill="currentColor">
                            <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM6.636 10.636a1 1 0 011.414 0L10 12.586l1.95-1.95a1 1 0 111.414 1.414l-2.657 2.657a1.5 1.5 0 01-2.121 0L6.636 12.05a1 1 0 010-1.414z" clip-rule="evenodd" />
                        </svg>
                        <p id="avgSkinConductance" class="font-bold text-base">0.000</p>
                    </div>
                    <p class="text-xs font-semibold">Skin Conductance</p>
                </div>

                <div class="flex flex-col items-center gap-y-1.5">
                    <div class="bg-[#B3E5FC] p-2 rounded-lg shadow w-24 h-12 flex items-center justify-center gap-1.5">
                        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 opacity-70" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                            <path stroke-linecap="round" stroke-linejoin="round" d="M14.828 14.828a4 4 0 01-5.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                        </svg>
                        <p id="avgSkinTemp" class="font-bold text-base">0.0</p>
                    </div>
                    <p class="text-xs font-semibold">Skin Temperature</p>
                </div>
            </div>
        </div>
    </div>

    <script>

        // Variabel untuk menyimpan nilai dari localStorage
        let heartRate, skinConductance, skinTemp;

        // Fungsi ini berjalan saat halaman dimuat
        window.onload = function() {
            // Ambil data dari localStorage yang disimpan oleh page4.php
            heartRate = localStorage.getItem('avgHeartRate');
            skinConductance = localStorage.getItem('avgSkinConductance');
            skinTemp = localStorage.getItem('avgSkinTemp');

            // Update elemen HTML dengan nilai yang diambil dan format desimalnya
            if (heartRate) {
                document.getElementById('avgHeartRate').textContent = parseFloat(heartRate).toFixed(0);
            }
            if (skinConductance) {
                document.getElementById('avgSkinConductance').textContent = parseFloat(skinConductance).toFixed(3);
            }
            if (skinTemp) {
                document.getElementById('avgSkinTemp').textContent = parseFloat(skinTemp).toFixed(1);
            }
        };

        // Dapatkan elemen tombol
        const resultButton = document.getElementById('resultButton');

        // Fungsi untuk mengirim data ke API dan redirect
        async function processAndRedirect() {
            // Cek jika data sudah ada
            if (!heartRate || !skinConductance || !skinTemp) {
                alert("Data fisiologis tidak ditemukan. Harap ulangi proses dari awal.");
                return;
            }
            
            // Beri feedback visual ke pengguna bahwa proses sedang berjalan
            resultButton.textContent = 'PROCESSING...';
            resultButton.disabled = true;

            const apiUrl = 'http://127.0.0.1:5000/predict'; // URL API Python Flask
            const dataToSend = {
                HR: parseFloat(heartRate),
                ST: parseFloat(skinTemp),
                GSR: parseFloat(skinConductance)
            };

            try {
                const response = await fetch(apiUrl, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(dataToSend)
                });

                if (!response.ok) throw new Error(`HTTP Error: ${response.status}`);

                const result = await response.json();

                if (result.predicted_label) {
                    // Siapkan URL untuk page6.php dengan data sebagai parameter
                    const redirectUrl = `page6.php?prediction=${encodeURIComponent(result.predicted_label)}&hr=${encodeURIComponent(heartRate)}&st=${encodeURIComponent(skinTemp)}&gsr=${encodeURIComponent(skinConductance)}`;
                    // Arahkan ke halaman hasil
                    window.location.href = redirectUrl;
                } else {
                    throw new Error(result.error || 'Invalid response from server.');
                }

            } catch (error) {
                console.error("API Error:", error);
                alert("Gagal mendapatkan hasil prediksi. Pastikan server API berjalan dan dapat diakses.");
                // Kembalikan tombol ke keadaan semula jika gagal
                resultButton.textContent = 'RESULT';
                resultButton.disabled = false;
            }
        }

        // Tambahkan event listener ke tombol "RESULT"
        resultButton.addEventListener('click', processAndRedirect);
    </script>
</body>
</html>