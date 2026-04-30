<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Instructions</title>
    <link href="assets/tailwind.css" rel="stylesheet">
    <link href="assets/fonts.css" rel="stylesheet">
</head>
<body class="text-[#0D3D6F]"> 
    <div class="min-h-screen flex flex-col items-center justify-center p-4 md:p-6 lg:p-8">

        <main class="w-full max-w-6xl flex-grow grid grid-cols-2 gap-8 md:gap-12 items-center">
            
            <div class="text-center">
                <p class="font-semibold text-3xl md:text-4xl lg:text-4xl leading-normal md:leading-relaxed">
                    ENSURE THE PATIENT <br>
                    PLACES THEIR HAND <br>
                    ON THE DETECTOR <br>
                    AREA AND LOOKS <br>
                    AT THE CAMERA
                </p>
            </div>

            <div class="flex justify-center items-center">
                <img src="assets/hand.png" alt="Assessment Device Diagram" class="bg-white p-4 rounded-2xl shadow-lg w-full max-w-sm">
            </div>
        </main>
        
        <nav class="max-w-4xl flex justify-center items-center gap-x-6 md:gap-x-16 mb-8">
            <a href="page1.php" class="bg-[#B3E5FC] text-[#0D3D6F] font-bold text-lg md:text-xl py-3 px-10 md:px-12 rounded-full shadow-lg hover:opacity-90 transition-opacity">
                Back
            </a>
            <img src="assets/logo.png" alt="Logo" class="h-6 md:h-8 w-auto">
            <a href="assessment.php" class="bg-[#B3E5FC] text-[#0D3D6F] font-bold text-lg md:text-xl py-3 px-10 md:px-12 rounded-full shadow-lg hover:opacity-90 transition-opacity">
                Next
            </a>
        </nav>
    </div>
</body>
</html>