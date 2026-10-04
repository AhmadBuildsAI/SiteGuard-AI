from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc
from ...core.database import get_db
from ...models.alert import Alert
from ...models.inspection import Inspection
from ...models.user import User
from ...schemas.inspection import AlertItem
from ...api.dependencies.auth import get_current_user

router = APIRouter(prefix="/alerts", tags=["alerts"])


def _to_item(a: Alert, insp: Inspection) -> AlertItem:
    return AlertItem(
        id=str(a.id),
        inspection_id=str(a.inspection_id),
        inspection_ref=insp.inspection_ref if insp else "—",
        rule_id=a.rule_id,
        severity=a.severity,
        title=a.title,
        message=a.message,
        vlm_observation=a.vlm_observation,
        confidence=a.confidence,
        is_acknowledged=a.is_acknowledged,
        created_at=a.created_at.isoformat(),
    )


@router.get("/", response_model=list[AlertItem])
def list_alerts(
    severity: str | None = None,
    acknowledged: bool | None = None,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    limit = max(1, min(limit, 200))
    # Only show alerts from inspections created by this user
    user_inspection_ids = [
        str(r.id) for r in db.query(Inspection).filter(Inspection.created_by == current_user.id).all()
    ]
    q = db.query(Alert).filter(Alert.inspection_id.in_(user_inspection_ids))
    if severity:
        q = q.filter(Alert.severity == severity)
    if acknowledged is not None:
        q = q.filter(Alert.is_acknowledged == acknowledged)
    rows = q.order_by(desc(Alert.created_at)).limit(limit).all()
    
    out = []
    for a in rows:
        insp = db.query(Inspection).filter(Inspection.id == a.inspection_id).first()
        out.append(_to_item(a, insp))
    return out


@router.post("/{alert_id}/acknowledge", response_model=AlertItem)
def acknowledge(
    alert_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    a = db.query(Alert).join(Inspection, Alert.inspection_id == Inspection.id).filter(
        Alert.id == alert_id, Inspection.created_by == current_user.id
    ).first()
    if not a:
        raise HTTPException(status_code=404, detail="Alert not found")
    a.is_acknowledged = True
    db.commit()
    insp = db.query(Inspection).filter(Inspection.id == a.inspection_id).first()
    return _to_item(a, insp)
