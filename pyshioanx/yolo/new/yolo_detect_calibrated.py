import os, time, json
import cv2, numpy as np
from ultralytics import YOLO

cv2.setUseOptimized(True)
try:
    cv2.setNumThreads(2)
except Exception:
    pass

def _safe_class_names(model, default_n=80):
    names = getattr(model, "names", None)
    if isinstance(names, dict):
        return names
    if isinstance(names, (list, tuple)):
        return {i: n for i, n in enumerate(names)}
    return {i: f"class_{i}" for i in range(default_n)}

def _apply_user_labels(existing_names):
    """Override names with user's mapping when model has 4 classes with ids 0..3."""
    user_map = {0: "normal", 1: "emotional stress", 2: "anxiety", 3: "depression"}
    try:
        keys = set(int(k) for k in existing_names.keys())
    except Exception:
        return existing_names
    if keys == set(user_map.keys()) and len(existing_names) == 4:
        return user_map
    return existing_names

def _clip_box(x1, y1, x2, y2, W, H):
    return max(0, int(x1)), max(0, int(y1)), min(W-1, int(x2)), min(H-1, int(y2))

def _draw_label(img, x1, y1, text, color=(68,148,228)):
    tsize, _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
    tw, th = tsize
    y_top = max(0, y1 - th - 6)
    cv2.rectangle(img, (x1, y_top), (x1 + tw + 6, y_top + th + 6), color, -1, cv2.LINE_AA)
    cv2.putText(img, text, (x1 + 3, y_top + th), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,0), 1, cv2.LINE_AA)

# ---------- Calibration helpers ----------
def _temp_scale_scalar(prob, T):
    p = float(np.clip(prob, 1e-6, 1-1e-6))
    z = np.log(p/(1-p))
    return float(1.0/(1.0 + np.exp(-z/float(T))))

def _load_calibration(calib_json):
    params = {}
    if calib_json and os.path.exists(calib_json):
        try:
            with open(calib_json, 'r') as f:
                params = json.load(f)
            print(f"[CAL] Loaded per-class params from {calib_json} ({len(params)} classes).")
        except Exception as e:
            print(f"[CAL] Could not read {calib_json}: {e}. Using raw confidences.")
    return params

def _calibrate_conf_and_threshold(cls_idx, p_raw, global_thr, params_dict, enabled=True):
    if not enabled:
        return float(p_raw), float(global_thr)
    d = params_dict.get(str(int(cls_idx)))
    if d is None:
        return float(p_raw), float(global_thr)
    T   = float(d.get("T", 1.0))
    thr = float(d.get("thr", 0.0))
    p_final = _temp_scale_scalar(p_raw, T)
    thr_eff = max(thr, float(global_thr))
    return p_final, thr_eff

def video_detection(path_x,
                    model_path="yolo_terbaru_ncnn_model",
                    imgsz=640,
                    conf=0.25,
                    iou=0.45,
                    cam_w=640, cam_h=480,
                    calib_json='calibration_params.json',
                    enable_calib=True,
                    show_fps=True):
    """
    Calibrated YOLO video detection. Compatible with test_yolo_video.py.
    Yields annotated frames with improved FPS.
    """
    # Video capture
    cap = cv2.VideoCapture(path_x)
    if cam_w and cam_h:
        cap.set(cv2.CAP_PROP_FRAME_WIDTH,  cam_w)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, cam_h)
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
    try:
        cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*"MJPG"))
    except Exception:
        pass
    if not cap.isOpened():
        raise RuntimeError("Cannot open video source.")

    # Load model and calibration
    model = YOLO(model_path)
    classNames = _apply_user_labels(_safe_class_names(model))
    calib_params = _load_calibration(calib_json) if enable_calib else {}

    # FPS smoothing
    frame_times = []
    N = 30
    frame_idx = 0

    while True:
        t0 = time.perf_counter()
        ok, frame = cap.read()
        if not ok or frame is None:
            time.sleep(0.005)
            continue

        H, W = frame.shape[:2]

        # Inference on original frame (no cropping)
        res = model.predict(source=frame, imgsz=imgsz, conf=conf, iou=iou, verbose=False, device='cpu')[0]
        boxes = res.boxes

        # Draw detections with calibrated confidences
        if boxes is not None and len(boxes):
            xyxy = boxes.xyxy.cpu().numpy()
            confs = boxes.conf.cpu().numpy()
            clses = boxes.cls.cpu().numpy().astype(int)

            for (bx1, by1, bx2, by2), p_raw, cls in zip(xyxy, confs, clses):
                p_show, thr_eff = _calibrate_conf_and_threshold(cls, float(p_raw), conf, calib_params, enabled=enable_calib)
                if p_show < thr_eff:
                    continue
                x1, y1, x2, y2 = _clip_box(bx1, by1, bx2, by2, W, H)
                color = (68, 148, 228)  # blue
                cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                cname = classNames.get(int(cls), str(int(cls)))
                _draw_label(frame, x1, y1, f"{cname} {p_show:.2f}", color)

        # HUD
        dt = max(time.perf_counter() - t0, 1e-6)
        fps = 1.0/dt
        frame_times.append(fps)
        if len(frame_times) > N:
            frame_times.pop(0)
        avg_fps = float(np.mean(frame_times))
        if show_fps:
            cv2.putText(frame, f"FPS: {avg_fps:0.2f}", (10, 22),
                        cv2.FONT_HERSHEY_SIMPLEX, .7, (0,255,255), 2)
            cv2.putText(frame, f"Calib: {'ON' if enable_calib else 'OFF'} thr>={conf:.2f}", (10, 44),
                        cv2.FONT_HERSHEY_SIMPLEX, .5, (200,200,200), 1)

        frame_idx += 1
        yield frame

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", default="0", help="Camera index, video file path, or RTSP URL")
    parser.add_argument("--model", default="best.pt", help="Path to YOLO weights (.pt or .onnx)")
    parser.add_argument("--imgsz", type=int, default=640)
    parser.add_argument("--conf", type=float, default=0.25)
    parser.add_argument("--iou", type=float, default=0.45)
    parser.add_argument("--width", type=int, default=640)
    parser.add_argument("--height", type=int, default=480)
    parser.add_argument("--calib-json", default="calibration_params.json")
    parser.add_argument("--calib", action="store_true", help="Enable calibration")
    args = parser.parse_args()

    try:
        src = int(args.source)
    except ValueError:
        src = args.source

    def _show(gen):
        import cv2
        for fr in gen:
            cv2.imshow("Calibrated YOLO", fr)
            if (cv2.waitKey(1) & 0xFF) == ord('q'):
                break
        cv2.destroyAllWindows()

    _show(video_detection(src,
                          model_path=args.model,
                          imgsz=args.imgsz,
                          conf=args.conf,
                          iou=args.iou,
                          cam_w=args.width, cam_h=args.height,
                          calib_json=args.calib_json,
                          enable_calib=args.calib))
