from sqlalchemy import Column, String, Float, DateTime, ForeignKey, Integer, Text, Date
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from ..core.database import Base
import uuid

class Inspection(Base):
    __tablename__ = "inspections"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    inspection_ref = Column(String(20), unique=True, nullable=False, index=True)
    site_name = Column(String(200), nullable=False, default="Site A")
    site_area = Column(String(200), nullable=True)
    
    filename = Column(String(255), nullable=True)
    image_path = Column(String(500), nullable=True)
    image_width = Column(Integer, nullable=True)
    image_height = Column(Integer, nullable=True)
    
    detections = Column(JSONB, nullable=False, default=list)  # [{label, bbox:[x,y,w,h], confidence, source}]
    scene_analysis = Column(JSONB, nullable=True)  # VLM JSON response
    violations = Column(JSONB, nullable=False, default=list)  # [{rule_id, severity, evidence, confidence}]
    
    safety_score = Column(Float, nullable=False, default=100.0)
    ppe_score = Column(Float, nullable=False, default=100.0)
    zone_score = Column(Float, nullable=False, default=100.0)
    equipment_score = Column(Float, nullable=False, default=100.0)
    organization_score = Column(Float, nullable=False, default=100.0)
    risk_level = Column(String(20), nullable=False, default="LOW")  # LOW | MEDIUM | HIGH | CRITICAL
    
    worker_count = Column(Integer, default=0)
    helmet_count = Column(Integer, default=0)
    vest_count = Column(Integer, default=0)
    equipment_count = Column(Integer, default=0)
    
    vlm_used = Column(String(20), nullable=False, default="false")
    explanation = Column(Text, nullable=True)
    
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, server_default=func.now(), index=True)
