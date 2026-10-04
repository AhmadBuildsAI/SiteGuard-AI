from sqlalchemy import Column, String, Float, DateTime, ForeignKey, Text, Boolean, Integer
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from ..core.database import Base
import uuid

class Alert(Base):
    __tablename__ = "alerts"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    inspection_id = Column(UUID(as_uuid=True), ForeignKey("inspections.id"), nullable=False, index=True)
    rule_id = Column(String(50), nullable=False)
    severity = Column(String(20), nullable=False, index=True)  # CRITICAL | HIGH | MEDIUM | LOW
    title = Column(String(200), nullable=False)
    message = Column(Text, nullable=False)
    vlm_observation = Column(Text, nullable=True)
    evidence = Column(JSONB, nullable=True)
    confidence = Column(Float, nullable=False, default=0.5)
    requires_human_review = Column(Boolean, default=True)
    is_acknowledged = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now(), index=True)
