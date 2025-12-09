"""
Report model - represents daily opportunity reports
"""
from sqlalchemy import Column, Integer, Date, JSON, Text, DateTime, Numeric, ARRAY
from sqlalchemy.sql import func
from app.database import Base


class DailyReport(Base):
    """Model for daily opportunity reports."""
    
    __tablename__ = "daily_reports"
    
    id = Column(Integer, primary_key=True, index=True)
    report_date = Column(Date, unique=True, nullable=False, index=True)
    
    # Top opportunities
    top_opportunities = Column(ARRAY(Integer), nullable=False)  # Array of opportunity IDs
    
    # Report data
    report_json = Column(JSON, nullable=True)  # Full structured report
    report_html = Column(Text, nullable=True)  # HTML email version
    
    # Metadata
    sources_consulted = Column(Integer, nullable=True)
    total_analyzed = Column(Integer, nullable=True)
    execution_time_minutes = Column(Numeric(5, 2), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<DailyReport(id={self.id}, date={self.report_date}, top_count={len(self.top_opportunities)})>"
