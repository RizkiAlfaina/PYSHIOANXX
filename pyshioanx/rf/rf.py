import os
import numpy as np
from ultralytics import YOLO
from tensorflow.keras.models import load_model
from sklearn.ensemble import RandomForestClassifier
import joblib
import sys
from flask import Flask, request, jsonify
from flask_cors import CORS
import gspread
from datetime import datetime

# Flask app setup
app = Flask(__name__)
CORS(app)

# Path model (ganti sesuai lokasi file Anda)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RF_MODEL_PATH = os.path.join(BASE_DIR, "fusionrfmodelfix.pkl")

# Path untuk model DNN dan scaler dari pengumpulan folder
PENGUMPULAN_DIR = os.path.join(os.path.dirname(BASE_DIR), 'pengumpulan')
DNN_MODEL_PATH = os.path.join(PENGUMPULAN_DIR, "best_fold2.h5")
SCALER_PATH = os.path.join(PENGUMPULAN_DIR, "scaler_fold2.joblib")
SERVICE_ACCOUNT_PATH = os.path.join(PENGUMPULAN_DIR, "service_account.json")

def load_models():
    """Load semua model dengan error handling"""
    try:
        print("Loading models...")
        dnn_model = load_model(DNN_MODEL_PATH)
        scaler = joblib.load(SCALER_PATH)
        rf_model = joblib.load(RF_MODEL_PATH)
        print("✓ All models loaded successfully!")
        return dnn_model, scaler, rf_model
    except FileNotFoundError as e:
        print(f"❌ Model file not found: {e}")
        print("Pastikan semua file model ada:")
        print(f"- {RF_MODEL_PATH}")
        print(f"- {DNN_MODEL_PATH}")
        print(f"- {SCALER_PATH}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error loading models: {e}")
        sys.exit(1)

# Load model dengan error handling
dnn_model, scaler, rf_model = load_models()

# Google Sheets connection
try:
    gc = gspread.service_account(filename=SERVICE_ACCOUNT_PATH)
    sht2 = gc.open_by_url('https://docs.google.com/spreadsheets/d/1JGaNiwB-bztN4Sf_W_QayTde6UpcALphXjupHNuUct8/edit?gid=0#gid=0')
    worksheet = sht2.get_worksheet(0)
    print("✅ Connected to Google Sheets successfully!")
except Exception as e:
    print(f"❌ Error connecting to Google Sheets: {e}")
    worksheet = None

label_map = {0: "normal to mild", 1: "mild to moderate", 2: "moderate to severe", 3: "severe"}

def get_probs_dnn(X_input):
    """Ekstrak probabilitas dari model DNN dengan input validation"""
    try:
        # Validasi input
        if not isinstance(X_input, (list, np.ndarray)) or len(X_input) != 3:
            raise ValueError("Input harus berupa list/array dengan 3 elemen [hr, st, gsr]")
        
        hr, st, gsr = X_input
        
        # Validasi range input
        if not (0 <= hr <= 200):
            print(f"⚠ Warning: HR={hr} di luar range normal (0-200)")
        if not (0 <= st <= 50):
            print(f"⚠ Warning: ST={st} di luar range normal (0-50)")
        if not (0 <= gsr <= 1):
            print(f"⚠ Warning: GSR={gsr} di luar range normal (0-1)")
        
        X_scaled = scaler.transform([X_input])
        probs = dnn_model.predict(X_scaled, verbose=0)
        return probs.flatten()
    except Exception as e:
        print(f"❌ Error in DNN prediction: {e}")
        return np.array([0.25, 0.25, 0.25, 0.25])

