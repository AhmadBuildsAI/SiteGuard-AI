"""
Generate synthetic construction-site images for demo.
Uses PIL to draw simplified scenes: ground, workers (rectangles), helmets,
vests, equipment. Not photorealistic — VLM may or may not detect them,
but the demo runs end-to-end regardless.
"""
import random
from pathlib import Path
from datetime import datetime
from PIL import Image, ImageDraw
from sqlalchemy.orm import Session
from ..models.inspection import Inspection
from ..models.alert import Alert
from ..core.config import settings


SCENES = [
    {
        "name": "North Construction Area",
        "workers": 4,
        "missing_helmets": 1,
        "missing_vests": 0,
        "has_excavator": True,
        "has_barrier": True,
    },
    {
        "name": "Foundation Zone",
        "workers": 6,
        "missing_helmets": 0,
        "missing_vests": 2,
        "has_excavator": False,
        "has_barrier": True,
    },
    {
        "name": "Steel Structure Area",
        "workers": 3,
        "missing_helmets": 0,
        "missing_vests": 0,
        "has_excavator": False,
        "has_barrier": True,
    },
    {
        "name": "Excavation Zone East",
        "workers": 5,
        "missing_helmets": 2,
        "missing_vests": 1,
        "has_excavator": True,
        "has_barrier": False,
    },
]


def _draw_site(scene_spec: dict, width: int = 800, height: int = 500) -> Image.Image:
    img = Image.new("RGB", (width, height), (200, 210, 220))
    draw = ImageDraw.Draw(img)
    
    # Sky gradient
    for y in range(height // 2):
        c = 200 + int(30 * y / (height // 2))
        draw.line([(0, y), (width, y)], fill=(c, c + 5, c + 20))
    
    # Ground
    draw.rectangle([0, height // 2, width, height], fill=(160, 140, 110))
    for x in range(0, width, 40):
        draw.line([(x, height // 2 + 100), (x + 20, height - 20)], fill=(140, 120, 90), width=1)
    
    # Barriers (yellow/black)
    if scene_spec["has_barrier"]:
        draw.rectangle([50, height // 2 + 20, 250, height // 2 + 40], fill=(240, 200, 30))
        draw.rectangle([600, height // 2 + 20, 780, height // 2 + 40], fill=(240, 200, 30))
    
    # Excavator (rough)
    if scene_spec["has_excavator"]:
        draw.rectangle([550, height // 2 - 40, 700, height // 2 + 30], fill=(220, 180, 40))
        draw.rectangle([570, height // 2 - 90, 640, height // 2 - 40], fill=(220, 180, 40))
        draw.ellipse([560, height // 2 + 20, 610, height // 2 + 60], fill=(40, 40, 40))
        draw.ellipse([640, height // 2 + 20, 690, height // 2 + 60], fill=(40, 40, 40))
        # Arm
        draw.line([(640, height // 2 - 60), (760, height // 2 - 20)], fill=(30, 30, 30), width=6)
    
    # Workers (as simple figures)
    worker_positions = []
    for i in range(scene_spec["workers"]):
        wx = 80 + i * 120 + random.randint(-20, 20)
        wy = height // 2 + 60 + random.randint(-30, 30)
        worker_positions.append((wx, wy))
        
        # Body
        draw.rectangle([wx - 12, wy - 40, wx + 12, wy], fill=(70, 90, 140))
        # Head
        draw.ellipse([wx - 10, wy - 60, wx + 10, wy - 40], fill=(230, 200, 160))
        
        # Helmet (if not missing)
        if i >= scene_spec["missing_helmets"]:
            draw.ellipse([wx - 12, wy - 66, wx + 12, wy - 48], fill=(240, 200, 30))
        
        # Vest (if not missing)
        if i >= scene_spec["missing_vests"]:
            draw.rectangle([wx - 10, wy - 38, wx + 10, wy - 10], fill=(240, 240, 30))
    
    return img


def ensure_seed_data(db: Session) -> None:
    from ..models.user import User
    if db.query(Inspection).count() > 0:
        return
    
    admin = db.query(User).filter(User.email == "admin@siteguard.com").first()
    if not admin:
        return
    
    upload_dir = Path(settings.UPLOAD_DIR)
    upload_dir.mkdir(parents=True, exist_ok=True)
    
    for i, spec in enumerate(SCENES):
        img = _draw_site(spec)
        filename = f"seed_{i+1}.jpg"
        path = upload_dir / filename
        img.save(path, "JPEG", quality=85)
        
        # Manually build synthetic scene_analysis + violations (skip VLM for seed)
        workers = []
        for j in range(spec["workers"]):
            workers.append({
                "id": f"Worker #{j+1}",
                "approx_bbox": [80 + j * 120 - 15, 250, 30, 80],
                "has_helmet": j >= spec["missing_helmets"],
                "has_vest": j >= spec["missing_vests"],
                "in_restricted_zone": False,
                "near_heavy_equipment": spec["has_excavator"] and j == spec["workers"] - 1,
            })
        
        scene = {
            "workers": workers,
            "helmets": [{"approx_bbox": [80 + j * 120 - 15, 240, 30, 20]} for j in range(spec["workers"] - spec["missing_helmets"])],
            "vests": [{"approx_bbox": [80 + j * 120 - 15, 280, 30, 40]} for j in range(spec["workers"] - spec["missing_vests"])],
            "barriers": [{"approx_bbox": [50, 270, 200, 20]}] if spec["has_barrier"] else [],
            "equipment": [{"label": "excavator", "approx_bbox": [550, 210, 150, 70]}] if spec["has_excavator"] else [],
            "restricted_zones": [],
            "scene_observations": [
                f"Approximately {spec['workers']} workers visible in the frame.",
                f"{spec['missing_helmets']} worker(s) may not be wearing visible head protection." if spec["missing_helmets"] else "Head protection appears present on visible workers.",
                "Synthetic demo scene — replace with real site imagery for evaluation.",
            ],
            "site_organization": "acceptable",
            "active_construction_zone": True,
            "overall_scene": "Synthetic seed scene for demonstration.",
        }
        
        # Run rule engine
        from .rule_engine import evaluate as run_rules
        violations = run_rules(scene, [], (800, 500))
        
        from .scoring_service import compute_scores, build_explanation
        scores = compute_scores(scene, violations)
        explanation = build_explanation(scene, violations)
        
        inspection = Inspection(
            inspection_ref=f"INSP-{1001 + i}",
            site_name=spec["name"],
            filename=filename,
            image_path=str(path),
            image_width=800,
            image_height=500,
            detections=[],
            scene_analysis=scene,
            violations=violations,
            safety_score=scores["safety_score"],
            ppe_score=scores["ppe_score"],
            zone_score=scores["zone_score"],
            equipment_score=scores["equipment_score"],
            organization_score=scores["organization_score"],
            risk_level=scores["risk_level"],
            worker_count=spec["workers"],
            helmet_count=spec["workers"] - spec["missing_helmets"],
            vest_count=spec["workers"] - spec["missing_vests"],
            equipment_count=len(scene["equipment"]),
            vlm_used="false",
            explanation=explanation,
            created_by=admin.id,
        )
        db.add(inspection)
        db.flush()
        
        for v in violations:
            db.add(Alert(
                inspection_id=inspection.id,
                rule_id=v["rule_id"],
                severity=v["severity"],
                title=v["title"],
                message=v["message"],
                vlm_observation=v.get("vlm_observation"),
                evidence=v.get("evidence"),
                confidence=v.get("confidence", 0.5),
            ))
    
    db.commit()
