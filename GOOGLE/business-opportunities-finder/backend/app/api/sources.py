"""
API routes for sources management.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models import Source

router = APIRouter()


@router.get("/sources")
async def list_sources(db: Session = Depends(get_db)):
    """List all data sources."""
    sources = db.query(Source).all()
    
    return {
        "sources": [
            {
                "id": s.id,
                "name": s.name,
                "type": s.type,
                "url": s.url,
                "active": s.active,
                "last_scraped_at": s.last_scraped_at.isoformat() if s.last_scraped_at else None
            }
            for s in sources
        ]
    }
