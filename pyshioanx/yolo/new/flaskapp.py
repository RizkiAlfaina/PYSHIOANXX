from flask import Flask, render_template, Response,jsonify,request,session
from flask_wtf import FlaskForm
from wtforms import FileField, SubmitField,StringField,DecimalRangeField,IntegerRangeField
from werkzeug.utils import secure_filename
from wtforms.validators import InputRequired,NumberRange
from flask_cors import CORS
import os
import cv2
import time
import threading
import json
from datetime import datetime
import numpy as np
from collections import defaultdict

# YOLO_Video is the python file which contains the code for our object detection model
from yolo_detect_calibrated import video_detection, YOLO, _safe_class_names, _apply_user_labels

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes
app.config['SECRET_KEY'] = 'muhammadmoin'
app.config['UPLOAD_FOLDER'] = 'static/files'

# Global variables untuk menyimpan data YOLO
yolo_detection_data = {
    'is_scanning': False,
    'scan_start_time': None,
    'detections': [],  # List of detections per 10-second interval
    'current_interval_data': {'class_counts': [0, 0, 0, 0], 'confidences': []}
}

# Load YOLO model untuk detection
model_path = "yolofix_ncnn_model"  # Model ada di direktori yolo/new/
if os.path.exists(model_path):
    yolo_model = YOLO(model_path)
    class_names = _apply_user_labels(_safe_class_names(yolo_model))
    print(f"✅ YOLO model loaded successfully from {model_path}")
else:
    # Try alternative paths
    alt_paths = ["yolo.pt", "../yolo.pt", "yolo_terbaru.pt"]
    yolo_model = None
    for alt_path in alt_paths:
        if os.path.exists(alt_path):
            try:
                yolo_model = YOLO(alt_path)
                class_names = _apply_user_labels(_safe_class_names(yolo_model))
                print(f"✅ YOLO model loaded successfully from {alt_path}")
                break
            except Exception as e:
                print(f"❌ Failed to load model from {alt_path}: {e}")
                continue
    
    if yolo_model is None:
        print("⚠️ No YOLO model found, using default class names")
        class_names = {0: "normal", 1: "emotional stress", 2: "anxiety", 3: "depression"}

class UploadFileForm(FlaskForm):
    file = FileField("File",validators=[InputRequired()])
    submit = SubmitField("Run")

def process_yolo_detections(frame):
    """
    Process frame untuk deteksi YOLO dan simpan hasilnya
    """
    global yolo_detection_data, yolo_model
    
    if not yolo_detection_data['is_scanning'] or yolo_model is None:
        return frame
    
    try:
        # Lakukan prediksi YOLO
        results = yolo_model.predict(source=frame, conf=0.25, verbose=False)[0]
        boxes = results.boxes
        
        if boxes is not None and len(boxes):
            classes = boxes.cls.cpu().numpy().astype(int)
            confidences = boxes.conf.cpu().numpy()
            
            # Simpan deteksi ke data interval saat ini
            for cls, conf in zip(classes, confidences):
                if 0 <= cls < 4:  # Pastikan kelas valid (0-3)
                    yolo_detection_data['current_interval_data']['class_counts'][cls] += 1
                    yolo_detection_data['current_interval_data']['confidences'].append(float(conf))
    
    except Exception as e:
        print(f"Error in YOLO detection: {e}")
    
    return frame

def save_interval_data():
    """
    Simpan data deteksi untuk interval 10 detik
    """
    global yolo_detection_data
    
    if yolo_detection_data['is_scanning']:
        current_data = yolo_detection_data['current_interval_data'].copy()
        
        # Hitung confidence rata-rata untuk interval ini
        confidences = current_data['confidences']
        avg_confidence = np.mean(confidences) if confidences else 0.0
        
        # Simpan data interval
        interval_data = {
            'timestamp': datetime.now().isoformat(),
            'class_counts': current_data['class_counts'].copy(),
            'avg_confidence': float(avg_confidence),
            'total_detections': sum(current_data['class_counts'])
        }
        
        yolo_detection_data['detections'].append(interval_data)
        
        # Reset data untuk interval berikutnya
        yolo_detection_data['current_interval_data'] = {
            'class_counts': [0, 0, 0, 0], 
            'confidences': []
        }
        
        print(f"Saved interval data: {interval_data}")
        
        # Schedule next save (10 seconds)
        if yolo_detection_data['is_scanning']:
            threading.Timer(10.0, save_interval_data).start()

