<?php
    // Ambil data dari parameter URL dengan aman
    $prediction = isset($_GET['prediction']) ? htmlspecialchars(strtoupper($_GET['prediction'])) : 'TIDAK DIKETAHUI';
    $heartRate = isset($_GET['hr']) ? htmlspecialchars($_GET['hr']) : '0';
    $skinConductance = isset($_GET['gsr']) ? htmlspecialchars($_GET['gsr']) : '0.000';
    $skinTemp = isset($_GET['st']) ? htmlspecialchars($_GET['st']) : '0.00';
    
    // Data YOLO dan Random Forest
    $yoloClass = isset($_GET['yolo_class']) ? htmlspecialchars($_GET['yolo_class']) : 'normal';
    $yoloConfidence = isset($_GET['yolo_confidence']) ? htmlspecialchars($_GET['yolo_confidence']) : '0.000';
    $rfConfidence = isset($_GET['rf_confidence']) ? htmlspecialchars($_GET['rf_confidence']) : '0.000';
    
    // Format data dengan desimal yang konsisten
    $formattedHeartRate = round(floatval($heartRate)); // Tanpa desimal
    $formattedSkinConductance = number_format(floatval($skinConductance), 3); // 3 desimal
    $formattedSkinTemp = number_format(floatval($skinTemp), 2); // 2 desimal
    $formattedYoloConfidence = number_format(floatval($yoloConfidence), 3); // 3 desimal
    $formattedRfConfidence = number_format(floatval($rfConfidence), 3); // 3 desimal
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Anxiety Category Result</title>
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

            <header class="w-full max-w-xl flex justify-between items-center">
                <img src="assets/logo.png" alt="Logo" class="h-13">
                <a id="homeButton" href="page1.php" class="bg-[#B3E5FC] p-2.5 rounded-full shadow-md hover:opacity-90 transition-opacity">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
                    </svg>
                </a>
            </header>

            <main class="w-full max-w-lg flex flex-col items-center text-center">
                <h1 class="text-4xl font-bold tracking-wider mb-4">ANXIETY CATEGORY</h1>
                <div class="bg-[#B3E5FC] w-full py-10 px-6 rounded-2xl shadow-lg">
                    <p class="text-5xl font-bold tracking-widest"><?php echo $prediction; ?></p>
                </div>
            </main>

            <footer class="w-full max-w-lg flex flex-row justify-between text-center">
                <div class="flex flex-col items-center gap-y-1.5">
                    <div class="bg-[#B3E5FC] p-2 rounded-lg shadow w-24 h-12 flex items-center justify-center gap-1.5">
                        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 opacity-70" viewBox="0 0 20 20" fill="currentColor">
                            <path fill-rule="evenodd" d="M3.172 5.172a4 4 0 015.656 0L10 6.343l1.172-1.171a4 4 0 115.656 5.656L10 17.657l-6.828-6.829a4 4 0 010-5.656z" clip-rule="evenodd" />
                        </svg>
                        <p class="font-bold text-base"><?php echo $formattedHeartRate; ?></p>
                    </div>
                    <p class="text-xs font-semibold">Heart Rate</p>
                </div>

                <div class="flex flex-col items-center gap-y-1.5">
                    <div class="bg-[#B3E5FC] p-2 rounded-lg shadow w-24 h-12 flex items-center justify-center gap-1.5">
                        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 opacity-70" viewBox="0 0 20 20" fill="currentColor">
                            <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM6.636 10.636a1 1 0 011.414 0L10 12.586l1.95-1.95a1 1 0 111.414 1.414l-2.657 2.657a1.5 1.5 0 01-2.121 0L6.636 12.05a1 1 0 010-1.414z" clip-rule="evenodd" />
                        </svg>
                        <p class="font-bold text-base"><?php echo $formattedSkinConductance; ?></p>
                    </div>
                    <p class="text-xs font-semibold">Skin Conductance</p>
                </div>

                <div class="flex flex-col items-center gap-y-1.5">
                    <div class="bg-[#B3E5FC] p-2 rounded-lg shadow w-24 h-12 flex items-center justify-center gap-1.5">
                        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 opacity-70" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                            <path stroke-linecap="round" stroke-linejoin="round" d="M14.828 14.828a4 4 0 01-5.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                        </svg>
                        <p class="font-bold text-base"><?php echo $formattedSkinTemp; ?></p>
                    </div>
                    <p class="text-xs font-semibold">Skin Temperature</p>
                </div>
            </footer>
        </div>
    </div>
    <script>
        // Ambil elemen tombol home
        const homeButton = document.getElementById('homeButton');

        // Tambahkan event listener untuk membersihkan localStorage saat tombol diklik
        homeButton.addEventListener('click', function(event) {
            // Mencegah link langsung pindah halaman agar script bisa berjalan dulu
            event.preventDefault(); 
            
            // Hapus data sesi sebelumnya dari localStorage
            localStorage.removeItem('avgHeartRate');
            localStorage.removeItem('avgSkinConductance');
            localStorage.removeItem('avgSkinTemp');
            
            // Setelah data dihapus, arahkan pengguna ke halaman utama
            window.location.href = this.href; 
        });
    </script>
</body>
</html>