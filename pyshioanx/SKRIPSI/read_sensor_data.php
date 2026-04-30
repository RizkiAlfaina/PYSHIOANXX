<?php
header('Content-Type: application/json');
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: GET');
header('Access-Control-Allow-Headers: Content-Type');

$json_file = '/home/umudiyah/pyshioanx/SKRIPSI/sensor_data.json';

// Cek apakah file JSON ada
if (!file_exists($json_file)) {
    echo json_encode([
        'success' => false,
        'error' => 'Sensor data file not found',
        'data' => null
    ]);
    exit;
}

// Baca file JSON
$json_content = file_get_contents($json_file);
if ($json_content === false) {
    echo json_encode([
        'success' => false,
        'error' => 'Failed to read sensor data file',
        'data' => null
    ]);
    exit;
}

// Decode JSON
$sensor_data = json_decode($json_content, true);
if ($sensor_data === null) {
    echo json_encode([
        'success' => false,
        'error' => 'Invalid JSON format in sensor data file',
        'data' => null
    ]);
    exit;
}

// Return data
echo json_encode([
    'success' => true,
    'error' => null,
    'data' => $sensor_data
]);
?>
