"""
Draw bounding boxes on the uploaded image based on detections + VLM bboxes.
Returns base64 PNG (data URI) for the frontend.
"""
import base64
import io
from pathlib import Path
from typing import List, Dict
from PIL import Image, ImageDraw, ImageFont


COLORS = {
    "person":  "#3b82f6",
    "worker":  "#3b82f6",
    "helmet":  "#22c55e",
    "vest":    "#eab308",
    "barrier": "#a855f7",
    "equipment": "#ef4444",
    "restricted_zone": "#dc2626",
    "default": "#6b7280",
}


def draw_overlay(image_path: Path, detections: List[Dict], scene: Dict) -> str:
    """Return base64 data URI of image with drawn boxes."""
    try:
        img = Image.open(image_path).convert("RGB")
        draw = ImageDraw.Draw(img)
        
        # Try to load a small font
        try:
            font = ImageFont.truetype("DejaVuSans-Bold.ttf", 14)
        except Exception:
            font = ImageFont.load_default()
        
        # YOLO detections
        for det in detections:
            _draw_box(draw, det["bbox"], det["label"], COLORS.get(det["label"], COLORS["default"]), font)
        
        # VLM workers
        for w in scene.get("workers", []):
            bbox = w.get("approx_bbox")
            if bbox and len(bbox) == 4:
                color = "#dc2626" if w.get("in_restricted_zone") or w.get("has_helmet") is False else COLORS["worker"]
                _draw_box(draw, bbox, w.get("id", "worker"), color, font)
        
        # Helmets
        for h in scene.get("helmets", []):
            bbox = h.get("approx_bbox")
            if bbox and len(bbox) == 4:
                _draw_box(draw, bbox, "helmet", COLORS["helmet"], font)
        
        # Vests
        for v in scene.get("vests", []):
            bbox = v.get("approx_bbox")
            if bbox and len(bbox) == 4:
                _draw_box(draw, bbox, "vest", COLORS["vest"], font)
        
        # Restricted zones
        for z in scene.get("restricted_zones", []):
            bbox = z.get("approx_bbox")
            if bbox and len(bbox) == 4:
                _draw_box(draw, bbox, z.get("label", "restricted"), COLORS["restricted_zone"], font, dashed=True)
        
        # Encode to base64
        buf = io.BytesIO()
        img.save(buf, format="JPEG", quality=85)
        encoded = base64.b64encode(buf.getvalue()).decode("utf-8")
        return f"data:image/jpeg;base64,{encoded}"
    except Exception as e:
        print(f"Overlay error: {e}")
        return ""


def _draw_box(draw, bbox, label, color, font, dashed=False):
    try:
        x, y, w, h = [float(v) for v in bbox]
        x2, y2 = x + w, y + h
        if dashed:
            # Draw dashed rectangle manually
            _dashed_rect(draw, x, y, x2, y2, color, dash=8)
        else:
            draw.rectangle([x, y, x2, y2], outline=color, width=3)
        # Label background
        tw, th = draw.textbbox((0, 0), label, font=font)[2:4]
        draw.rectangle([x, y - th - 4, x + tw + 6, y], fill=color)
        draw.text((x + 3, y - th - 2), label, fill="white", font=font)
    except Exception:
        pass


def _dashed_rect(draw, x1, y1, x2, y2, color, dash=8):
    for x in range(int(x1), int(x2), dash * 2):
        draw.line([(x, y1), (min(x + dash, x2), y1)], fill=color, width=2)
        draw.line([(x, y2), (min(x + dash, x2), y2)], fill=color, width=2)
    for y in range(int(y1), int(y2), dash * 2):
        draw.line([(x1, y), (x1, min(y + dash, y2))], fill=color, width=2)
        draw.line([(x2, y), (x2, min(y + dash, y2))], fill=color, width=2)
