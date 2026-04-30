from flask import Flask, request, jsonify
from flask_cors import CORS
import numpy as np
from tensorflow.keras.models import load_model
import joblib
import gspread
import os
from datetime import datetime

# =====================================================================
# Inisialisasi Aplikasi dan Pemuatan Awal
# =====================================================================

app = Flask(__name__)
CORS(app)  # Aktifkan CORS untuk akses dari frontend

# --- Tentukan path absolut untuk semua file ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, 'model_terbaik.h5')
SCALER_PATH = os.path.join(BASE_DIR, 'scaler_terbaik.joblib')
SERVICE_ACCOUNT_PATH = os.path.join(BASE_DIR, 'service_account.json')

# --- Muat Model dan Scaler ---
try:
    model = load_model(MODEL_PATH)
    scaler = joblib.load(SCALER_PATH)
    print("✅ Model and scaler loaded successfully!")
except Exception as e:
    print(f"❌ Error loading model or scaler: {e}")
    model = None
    scaler = None

# --- Koneksi ke Google Sheets ---
try:
    gc = gspread.service_account(filename=SERVICE_ACCOUNT_PATH)
    sht2 = gc.open_by_url('https://docs.google.com/spreadsheets/d/1JGaNiwB-bztN4Sf_W_QayTde6UpcALphXjupHNuUct8/edit?gid=0#gid=0')
    worksheet = sht2.get_worksheet(0)
    print("✅ Connected to Google Sheets successfully!")
except Exception as e:
    print(f"❌ Error connecting to Google Sheets: {e}")
    worksheet = None

# --- Definisi Mapping Label ---
label_reverse_mapping = {
    0: 'normal to mild',
    1: 'mild to moderate',
    2: 'moderate to severe',
    3: 'severe'
}

# =====================================================================
# Definisi Endpoint API
# =====================================================================

@app.route('/')
def home():
    return "API Model Prediksi Kecemasan Aktif dan Terhubung ke Google Sheets!"

@app.route('/predict', methods=['POST'])
def predict():
    # Pastikan semua komponen (model, scaler, worksheet) sudah termuat
    if not all([model, scaler, worksheet]):
        return jsonify({'error': 'Server not ready. Check logs for model, scaler, or worksheet loading errors.'}), 500

    # Dapatkan data JSON dari request
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Invalid input: No JSON data received.'}), 400

    # Validasi input: Pastikan semua field yang dibutuhkan ada
    required_fields = ['HR', 'ST', 'GSR']
    if not all(field in data for field in required_fields):
        return jsonify({'error': f'Invalid input: Missing one or more fields. Required: {required_fields}.'}), 400
    
    try:
        # --- 1. PROSES PREDIKSI MODEL ---
        
        # Susun fitur untuk model: ['HR', 'ST', 'GSR']
        features = np.array([[data['HR'], data['ST'], data['GSR']]], dtype=float)
        
        # Terapkan standarisasi menggunakan scaler yang sudah di-load
        scaled_features = scaler.transform(features)
        
        # Lakukan prediksi dengan model
        prediction_probs = model.predict(scaled_features)
        
        # Dapatkan kelas dengan probabilitas tertinggi
        predicted_class = np.argmax(prediction_probs, axis=1)[0]
        
        # Dapatkan label nama kelas dari mapping
        predicted_label = label_reverse_mapping.get(int(predicted_class), "Unknown")

        # --- 2. SIMPAN HASIL KE GOOGLE SHEETS ---

        print(f"Prediction successful. Preparing to write to Google Sheets...")
        
        try:
            # Dapatkan timestamp saat ini untuk kolom 'Waktu'
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # Susun data dalam list sesuai urutan kolom di Google Sheets
            # Contoh urutan: Waktu, Nama, NIM, Kelas, HR, ST, GSR, Klasifikasi
            data_row = [
                current_time,
                data['HR'],
                data['ST'],
                data['GSR'],
                predicted_label # Hasil dari prediksi model
            ]
            
            # Tambahkan (append) data tersebut ke worksheet
            worksheet.append_row(data_row, value_input_option='USER_ENTERED')
            print(f"Successfully wrote to Google Sheets: {data_row}")
        
        except Exception as e:
            # Jika gagal menulis ke sheet, tampilkan error di log server tapi jangan hentikan API
            print(f"⚠️ Could not write to Google Sheets: {e}")


        # --- 3. KIRIM RESPON JSON KE PENGGUNA ---
        
        response = {
            'status': 'success',
            'predicted_class': int(predicted_class),
            'predicted_label': predicted_label,
            'prediction_probabilities': prediction_probs.tolist()[0]
        }
        
        return jsonify(response)

    except Exception as e:
        # Tangani error jika terjadi saat proses prediksi
        return jsonify({'error': f'An error occurred during prediction: {str(e)}'}), 500

if __name__ == '__main__':
    # Jalankan server
    app.run(host='0.0.0.0', port=5000, debug=True)