"""
Deterministic safety rule engine.
Takes scene_analysis (VLM output) + YOLO detections → list of violations.
NEVER produces automatic disciplinary action. Always flags "requires human review".
"""
from typing import Dict, List


def _sev(severity: str) -> str:
    return severity.upper()


def evaluate(scene: Dict, yolo_detections: List[Dict], image_size: tuple) -> List[Dict]:
    """
    Returns list of violations:
      {rule_id, severity, title, message, evidence, confidence, vlm_observation}
    """
    violations = []
    workers = scene.get("workers", [])
    helmets = scene.get("helmets", [])
    vests = scene.get("vests", [])
    equipment = scene.get("equipment", [])
    restricted = scene.get("restricted_zones", [])
    observations = scene.get("scene_observations", [])
    organization = scene.get("site_organization", "acceptable")
    
    # Rule 1 — Worker without helmet
    for w in workers:
        if w.get("has_helmet") is False:
            violations.append({
                "rule_id": "R1_HELMET_REQUIRED",
                "severity": "HIGH",
                "title": f"Potential missing head protection ({w.get('id', 'worker')})",
                "message": (
                    f"{w.get('id', 'A worker')} appears to be in an active construction area "
                    f"without visible head protection. Human safety inspector verification required."
                ),
                "evidence": {"worker": w.get("id"), "bbox": w.get("approx_bbox")},
                "confidence": 0.75,
                "vlm_observation": "head protection not visible",
            })
    
    # Rule 2 — Worker without vest
    for w in workers:
        if w.get("has_vest") is False:
            violations.append({
                "rule_id": "R2_VEST_REQUIRED",
                "severity": "MEDIUM",
                "title": f"Potential missing safety vest ({w.get('id', 'worker')})",
                "message": (
                    f"{w.get('id', 'A worker')} may not be wearing a high-visibility vest in an "
                    f"active zone. Human safety inspector verification required."
                ),
                "evidence": {"worker": w.get("id"), "bbox": w.get("approx_bbox")},
                "confidence": 0.7,
                "vlm_observation": "safety vest not visible",
            })
    
    # Rule 3 — Worker inside restricted zone
    for w in workers:
        if w.get("in_restricted_zone") is True:
            violations.append({
                "rule_id": "R3_RESTRICTED_ZONE",
                "severity": "CRITICAL",
                "title": f"Potential restricted-zone entry ({w.get('id', 'worker')})",
                "message": (
                    f"{w.get('id', 'A worker')} appears to be inside a restricted zone. "
                    f"Human safety inspector verification required before any action."
                ),
                "evidence": {"worker": w.get("id"), "bbox": w.get("approx_bbox")},
                "confidence": 0.75,
                "vlm_observation": "positioned within restricted region",
            })
    
    # Rule 4 — Worker near heavy equipment
    for w in workers:
        if w.get("near_heavy_equipment") is True:
            violations.append({
                "rule_id": "R4_EQUIPMENT_PROXIMITY",
                "severity": "HIGH",
                "title": f"Potential unsafe equipment proximity ({w.get('id', 'worker')})",
                "message": (
                    f"{w.get('id', 'A worker')} appears to be within close proximity to heavy "
                    f"equipment. Human safety inspector verification recommended."
                ),
                "evidence": {"worker": w.get("id"), "bbox": w.get("approx_bbox")},
                "confidence": 0.65,
                "vlm_observation": "close to operating equipment",
            })
    
    # Rule 5 — Missing barrier around restricted zone
    if restricted and not scene.get("barriers"):
        violations.append({
            "rule_id": "R5_MISSING_BARRIER",
            "severity": "MEDIUM",
            "title": "Potential missing barrier around restricted zone",
            "message": (
                "A restricted or excavation zone is visible without an obvious physical "
                "barrier. Human safety inspector verification recommended."
            ),
            "evidence": {"restricted_zones": len(restricted)},
            "confidence": 0.6,
            "vlm_observation": "barrier not detected in frame",
        })
    
    # Rule 6 — Site organization
    if organization == "cluttered":
        violations.append({
            "rule_id": "R6_SITE_ORGANIZATION",
            "severity": "LOW",
            "title": "Site organization may need attention",
            "message": (
                "The scene appears cluttered based on the visual analysis. This is a general "
                "observation for review, not a specific violation."
            ),
            "evidence": {"organization": organization},
            "confidence": 0.5,
            "vlm_observation": "cluttered appearance",
        })
    elif organization == "poor":
        violations.append({
            "rule_id": "R6_SITE_ORGANIZATION",
            "severity": "MEDIUM",
            "title": "Site organization may need attention",
            "message": (
                "The scene appears poorly organized based on the visual analysis. "
                "Human safety inspector review recommended."
            ),
            "evidence": {"organization": organization},
            "confidence": 0.6,
            "vlm_observation": "poor organization detected",
        })
    
    return violations