def get_final_yolo_result():
    """
    Mengembalikan kelas terbanyak dengan confidence tertinggi dari semua interval
    """
    global yolo_detection_data
    
    if not yolo_detection_data['detections']:
        return {
            'class_counts': [1, 0, 0, 0],  # Default normal
            'avg_confidence': 0.0,
            'total_detections': 0,
            'dominant_class': 0,
            'dominant_class_name': 'normal'
        }
    
    # Agregasi semua deteksi
    total_class_counts = [0, 0, 0, 0]
    all_confidences = []
    
    for detection in yolo_detection_data['detections']:
        for i in range(4):
            total_class_counts[i] += detection['class_counts'][i]
        if detection['avg_confidence'] > 0:
            all_confidences.append(detection['avg_confidence'])
    
    # Tentukan kelas dominan (yang paling banyak terdeteksi)
    dominant_class = np.argmax(total_class_counts)
    
    # Jika tidak ada deteksi sama sekali, default ke normal
    if sum(total_class_counts) == 0:
        total_class_counts[0] = 1
        dominant_class = 0
    
    result = {
        'class_counts': total_class_counts,
        'avg_confidence': float(np.mean(all_confidences)) if all_confidences else 0.0,
        'total_detections': sum(total_class_counts),
        'dominant_class': int(dominant_class),
        'dominant_class_name': class_names.get(dominant_class, 'unknown'),
        'intervals_data': yolo_detection_data['detections']
    }
    
    return result

def generate_frames(path_x = ''):
    yolo_output = video_detection(path_x)
    for detection_ in yolo_output:
        # Process frame untuk YOLO detection jika sedang scanning
        detection_ = process_yolo_detections(detection_)
        
        ref,buffer=cv2.imencode('.jpg',detection_)
        frame=buffer.tobytes()
        yield (b'--frame\r\n'
                    b'Content-Type: image/jpeg\r\n\r\n' + frame +b'\r\n')

def generate_frames_web(path_x):
    yolo_output = video_detection(path_x)
    for detection_ in yolo_output:
        # Process frame untuk YOLO detection jika sedang scanning
        detection_ = process_yolo_detections(detection_)
        
        ref,buffer=cv2.imencode('.jpg',detection_)
        frame=buffer.tobytes()
        yield (b'--frame\r\n'
                    b'Content-Type: image/jpeg\r\n\r\n' + frame +b'\r\n')

@app.route('/', methods=['GET','POST'])
@app.route('/home', methods=['GET','POST'])
def home():
    session.clear()
    return render_template('indexproject.html')

@app.route("/webcam", methods=['GET','POST'])
def webcam():
    session.clear()
    return render_template('ui.html')

@app.route('/FrontPage', methods=['GET','POST'])
def front():
    form = UploadFileForm()
    if form.validate_on_submit():
        file = form.file.data
        file.save(os.path.join(os.path.abspath(os.path.dirname(__file__)), app.config['UPLOAD_FOLDER'],
                               secure_filename(file.filename)))
        session['video_path'] = os.path.join(os.path.abspath(os.path.dirname(__file__)), app.config['UPLOAD_FOLDER'],
                                             secure_filename(file.filename))
    return render_template('videoprojectnew.html', form=form)

@app.route('/video')
def video():
    return Response(generate_frames(path_x = session.get('video_path', None)),mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/webapp')
def webapp():
    return Response(generate_frames_web(path_x=0), mimetype='multipart/x-mixed-replace; boundary=frame')

# API Endpoints untuk kontrol scanning YOLO
@app.route('/api/start_yolo_scan', methods=['POST'])
def start_yolo_scan():
    """
    Memulai scanning YOLO untuk 60 detik dengan pengumpulan data setiap 10 detik
    """
    global yolo_detection_data
    
    try:
        # Reset data
        yolo_detection_data = {
            'is_scanning': True,
            'scan_start_time': datetime.now().isoformat(),
            'detections': [],
            'current_interval_data': {'class_counts': [0, 0, 0, 0], 'confidences': []}
        }
        
        # Mulai timer untuk menyimpan data setiap 10 detik
        threading.Timer(10.0, save_interval_data).start()
        
        # Timer untuk menghentikan scanning setelah 60 detik
        def stop_scanning():
            yolo_detection_data['is_scanning'] = False
            print("YOLO scanning stopped after 60 seconds")
        
        threading.Timer(60.0, stop_scanning).start()
        
        return jsonify({
            'status': 'success',
            'message': 'YOLO scanning started for 60 seconds',
            'scan_start_time': yolo_detection_data['scan_start_time']
        })
    
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/get_yolo_result', methods=['GET'])
def get_yolo_result():
    """
    Mengembalikan hasil akhir YOLO detection
    """
    try:
        result = get_final_yolo_result()
        return jsonify({
            'status': 'success',
            'yolo_data': result,
            'is_scanning': yolo_detection_data['is_scanning']
        })
    
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/yolo_status', methods=['GET'])
def yolo_status():
    """
    Cek status scanning YOLO
    """
    return jsonify({
        'is_scanning': yolo_detection_data['is_scanning'],
        'scan_start_time': yolo_detection_data.get('scan_start_time'),
        'intervals_collected': len(yolo_detection_data['detections']),
        'current_interval': yolo_detection_data['current_interval_data']
    })

if __name__ == "__main__":
    # Gunakan port 5003 untuk menghindari konflik dengan start_flaskapp.sh (port 5001)
    app.run(host='0.0.0.0', port=5003, debug=True)