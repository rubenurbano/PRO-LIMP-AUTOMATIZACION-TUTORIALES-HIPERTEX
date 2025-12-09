"""
API routes for daily reports.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import date, datetime
from typing import Optional

from app.database import get_db
from app.models import DailyReport
from app.api.schemas import DailyReportResponse

router = APIRouter()


@router.get("/reports/{report_date}", response_model=DailyReportResponse)
async def get_daily_report(
    report_date: str,
    db: Session = Depends(get_db)
):
    """
    Get daily report by date.
    
    Args:
        report_date: Date in format YYYY-MM-DD
    """
    try:
        parsed_date = datetime.strptime(report_date, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
    
    report = db.query(DailyReport).filter(
        DailyReport.report_date == parsed_date
    ).first()
    
    if not report:
        raise HTTPException(status_code=404, detail="Report not found for this date")
    
    return report


@router.get("/reports/latest", response_model=DailyReportResponse)
async def get_latest_report(db: Session = Depends(get_db)):
    """Get the most recent daily report."""
    report = db.query(DailyReport).order_by(
        DailyReport.report_date.desc()
    ).first()
    
    if not report:
        raise HTTPException(status_code=404, detail="No reports found")
    
    return report
