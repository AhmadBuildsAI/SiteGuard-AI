"""
Compute safety score and category breakdowns from violations + scene analysis.
"""
from typing import Dict, List


def compute_scores(scene: Dict, violations: List[Dict]) -> Dict:
    workers = scene.get("workers", [])
    worker_count = max(1, len(workers))
    
    critical = sum(1 for v in violations if v["severity"] == "CRITICAL")
    high = sum(1 for v in violations if v["severity"] == "HIGH")
    medium = sum(1 for v in violations if v["severity"] == "MEDIUM")
    low = sum(1 for v in violations if v["severity"] == "LOW")
    
    overall = 100.0 - (
        40.0 * (critical / worker_count)
        + 25.0 * (high / worker_count)
        + 15.0 * (medium / worker_count)
        + 5.0 * low
    )
    overall = max(0.0, min(100.0, overall))
    
    # Category breakdown
    ppe = 100.0
    zone = 100.0
    equipment_safety = 100.0
    organization = 100.0
    
    for v in violations:
        rid = v["rule_id"]
        if rid in ("R1_HELMET_REQUIRED", "R2_VEST_REQUIRED"):
            ppe -= 20 if v["severity"] == "HIGH" else 12
        elif rid == "R3_RESTRICTED_ZONE":
            zone -= 40
        elif rid == "R4_EQUIPMENT_PROXIMITY":
            equipment_safety -= 25
        elif rid == "R5_MISSING_BARRIER":
            organization -= 12
        elif rid == "R6_SITE_ORGANIZATION":
            organization -= 10 if v["severity"] == "MEDIUM" else 5
    
    ppe = max(0.0, ppe)
    zone = max(0.0, zone)
    equipment_safety = max(0.0, equipment_safety)
    organization = max(0.0, organization)
    
    # Risk level
    if overall >= 85:
        risk = "LOW"
    elif overall >= 65:
        risk = "MEDIUM"
    elif overall >= 45:
        risk = "HIGH"
    else:
        risk = "CRITICAL"
    
    return {
        "safety_score": round(overall, 1),
        "ppe_score": round(ppe, 1),
        "zone_score": round(zone, 1),
        "equipment_score": round(equipment_safety, 1),
        "organization_score": round(organization, 1),
        "risk_level": risk,
    }


def build_explanation(scene: Dict, violations: List[Dict]) -> str:
    obs = scene.get("scene_observations", [])
    overall = scene.get("overall_scene", "")
    parts = []
    if overall:
        parts.append(overall)
    if obs:
        parts.extend(f"• {o}" for o in obs[:5])
    if violations:
        parts.append(f"\n{len(violations)} potential safety observation(s) flagged for human review.")
    else:
        parts.append("\nNo obvious safety concerns detected in this frame.")
    return "\n".join(parts)
