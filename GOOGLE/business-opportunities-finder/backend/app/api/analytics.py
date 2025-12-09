"""
API routes for analytics.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Dict, Any

from app.database import get_db
from app.models import Opportunity
from app.api.schemas import AnalyticsResponse

router = APIRouter()


@router.get("/analytics", response_model=AnalyticsResponse)
async def get_analytics(db: Session = Depends(get_db)):
    """Get analytics and statistics about opportunities."""
    
    # Total opportunities
    total = db.query(Opportunity).count()
    
    # Average score
    avg_score_result = db.query(func.avg(Opportunity.score_total)).scalar()
    avg_score = float(avg_score_result) if avg_score_result else 0.0
    
    # Top sectors
    top_sectors_query = db.query(
        Opportunity.sector,
        func.count(Opportunity.id).label('count'),
        func.avg(Opportunity.score_total).label('avg_score')
    ).filter(
        Opportunity.sector.isnot(None)
    ).group_by(
        Opportunity.sector
    ).order_by(
        func.count(Opportunity.id).desc()
    ).limit(10).all()
    
    top_sectors = [
        {
            "sector": sector,
            "count": count,
            "avg_score": round(float(avg_score_val) if avg_score_val else 0.0, 2)
        }
        for sector, count, avg_score_val in top_sectors_query
    ]
    
    # Opportunities by status
    status_query = db.query(
        Opportunity.status,
        func.count(Opportunity.id).label('count')
    ).group_by(Opportunity.status).all()
    
    opportunities_by_status = {status: count for status, count in status_query}
    
    # Recent trends (last 7 days)
    # For MVP, we'll just return empty list
    # In production, you'd aggregate by day
    recent_trends = []
    
    return {
        "total_opportunities": total,
        "avg_score": round(avg_score, 2),
        "top_sectors": top_sectors,
        "opportunities_by_status": opportunities_by_status,
        "recent_trends": recent_trends
    }
