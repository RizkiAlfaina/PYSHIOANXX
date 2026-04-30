<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Physiological Anxiety Assessment</title>

    <link href="assets/tailwind.css" rel="stylesheet">
    <link href="assets/fonts.css" rel="stylesheet">
</head>
<body class="text-[#0D3D6F]">

    <div class="min-h-screen flex flex-col items-center justify-center p-2 w-full">
        
        <main class="flex flex-col items-center justify-center text-center flex-grow">
            
            <div class="flex justify-center">
                <img src="assets/logo.png" alt="Logo" class="h-16 md:h-24 lg:h-32 mx-auto mb-4 -translate-y-8">
            </div>
            
            <p class="text-sm md:text-lg lg:text-3xl font-light">PRESS</p>
            
            <a href="page2.php" class="bg-[#B3E5FC] text-[#0D3D6F] font-bold text-lg md:text-xl lg:text-3xl py-2 md:py-4 lg:py-8 px-8 md:px-12 lg:px-20 my-1 md:my-2 rounded-full shadow-lg hover:opacity-90 transition-opacity">
                CHECK
            </a>
            
            <p class="text-sm md:text-lg lg:text-3xl font-light mt-1 md:mt-2">to assess the anxiety category</p>

            <div class="mt-2 md:mt-8 lg:mt-15">
                <p id="clock" class="text-4xl md:text-6xl lg:text-7xl font-thin tracking-wider">Loading...</p>
                <p id="date" class="text-xs md:text-base lg:text-lg mt-1"></p>
                <p id="day" class="text-xs md:text-base lg:text-lg"></p>
            </div>
        </main>

        <footer class="text-center text-xl md:text-xl lg:text-base opacity-100 pt-2 pb-1">
            by : Biomedical Engineering ITERA
        </footer>
    </div>

    <script>
        function updateRealTimeClock() {
            // Mengatur zona waktu ke Waktu Indonesia Barat (WIB)
            const options = { timeZone: 'Asia/Jakarta' };
            const now = new Date();

            // Format waktu (Jam:Menit)
            const timeString = now.toLocaleTimeString('en-GB', { 
                ...options, 
                hour: '2-digit', 
                minute: '2-digit' 
            });

            // Format tanggal (DD/MM/YYYY)
            const dateString = now.toLocaleDateString('en-GB', { 
                ...options, 
                day: '2-digit', 
                month: '2-digit', 
                year: 'numeric' 
            });
            
            // Format nama hari (e.g., Monday)
            const dayString = now.toLocaleDateString('en-US', { 
                ...options, 
                weekday: 'long' 
            });

            // Memasukkan hasil format ke dalam elemen HTML
            document.getElementById('clock').textContent = timeString;
            document.getElementById('date').textContent = dateString;
            document.getElementById('day').textContent = dayString;
        }

        // Memanggil fungsi saat halaman dimuat
        updateRealTimeClock();
        // Mengatur agar fungsi dipanggil setiap 1 detik (1000 milidetik)
        setInterval(updateRealTimeClock, 1000);
    </script>
</body>
</html>