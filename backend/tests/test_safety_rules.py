from app.services.rule_engine import evaluate
from app.services.scoring_service import compute_scores


def test_all_safety_rules_trigger_on_synthetic_case():
    scene = {
        "workers": [{
            "id": "Worker #1", "approx_bbox": [10, 20, 30, 80],
            "has_helmet": False, "has_vest": False,
            "in_restricted_zone": True, "near_heavy_equipment": True,
        }],
        "helmets": [], "vests": [], "barriers": [],
        "equipment": [{"label": "excavator"}],
        "restricted_zones": [{"label": "excavation"}],
        "scene_observations": [], "site_organization": "cluttered",
    }
    violations = evaluate(scene, [], (800, 500))
    assert {v["rule_id"] for v in violations} == {
        "R1_HELMET_REQUIRED", "R2_VEST_REQUIRED", "R3_RESTRICTED_ZONE",
        "R4_EQUIPMENT_PROXIMITY", "R5_MISSING_BARRIER", "R6_SITE_ORGANIZATION",
    }
    assert compute_scores(scene, violations)["risk_level"] == "CRITICAL"


def test_clean_scene_has_no_alerts():
    scene = {
        "workers": [{"id": "Worker #1", "has_helmet": True, "has_vest": True,
                     "in_restricted_zone": False, "near_heavy_equipment": False}],
        "helmets": [{}], "vests": [{}], "barriers": [{}],
        "equipment": [], "restricted_zones": [],
        "scene_observations": [], "site_organization": "good",
    }
    assert evaluate(scene, [], (800, 500)) == []
