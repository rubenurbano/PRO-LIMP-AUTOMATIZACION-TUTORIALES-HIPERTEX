"""
Opportunity model - represents processed and scored business opportunities
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Numeric, JSON, ARRAY, Table, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import uuid


# Association table for many-to-many relationship between opportunities and raw opportunities
opportunity_sources = Table(
    'opportunity_sources',
    Base.metadata,
    Column('opportunity_id', Integer, ForeignKey('opportunities.id'), primary_key=True),
    Column('raw_opportunity_id', Integer, ForeignKey('raw_opportunities.id'), primary_key=True)
)


class RawOpportunity(Base):
    """Model for raw opportunities before processing."""
    
    __tablename__ = "raw_opportunities"
    
    id = Column(Integer, primary_key=True, index=True)
    source_id = Column(Integer, ForeignKey('sources.id'), nullable=False)
    external_id = Column(String(255), nullable=False)  # ID in the source platform
    title = Column(Text, nullable=True)
    description = Column(Text, nullable=True)
    url = Column(Text, nullable=True)
    extra_data = Column(JSON, nullable=True)  # upvotes, comments, etc.
    detected_at = Column(DateTime(timezone=True), server_default=func.now())
    processed = Column(Boolean, default=False)
    
    def __repr__(self):
        return f"<RawOpportunity(id={self.id}, source_id={self.source_id}, external_id='{self.external_id}')>"


class Opportunity(Base):
    """Model for processed and scored business opportunities."""
    
    __tablename__ = "opportunities"
    
    id = Column(Integer, primary_key=True, index=True)
    public_id = Column(String(50), unique=True, nullable=False, index=True)  # e.g., 'opp_20251201_001'
    title = Column(String(255), nullable=False)
    problem_description = Column(Text, nullable=False)
    sector = Column(String(100), nullable=True, index=True)
    solution_type = Column(String(100), nullable=True)
    
    # JSON fields
    proposed_app = Column(JSON, nullable=True)  # App proposal details
    ideal_users = Column(JSON, nullable=True)
    economic_benefit = Column(JSON, nullable=True)
    score_breakdown = Column(JSON, nullable=True)  # Individual scores
    
    # Scoring
    score_total = Column(Numeric(4, 2), nullable=True, index=True)
    
    # Tags
    tags = Column(ARRAY(String), nullable=True)
    
    # Status and notes
    status = Column(String(50), default='new', index=True)  # 'new', 'selected', 'discarded', 'in_progress'
    user_notes = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    raw_opportunities = relationship("RawOpportunity", secondary=opportunity_sources, backref="opportunities")
    
    def __repr__(self):
        return f"<Opportunity(id={self.id}, public_id='{self.public_id}', title='{self.title[:30]}...')>"
    
    @classmethod
    def generate_public_id(cls, date_str: str, sequence: int) -> str:
        """Generate a public ID like 'opp_20251201_001'."""
        return f"opp_{date_str}_{sequence:03d}"
