#!/usr/bin/env python3
"""
Quick test script untuk YOLO Video Detection
Langsung menggunakan webcam tanpa input menu
"""

import cv2
from YOLO_Video import video_detection

def quick_test():
    print("Quick YOLO Test - Menggunakan webcam (index 0)")
    print("Tekan 'q' untuk keluar")
    
    try:
        for frame in video_detection(0):  # 0 = default webcam
            cv2.imshow("Quick YOLO Test", frame)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
                
    except Exception as e:
        print(f"Error: {e}")
    finally:
        cv2.destroyAllWindows()

if __name__ == "__main__":
    quick_test()