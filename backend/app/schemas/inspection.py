from pydantic import BaseModel
from typing import List, Optional, Dict

class Detection(BaseModel):
    label: str
    bbox: List[float]  # [x, y, w, h] in original image pixels
    confidence: float
    source: str  # yolo | vlm

class Violation(BaseModel):
    rule_id: str
    severity: str
    title: str
    message: str
    evidence: Dict
    confidence: float
    vlm_observation: Optional[str] = None

class InspectionListItem(BaseModel):
    id: str
    inspection_ref: str
    site_name: str
    safety_score: float
    risk_level: str
    worker_count: int
    violation_count: int
    filename: Optional[str]
    image_url: Optional[str]
    created_at: str

class InspectionDetail(BaseModel):
    id: str
    inspection_ref: str
    site_name: str
    site_area: Optional[str]
    filename: Optional[str]
    image_url: Optional[str]
    image_width: Optional[int]
    image_height: Optional[int]
    detections: List[Detection]
    violations: List[Violation]
    scene_analysis: Optional[Dict]
    safety_score: float
    ppe_score: float
    zone_score: float
    equipment_score: float
    organization_score: float
    risk_level: str
    worker_count: int
    helmet_count: int
    vest_count: int
    equipment_count: int
    vlm_used: str
    explanation: Optional[str]
    disclaimer: str
    created_at: str

class AlertItem(BaseModel):
    id: str
    inspection_id: str
    inspection_ref: str
    rule_id: str
    severity: str
    title: str
    message: str
    vlm_observation: Optional[str]
    confidence: float
    is_acknowledged: bool
    created_at: str

class DashboardData(BaseModel):
    total_inspections: int
    total_alerts: int
    avg_safety_score: float
    critical_alerts: int
    high_alerts: int
    risk_distribution: List[dict]
    safety_trend: List[dict]
    recent_inspections: List[dict]
