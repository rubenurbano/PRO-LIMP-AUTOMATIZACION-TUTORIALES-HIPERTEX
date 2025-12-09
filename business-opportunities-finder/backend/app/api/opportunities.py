"""
API routes for opportunities.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.database import get_db
from app.models import Opportunity
from app.api.schemas import OpportunityResponse, OpportunityUpdate, OpportunityListResponse

router = APIRouter()


@router.get("/opportunities", response_model=OpportunityListResponse)
async def list_opportunities(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    sector: Optional[str] = None,
    status: Optional[str] = None,
    min_score: Optional[float] = Query(None, ge=0, le=10),
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    List opportunities with filtering and pagination.
    
    Query parameters:
    - skip: Number of records to skip (pagination)
    - limit: Maximum number of records to return
    - sector: Filter by sector
    - status: Filter by status (new, selected, discarded, in_progress)
    - min_score: Minimum score filter
    - search: Search in title and description
    """
    query = db.query(Opportunity)
    
    # Apply filters
    if sector:
        query = query.filter(Opportunity.sector.ilike(f"%{sector}%"))
    
    if status:
        query = query.filter(Opportunity.status == status)
    
    if min_score is not None:
        query = query.filter(Opportunity.score_total >= min_score)
    
    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            (Opportunity.title.ilike(search_pattern)) |
            (Opportunity.problem_description.ilike(search_pattern))
        )
    
    # Get total count
    total = query.count()
    
    # Apply pagination and ordering
    opportunities = query.order_by(
        Opportunity.score_total.desc(),
        Opportunity.created_at.desc()
    ).offset(skip).limit(limit).all()
    
    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "opportunities": opportunities
    }


@router.get("/opportunities/{opportunity_id}", response_model=OpportunityResponse)
async def get_opportunity(
    opportunity_id: str,
    db: Session = Depends(get_db)
):
    """Get a specific opportunity by public ID."""
    opportunity = db.query(Opportunity).filter(
        Opportunity.public_id == opportunity_id
    ).first()
    
    if not opportunity:
        raise HTTPException(status_code=404, detail="Opportunity not found")
    
    return opportunity


@router.patch("/opportunities/{opportunity_id}", response_model=OpportunityResponse)
async def update_opportunity(
    opportunity_id: str,
    update_data: OpportunityUpdate,
    db: Session = Depends(get_db)
):
    """
    Update opportunity status and notes.
    
    Allowed updates:
    - status: Change to 'new', 'selected', 'discarded', or 'in_progress'
    - user_notes: Add or update notes
    """
    opportunity = db.query(Opportunity).filter(
        Opportunity.public_id == opportunity_id
    ).first()
    
    if not opportunity:
        raise HTTPException(status_code=404, detail="Opportunity not found")
    
    # Update fields
    if update_data.status is not None:
        if update_data.status not in ["new", "selected", "discarded", "in_progress"]:
            raise HTTPException(status_code=400, detail="Invalid status value")
        opportunity.status = update_data.status
    
    if update_data.user_notes is not None:
        opportunity.user_notes = update_data.user_notes
    
    opportunity.updated_at = datetime.now()
    
    db.commit()
    db.refresh(opportunity)
    
    return opportunity
