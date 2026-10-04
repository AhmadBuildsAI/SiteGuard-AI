# Object Detection

Ultralytics YOLOv8n (pretrained on COCO) runs if `ultralytics` is installed.
If unavailable, the app silently falls back to VLM-only detection.

YOLO COCO classes include: person, car, truck — but NOT helmet/vest/barrier.
The VLM handles PPE detection; YOLO provides robust person detection.

Implementation: `backend/app/services/detection_service.py`
