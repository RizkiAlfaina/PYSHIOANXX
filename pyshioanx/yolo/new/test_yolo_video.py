#!/usr/bin/env python3
"""
Test script untuk YOLO Video Detection
Penggunaan: python test_yolo_video.py
"""

import cv2
import sys
import os
from yolo_detect_calibrated import video_detection

def main():
    print("=== YOLO Video Detection Test ===")
    print("Pilih input source:")
    print("1. Webcam (default)")
    print("2. Video file")
    print("3. Custom input")
    
    choice = input("Masukkan pilihan (1-3) [default: 1]: ").strip()
    
    if choice == "2":
        video_path = input("Masukkan path video file: ").strip()
        if not os.path.exists(video_path):
            print(f"Error: File {video_path} tidak ditemukan!")
            return
        path_x = video_path
    elif choice == "3":
        custom_input = input("Masukkan custom input (contoh: 0 untuk webcam, rtsp://... untuk IP cam): ").strip()
        try:
            # Coba convert ke int jika input adalah angka (untuk webcam index)
            path_x = int(custom_input)
        except ValueError:
            # Jika bukan angka, gunakan sebagai string (untuk file path atau URL)
            path_x = custom_input
    else:
        # Default ke webcam
        path_x = 0
    
    print(f"Menggunakan input: {path_x}")
    print("Tekan 'q' untuk keluar, 's' untuk screenshot")
    print("Memulai deteksi...")
    
    try:
        # Test generator function
        frame_count = 0
        for frame in video_detection(path_x):
            frame_count += 1
            
            # Tampilkan frame
            cv2.imshow("YOLO Detection Test", frame)
            
            # Handle keyboard input
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                print("Keluar dari program...")
                break
            elif key == ord('s'):
                # Save screenshot
                filename = f"screenshot_{frame_count:06d}.jpg"
                cv2.imwrite(filename, frame)
                print(f"Screenshot disimpan: {filename}")
            
            # Print info setiap 30 frame
            if frame_count % 30 == 0:
                print(f"Frame ke-{frame_count} diproses")
                
    except KeyboardInterrupt:
        print("\nProgram dihentikan oleh user")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        cv2.destroyAllWindows()
        print("Selesai")

if __name__ == "__main__":
    main()