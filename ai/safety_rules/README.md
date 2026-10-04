# Safety Rule Engine

Deterministic rules (never rely on VLM alone):

| Rule | Severity | Trigger |
|------|----------|---------|
| R1_HELMET_REQUIRED | HIGH | worker.has_helmet == false |
| R2_VEST_REQUIRED | MEDIUM | worker.has_vest == false |
| R3_RESTRICTED_ZONE | CRITICAL | worker.in_restricted_zone == true |
| R4_EQUIPMENT_PROXIMITY | HIGH | worker.near_heavy_equipment == true |
| R5_MISSING_BARRIER | MEDIUM | restricted zone visible without barrier |
| R6_SITE_ORGANIZATION | LOW/MEDIUM | VLM rates organization "cluttered"/"poor" |

Every rule emits: rule_id, severity, title, message, evidence, confidence.

Implementation: `backend/app/services/rule_engine.py`
