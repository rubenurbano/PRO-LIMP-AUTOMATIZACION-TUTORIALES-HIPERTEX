"""
Pydantic schemas for API request/response models.
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class OpportunityBase(BaseModel):
    """Base opportunity schema."""
    title: str
    problem_description: str
    sector: Optional[str] = None
    solution_type: Optional[str] = None
    score_total: Optional[float] = None
    tags: Optional[List[str]] = None
    status: str = "new"


class OpportunityResponse(OpportunityBase):
    """Opportunity response schema."""
    id: int
    public_id: str
    proposed_app: Optional[Dict[str, Any]] = None
    ideal_users: Optional[Dict[str, Any]] = None
    economic_benefit: Optional[Dict[str, Any]] = None
    score_breakdown: Optional[Dict[str, Any]] = None
    user_notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class OpportunityUpdate(BaseModel):
    """Schema for updating an opportunity."""
    status: Optional[str] = None
    user_notes: Optional[str] = None


class OpportunityListResponse(BaseModel):
    """Response for list of opportunities."""
    total: int
    skip: int
    limit: int
    opportunities: List[OpportunityResponse]


class DailyReportResponse(BaseModel):
    """Daily report response schema."""
    id: int
    report_date: str
    top_opportunities: List[int]
    sources_consulted: Optional[int] = None
    total_analyzed: Optional[int] = None
    execution_time_minutes: Optional[float] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class AnalyticsResponse(BaseModel):
    """Analytics response schema."""
    total_opportunities: int
    avg_score: float
    top_sectors: List[Dict[str, Any]]
    opportunities_by_status: Dict[str, int]
    recent_trends: List[Dict[str, Any]]