def predict_with_fusion(yolo_data, hr, st, gsr):
    """
    Prediksi level kecemasan menggunakan late fusion YOLO + DNN + RF
    
    Args:
        yolo_data (dict): Data dari YOLO detection dengan format:
                         {'class_counts': [count0, count1, count2, count3], 
                          'avg_confidence': float}
        hr (float): Heart rate
        st (float): Skin temperature
        gsr (float): Galvanic skin response
    
    Returns:
        dict: Hasil prediksi dengan detail
    """
    try:
        # Validasi input numerik
        hr = float(hr)
        st = float(st)
        gsr = float(gsr)
        
        # Konversi YOLO class counts ke probabilitas
        class_counts = np.array(yolo_data.get('class_counts', [1, 0, 0, 0]))
        total_detections = max(class_counts.sum(), 1)  # Avoid division by zero
        yolo_probs = class_counts / total_detections
        
        # Ekstrak probabilitas dari DNN
        dnn_probs = get_probs_dnn([hr, st, gsr])
        
        # Late fusion - gabungkan probabilitas DNN dan YOLO
        X_fusion = np.concatenate([dnn_probs, yolo_probs]).reshape(1, -1)
        
        # Prediksi menggunakan Random Forest
        rf_prediction = rf_model.predict(X_fusion)[0]
        rf_probabilities = rf_model.predict_proba(X_fusion)[0]
        
        # Hasil akhir
        final_label = label_map.get(rf_prediction, f"Unknown class {rf_prediction}")
        
        result = {
            'status': 'success',
            'predicted_class': int(rf_prediction),
            'predicted_label': final_label,
            'rf_probabilities': rf_probabilities.tolist(),
            'dnn_probabilities': dnn_probs.tolist(),
            'yolo_probabilities': yolo_probs.tolist(),
            'yolo_data': yolo_data,
            'sensor_data': {
                'hr': hr,
                'st': st, 
                'gsr': gsr
            }
        }
        
        return result
        
    except ValueError as e:
        return {'status': 'error', 'message': f"Input error: {e}"}
    except Exception as e:
        return {'status': 'error', 'message': f"Prediction error: {e}"}

@app.route('/')
def home():
    return "Random Forest Prediction API - Ready for YOLO + Sensor data fusion!"

@app.route('/predict', methods=['POST'])
def predict_api():
    """
    API endpoint untuk prediksi menggunakan data YOLO dan sensor
    
    Expected JSON format:
    {
        "yolo_data": {
            "class_counts": [count0, count1, count2, count3],
            "avg_confidence": float,
            "total_detections": int
        },
        "sensor_data": {
            "HR": float,
            "ST": float,
            "GSR": float,
            "voltage": float
        }
    }
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'status': 'error', 'message': 'No JSON data received'}), 400
        
        # Validasi struktur data
        if 'yolo_data' not in data or 'sensor_data' not in data:
            return jsonify({'status': 'error', 'message': 'Missing yolo_data or sensor_data'}), 400
        
        yolo_data = data['yolo_data']
        sensor_data = data['sensor_data']
        
        # Validasi sensor data
        required_sensor_fields = ['HR', 'ST', 'GSR']
        if not all(field in sensor_data for field in required_sensor_fields):
            return jsonify({'status': 'error', 'message': f'Missing sensor fields. Required: {required_sensor_fields}'}), 400
        
        # Lakukan prediksi
        result = predict_with_fusion(
            yolo_data=yolo_data,
            hr=sensor_data['HR'],
            st=sensor_data['ST'],
            gsr=sensor_data['GSR']
        )
        
        # Debug print untuk melihat voltage yang diterima dan diproses
        print(f"🔋 Debug - Input voltage: {sensor_data.get('voltage')}")
        
        # Simpan ke Google Sheets jika berhasil
        if result['status'] == 'success' and worksheet:
            try:
                current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                # Ambil voltage dari sensor_data input
                voltage_value = sensor_data.get('voltage', '')
                if voltage_value is None:
                    voltage_value = ''
                    
                data_row = [
                    current_time,           # Kolom 1: Timestamp
                    sensor_data['HR'],      # Kolom 2: Heart Rate
                    sensor_data['ST'],      # Kolom 3: Skin Temperature  
                    sensor_data['GSR'],     # Kolom 4: GSR
                    result['predicted_label'],  # Kolom 5: Predicted Label
                    str(yolo_data),         # Kolom 6: YOLO Data
                    result['yolo_data'].get('avg_confidence', 0),  # Kolom 7: YOLO Confidence
                    voltage_value           # Kolom 8: Voltage (posisi terakhir)
                ]
                worksheet.append_row(data_row, value_input_option='USER_ENTERED')
                print(f"Successfully wrote to Google Sheets: {data_row}")
            except Exception as e:
                print(f"⚠️ Could not write to Google Sheets: {e}")
                # Debug info untuk melihat apa yang dikirim
                print(f"Debug - sensor_data voltage: {sensor_data.get('voltage')}")
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Server error: {str(e)}'}), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5002, debug=True)