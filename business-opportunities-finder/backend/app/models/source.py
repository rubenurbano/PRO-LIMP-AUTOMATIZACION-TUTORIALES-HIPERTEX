"""
Source model - represents data sources (Reddit, HackerNews, etc.)
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, JSON
from sqlalchemy.sql import func
from app.database import Base


class Source(Base):
    """Model for data sources."""
    
    __tablename__ = "sources"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True)
    type = Column(String(50), nullable=False)  # 'reddit', 'hn', 'producthunt', etc.
    url = Column(String(500), nullable=False)
    config = Column(JSON, nullable=True)  # Source-specific configuration
    active = Column(Boolean, default=True)
    last_scraped_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<Source(id={self.id}, name='{self.name}', type='{self.type}')>"
