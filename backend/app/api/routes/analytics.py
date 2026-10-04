from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from ...core.database import get_db
from ...core.config import settings
from ...models.inspection import Inspection
from ...models.alert import Alert
from ...models.user import User
from ...schemas.inspection import DashboardData
from ...api.dependencies.auth import get_current_user
from ...core.vlm_client import vlm_client
from ...services import detection_service

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/dashboard", response_model=DashboardData)
def dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    inspections = db.query(Inspection).filter(Inspection.created_by == current_user.id).all()
    inspection_ids = [str(i.id) for i in inspections]
    alerts = db.query(Alert).filter(Alert.inspection_id.in_(inspection_ids)).all() if inspection_ids else []
    
    avg_score = sum(i.safety_score for i in inspections) / max(1, len(inspections))
    
    critical = sum(1 for a in alerts if a.severity == "CRITICAL")
    high = sum(1 for a in alerts if a.severity == "HIGH")
    
    risk_dist = {
        "LOW": sum(1 for i in inspections if i.risk_level == "LOW"),
        "MEDIUM": sum(1 for i in inspections if i.risk_level == "MEDIUM"),
        "HIGH": sum(1 for i in inspections if i.risk_level == "HIGH"),
        "CRITICAL": sum(1 for i in inspections if i.risk_level == "CRITICAL"),
    }
    
    trend = sorted(
        [{"date": i.created_at.date().isoformat(), "score": i.safety_score} for i in inspections],
        key=lambda x: x["date"],
    )
    
    recent = sorted(inspections, key=lambda i: i.created_at, reverse=True)[:5]
    
    return DashboardData(
        total_inspections=len(inspections),
        total_alerts=len(alerts),
        avg_safety_score=round(avg_score, 1),
        critical_alerts=critical,
        high_alerts=high,
        risk_distribution=[{"level": k, "count": v} for k, v in risk_dist.items()],
        safety_trend=trend,
        recent_inspections=[
            {
                "id": str(i.id),
                "ref": i.inspection_ref,
                "site_name": i.site_name,
                "safety_score": i.safety_score,
                "risk_level": i.risk_level,
                "violation_count": len(i.violations or []),
                "created_at": i.created_at.isoformat(),
            } for i in recent
        ],
    )


@router.get("/model-info")
def model_info(current_user: User = Depends(get_current_user)):
    return {
        "vlm_provider": vlm_client.provider,
        "vlm_model": vlm_client.model if vlm_client.enabled else None,
        "vlm_configured": vlm_client.enabled,
        "vlm_has_vision": vlm_client.has_vision,
        "yolo_available": detection_service._yolo_model is not None,
        "rules": [
            {"id": "R1_HELMET_REQUIRED", "severity": "HIGH"},
            {"id": "R2_VEST_REQUIRED", "severity": "MEDIUM"},
            {"id": "R3_RESTRICTED_ZONE", "severity": "CRITICAL"},
            {"id": "R4_EQUIPMENT_PROXIMITY", "severity": "HIGH"},
            {"id": "R5_MISSING_BARRIER", "severity": "MEDIUM"},
            {"id": "R6_SITE_ORGANIZATION", "severity": "LOW"},
        ],
        "disclaimer": settings.ETHICAL_DISCLAIMER,
        "limitations": [
            "All detections are potential observations — NOT confirmed violations",
            "VLM may hallucinate objects in low-quality images",
            "YOLO is pretrained on COCO and does not natively detect helmets/vests",
            "Bounding boxes from VLM are approximate",
            "Not a substitute for on-site human safety inspection",
            "No facial recognition, no worker identification, no automated discipline",
        ],
    }
