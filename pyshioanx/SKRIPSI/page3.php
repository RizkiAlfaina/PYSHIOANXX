<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Start Assessment</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="assets/fonts.css" rel="stylesheet">
    <style>
        /* Custom font import if needed */
        body {
            font-family: sans-serif;
        }
    </style>
</head>
<body class="text-[#0D3D6F]">

    <div class="min-h-screen w-full flex items-center justify-center">

        <div class="w-full max-w-5xl flex flex-col items-center justify-around p-4 aspect-[1024/600]">

            <img src="assets/logo.png" alt="Logo" class="h-10">

            <div class="w-full max-w-md">
                <div class="aspect-[4/3] bg-black rounded-lg overflow-hidden shadow-md border border-slate-400">
                    <img src="http://localhost:5001/webapp" alt="Upload video" class="w-full h-full object-cover">
                </div>
            </div>

            <a href="page4.php" class="bg-[#B3E5FC] text-[#0D3D6F] font-bold text-lg py-2.5 px-12 rounded-full shadow-md hover:opacity-90 transition-opacity">
                START
            </a>

            <div class="w-full max-w-lg flex flex-row justify-between text-center">
                <div class="flex flex-col items-center gap-y-1.5">
                    <div class="bg-[#B3E5FC] p-2 rounded-lg shadow w-24 h-12 flex items-center justify-center gap-1.5">
                        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 opacity-70" viewBox="0 0 20 20" fill="currentColor">
                            <path fill-rule="evenodd" d="M3.172 5.172a4 4 0 015.656 0L10 6.343l1.172-1.171a4 4 0 115.656 5.656L10 17.657l-6.828-6.829a4 4 0 010-5.656z" clip-rule="evenodd" />
                        </svg>
                        <p class="font-bold text-base">-</p>
                    </div>
                    <p class="text-xs font-semibold">Heart Rate</p>
                </div>

                <div class="flex flex-col items-center gap-y-1.5">
                    <div class="bg-[#B3E5FC] p-2 rounded-lg shadow w-24 h-12 flex items-center justify-center gap-1.5">
                        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 opacity-70" viewBox="0 0 20 20" fill="currentColor">
                            <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM6.636 10.636a1 1 0 011.414 0L10 12.586l1.95-1.95a1 1 0 111.414 1.414l-2.657 2.657a1.5 1.5 0 01-2.121 0L6.636 12.05a1 1 0 010-1.414z" clip-rule="evenodd" />
                        </svg>
                        <p class="font-bold text-base">-</p>
                    </div>
                    <p class="text-xs font-semibold">Skin Conductance</p>
                </div>

                <div class="flex flex-col items-center gap-y-1.5">
                    <div class="bg-[#B3E5FC] p-2 rounded-lg shadow w-24 h-12 flex items-center justify-center gap-1.5">
                        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 opacity-70" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                            <path stroke-linecap="round" stroke-linejoin="round" d="M14.828 14.828a4 4 0 01-5.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                        </svg>
                        <p class="font-bold text-base">-</p>
                    </div>
                    <p class="text-xs font-semibold">Skin Temperature</p>
                </div>
            </div>
        </div>
    </div>

</body>
</html>