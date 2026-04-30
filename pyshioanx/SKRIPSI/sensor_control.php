<?php
header('Content-Type: application/json');
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: GET, POST');
header('Access-Control-Allow-Headers: Content-Type');

function isProcessRunning($pid) {
    return file_exists("/proc/$pid");
}

$action = isset($_GET['action']) ? $_GET['action'] : '';
$json_file = '/home/umudiyah/pyshioanx/SKRIPSI/sensor_data.json';
$python_script = '/home/umudiyah/pyshioanx/sensor/mlx_max_gsr_copy.py';
$pid_file = '/home/umudiyah/pyshioanx/SKRIPSI/sensor_pid.txt';

switch($action) {
    case 'start':
        // Check if sensor is already running
        if (file_exists($pid_file)) {
            $pid = trim(file_get_contents($pid_file));
            if (isProcessRunning($pid)) {
                echo json_encode([
                    'success' => false,
                    'error' => 'Sensor is already running',
                    'pid' => $pid
                ]);
                exit;
            }
        }
        
        // Reset/create JSON file
        $initial_data = [
            "current_reading" => null,
            "total_readings" => 0,
            "duration" => 60,
            "is_complete" => false
        ];
        file_put_contents($json_file, json_encode($initial_data, JSON_PRETTY_PRINT));
        
        // Start Python script in background
        $command = "cd /home/umudiyah/pyshioanx && /bin/bash -c 'source .venv/bin/activate && cd sensor && python3 $python_script' > /dev/null 2>&1 & echo $!";
        $pid = trim(shell_exec($command));
        
        if ($pid && is_numeric($pid)) {
            // Save PID for later reference
            file_put_contents($pid_file, $pid);
            echo json_encode([
                'success' => true,
                'message' => 'Sensor started successfully',
                'pid' => $pid
            ]);
        } else {
            echo json_encode([
                'success' => false,
                'error' => 'Failed to start sensor script'
            ]);
        }
        break;
        
    case 'stop':
        if (file_exists($pid_file)) {
            $pid = trim(file_get_contents($pid_file));
            if (isProcessRunning($pid)) {
                shell_exec("kill -15 $pid 2>/dev/null"); // SIGTERM
                sleep(1); // Give it time to terminate
                if (!isProcessRunning($pid)) {
                    unlink($pid_file);
                    echo json_encode([
                        'success' => true,
                        'message' => 'Sensor stopped successfully'
                    ]);
                } else {
                    // Force kill if SIGTERM didn't work
                    shell_exec("kill -9 $pid 2>/dev/null");
                    unlink($pid_file);
                    echo json_encode([
                        'success' => true,
                        'message' => 'Sensor force stopped'
                    ]);
                }
            } else {
                unlink($pid_file);
                echo json_encode([
                    'success' => true,
                    'message' => 'Sensor was not running'
                ]);
            }
        } else {
            echo json_encode([
                'success' => false,
                'error' => 'Sensor is not running'
            ]);
        }
        break;
        
    case 'status':
        $is_running = false;
        $pid = null;
        if (file_exists($pid_file)) {
            $pid = trim(file_get_contents($pid_file));
            $is_running = isProcessRunning($pid);
        }
        
        // Check if data file exists and has recent data
        $has_data = false;
        if (file_exists($json_file)) {
            $data = json_decode(file_get_contents($json_file), true);
            $has_data = $data && isset($data['current_reading']);
        }
        
        echo json_encode([
            'success' => true,
            'is_running' => $is_running,
            'has_data' => $has_data,
            'pid' => $is_running ? $pid : null
        ]);
        break;
        
    default:
        echo json_encode([
            'success' => false,
            'error' => 'Invalid action. Use: start, stop, or status'
        ]);
}
?>
