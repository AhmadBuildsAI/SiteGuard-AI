"""
VLM scene analysis — sends image + YOLO hints to Gemini/OpenAI.
Returns structured JSON with workers, PPE, zones, equipment, observations.
"""
import base64
from pathlib import Path
from typing import Dict
from ..core.vlm_client import vlm_client
from ..core.config import settings


SYSTEM_PROMPT = """You are a construction-site safety observer AI.

Analyze the provided image and return STRICT JSON with these fields:

{
  "workers": [
    {
      "id": "Worker #1",
      "approx_bbox": [x, y, w, h],
      "has_helmet": true|false|"uncertain",
      "has_vest": true|false|"uncertain",
      "in_restricted_zone": true|false|"uncertain",
      "near_heavy_equipment": true|false|"uncertain"
    }
  ],
  "helmets":     [{"approx_bbox": [x,y,w,h], "confidence": 0.0-1.0}],
  "vests":       [{"approx_bbox": [x,y,w,h], "confidence": 0.0-1.0}],
  "barriers":    [{"approx_bbox": [x,y,w,h]}],
  "equipment":   [{"label": "excavator|crane|truck|...", "approx_bbox": [x,y,w,h]}],
  "restricted_zones": [{"label": "...", "approx_bbox": [x,y,w,h]}],
  "scene_observations": [
    "one short plain-language sentence per observation"
  ],
  "site_organization": "good|acceptable|cluttered|poor",
  "active_construction_zone": true|false,
  "overall_scene": "one sentence summary of what's happening"
}

RULES:
1. Bounding boxes are approximate — estimate from the image. Use pixel coordinates.
2. If you cannot see something clearly, mark it as "uncertain" — do NOT guess.
3. NEVER identify individual people by name or face.
4. Use phrases like "appears to", "may be", "potential" — never "confirmed".
5. Do NOT make diagnoses or recommendations about individuals.
6. Only return JSON. No prose outside the JSON object."""


def analyze_scene(image_path: Path, yolo_summary: str) -> Dict:
    if not vlm_client.enabled or not vlm_client.has_vision:
        return _fallback_scene(yolo_summary)
    
    try:
        image_bytes = image_path.read_bytes()
        image_b64 = base64.b64encode(image_bytes).decode("utf-8")
        result = vlm_client.analyze_image(image_b64, yolo_summary, SYSTEM_PROMPT)
        if result.get("error"):
            print(f"VLM error: {result['error']}")
            return _fallback_scene(yolo_summary)
        
        # Normalize defaults
        result.setdefault("workers", [])
        result.setdefault("helmets", [])
        result.setdefault("vests", [])
        result.setdefault("barriers", [])
        result.setdefault("equipment", [])
        result.setdefault("restricted_zones", [])
        result.setdefault("scene_observations", [])
        result.setdefault("site_organization", "acceptable")
        result.setdefault("active_construction_zone", True)
        result.setdefault("overall_scene", "")
        return result
    except Exception as e:
        print(f"VLM service error: {e}")
        return _fallback_scene(yolo_summary)


def _fallback_scene(yolo_summary: str) -> Dict:
    """Deterministic fallback when VLM unavailable."""
    return {
        "workers": [],
        "helmets": [],
        "vests": [],
        "barriers": [],
        "equipment": [],
        "restricted_zones": [],
        "scene_observations": [
            "Automated scene analysis unavailable — VLM provider not configured.",
            f"YOLO detected: {yolo_summary}",
        ],
        "site_organization": "unknown",
        "active_construction_zone": True,
        "overall_scene": "Limited analysis — configure VLM_PROVIDER and VLM_API_KEY for full scene understanding.",
    }
