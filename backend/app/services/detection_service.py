"""
YOLO-based object detection (optional).
If ultralytics not installed or weights missing, returns empty list — VLM does the work.
"""
from pathlib import Path
from typing import List, Dict


_yolo_model = None
_yolo_loaded = False


def _try_load_yolo():
    global _yolo_model, _yolo_loaded
    if _yolo_loaded:
        return
    _yolo_loaded = True
    try:
        from ultralytics import YOLO
        # Load the smallest pretrained model (COCO classes: person, car, truck, etc.)
        _yolo_model = YOLO("yolov8n.pt")
        print("✅ YOLOv8n loaded")
    except Exception as e:
        print(f"⚠️  YOLO unavailable ({e}) — VLM will do detection")
        _yolo_model = None


def detect_objects(image_path: Path) -> List[Dict]:
    """
    Run YOLO and return [{'label', 'bbox': [x, y, w, h], 'confidence', 'source'}]
    """
    _try_load_yolo()
    if _yolo_model is None:
        return []
    
    try:
        results = _yolo_model(str(image_path), verbose=False)
        detections = []
        for r in results:
            boxes = r.boxes
            for box in boxes:
                cls_id = int(box.cls[0].item())
                label = _yolo_model.names[cls_id]
                conf = float(box.conf[0].item())
                xyxy = box.xyxy[0].tolist()  # [x1, y1, x2, y2]
                x1, y1, x2, y2 = xyxy
                detections.append({
                    "label": label,
                    "bbox": [round(x1, 1), round(y1, 1), round(x2 - x1, 1), round(y2 - y1, 1)],
                    "confidence": round(conf, 3),
                    "source": "yolo",
                })
        return detections
    except Exception as e:
        print(f"YOLO inference error: {e}")
        return []


def summarize_for_vlm(detections: List[Dict]) -> str:
    if not detections:
        return "(no YOLO detections)"
    from collections import Counter
    c = Counter(d["label"] for d in detections)
    return ", ".join(f"{k}×{v}" for k, v in c.items())
