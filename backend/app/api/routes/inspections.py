from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from sqlalchemy import desc
from pathlib import Path
from PIL import Image, UnidentifiedImageError
import uuid

from ...core.database import get_db
from ...core.config import settings
from ...models.inspection import Inspection
from ...models.alert import Alert
from ...models.user import User
from ...schemas.inspection import (
    InspectionListItem, InspectionDetail, Detection, Violation,
)
from ...services.detection_service import detect_objects, summarize_for_vlm
from ...services.vlm_service import analyze_scene
from ...services.rule_engine import evaluate as run_rules
from ...services.scoring_service import compute_scores, build_explanation
from ...services.visual_service import draw_overlay
from ...api.dependencies.auth import get_current_user

router = APIRouter(prefix="/inspections", tags=["inspections"])


def _run_inspection(image_path: Path, site_name: str, site_area: str | None,
                    user_id: str, db: Session) -> Inspection:
    # 1. YOLO
    yolo_detections = detect_objects(image_path)
    yolo_summary = summarize_for_vlm(yolo_detections)
    
    # 2. VLM scene analysis
    scene = analyze_scene(image_path, yolo_summary)
    
    # 3. Image size
    with Image.open(image_path) as im:
        img_w, img_h = im.size
    
    # 4. Rule engine
    violations = run_rules(scene, yolo_detections, (img_w, img_h))
    
    # 5. Scoring
    scores = compute_scores(scene, violations)
    explanation = build_explanation(scene, violations)
    
    # 6. Persist
    count = db.query(Inspection).count()
    ref = f"INSP-{1001 + count}"
    
    inspection = Inspection(
        inspection_ref=ref,
        site_name=site_name,
        site_area=site_area,
        filename=image_path.name,
        image_path=str(image_path),
        image_width=img_w,
        image_height=img_h,
        detections=yolo_detections,
        scene_analysis=scene,
        violations=violations,
        safety_score=scores["safety_score"],
        ppe_score=scores["ppe_score"],
        zone_score=scores["zone_score"],
        equipment_score=scores["equipment_score"],
        organization_score=scores["organization_score"],
        risk_level=scores["risk_level"],
        worker_count=len(scene.get("workers", [])),
        helmet_count=len(scene.get("helmets", [])),
        vest_count=len(scene.get("vests", [])),
        equipment_count=len(scene.get("equipment", [])),
        vlm_used="true" if scene.get("overall_scene") and "unavailable" not in scene.get("overall_scene", "") else "false",
        explanation=explanation,
        created_by=user_id,
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
    db.refresh(inspection)
    return inspection


@router.post("/upload", response_model=InspectionDetail)
async def upload_inspection(
    file: UploadFile = File(...),
    site_name: str = Form("Site A"),
    site_area: str = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    suffix = Path(file.filename or "").suffix.lower()
    if suffix not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail=f"Unsupported file type: {suffix}")
    
    contents = await file.read()
    if not contents:
        raise HTTPException(status_code=400, detail="Empty image upload")
    if len(contents) > settings.MAX_FILE_SIZE_MB * 1024 * 1024:
        raise HTTPException(status_code=413, detail=f"File exceeds {settings.MAX_FILE_SIZE_MB}MB")
    
    upload_dir = Path(settings.UPLOAD_DIR)
    upload_dir.mkdir(parents=True, exist_ok=True)
    file_id = str(uuid.uuid4())
    save_path = upload_dir / f"{file_id}{suffix}"
    save_path.write_bytes(contents)
    try:
        with Image.open(save_path) as im:
            im.verify()
        with Image.open(save_path) as im:
            if im.width > settings.MAX_IMAGE_DIM or im.height > settings.MAX_IMAGE_DIM:
                im.thumbnail((settings.MAX_IMAGE_DIM, settings.MAX_IMAGE_DIM), Image.Resampling.LANCZOS)
                if suffix in {".jpg", ".jpeg"}:
                    im.convert("RGB").save(save_path, "JPEG", quality=88, optimize=True)
                elif suffix == ".webp":
                    im.convert("RGB").save(save_path, "WEBP", quality=88, method=6)
                else:
                    im.save(save_path, "PNG", optimize=True)
    except (UnidentifiedImageError, OSError) as e:
        save_path.unlink(missing_ok=True)
        raise HTTPException(status_code=400, detail="Uploaded file is not a valid image") from e
    
    try:
        inspection = _run_inspection(save_path, site_name, site_area, current_user.id, db)
    except Exception as e:
        save_path.unlink(missing_ok=True)
        raise HTTPException(status_code=400, detail=f"Processing failed: {e}")
    
    return _to_detail(db, inspection)


@router.get("/", response_model=list[InspectionListItem])
def list_inspections(
    limit: int = 50,

    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    limit = max(1, min(limit, 100))
    rows = db.query(Inspection).filter(
        Inspection.created_by == current_user.id
    ).order_by(desc(Inspection.created_at)).limit(limit).all()
    
    return [
        InspectionListItem(
            id=str(r.id),
            inspection_ref=r.inspection_ref,
            site_name=r.site_name,
            safety_score=r.safety_score,
            risk_level=r.risk_level,
            worker_count=r.worker_count,
            violation_count=len(r.violations or []),
            filename=r.filename,
            image_url=f"/uploads/{Path(r.image_path).name}" if r.image_path else None,
            created_at=r.created_at.isoformat(),
        ) for r in rows
    ]


@router.get("/{inspection_id}", response_model=InspectionDetail)
def get_inspection(
    inspection_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    insp = db.query(Inspection).filter(
        Inspection.id == inspection_id,
        Inspection.created_by == current_user.id,
    ).first()
    if not insp:
        raise HTTPException(status_code=404, detail="Inspection not found")
    return _to_detail(db, insp)


@router.get("/{inspection_id}/overlay")
def get_overlay(
    inspection_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    insp = db.query(Inspection).filter(
        Inspection.id == inspection_id, Inspection.created_by == current_user.id
    ).first()
    if not insp or not insp.image_path:
        raise HTTPException(status_code=404, detail="Inspection or image not found")
    overlay = draw_overlay(Path(insp.image_path), insp.detections or [], insp.scene_analysis or {})
    return {"overlay": overlay}


def _to_detail(db: Session, insp: Inspection) -> InspectionDetail:
    detections = [Detection(**d) for d in (insp.detections or [])]
    violations = [Violation(**v) for v in (insp.violations or [])]
    
    return InspectionDetail(
        id=str(insp.id),
        inspection_ref=insp.inspection_ref,
        site_name=insp.site_name,
        site_area=insp.site_area,
        filename=insp.filename,
        image_url=f"/uploads/{Path(insp.image_path).name}" if insp.image_path else None,
        image_width=insp.image_width,
        image_height=insp.image_height,
        detections=detections,
        violations=violations,
        scene_analysis=insp.scene_analysis,
        safety_score=insp.safety_score,
        ppe_score=insp.ppe_score,
        zone_score=insp.zone_score,
        equipment_score=insp.equipment_score,
        organization_score=insp.organization_score,
        risk_level=insp.risk_level,
        worker_count=insp.worker_count,
        helmet_count=insp.helmet_count,
        vest_count=insp.vest_count,
        equipment_count=insp.equipment_count,
        vlm_used=insp.vlm_used,
        explanation=insp.explanation,
        disclaimer=settings.ETHICAL_DISCLAIMER,
        created_at=insp.created_at.isoformat(),
    )
