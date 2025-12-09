"""
Scoring configuration model - stores different versions of scoring weights
"""
from sqlalchemy import Column, Integer, String, JSON, Boolean, DateTime
from sqlalchemy.sql import func
from app.database import Base


class ScoringConfig(Base):
    """Model for scoring configuration versions."""
    
    __tablename__ = "scoring_config"
    
    id = Column(Integer, primary_key=True, index=True)
    version = Column(String(20), nullable=False, unique=True)
    weights = Column(JSON, nullable=False)  # Dictionary of criterion weights
    active = Column(Boolean, default=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<ScoringConfig(id={self.id}, version='{self.version}', active={self.active})>"
