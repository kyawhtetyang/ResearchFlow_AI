from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db import get_db
from app.models.report import Report
from app.models.source import Source
from app.schemas import ReportResponse, SourceResponse

router = APIRouter()


@router.get("/{job_id}", response_model=ReportResponse)
def get_report(job_id: int, db: Session = Depends(get_db)):
    report = db.query(Report).filter(Report.job_id == job_id).order_by(Report.id.desc()).first()
    if report is None:
        raise HTTPException(status_code=404, detail="report not found")
    return report


@router.get("/{job_id}/sources", response_model=list[SourceResponse])
def get_sources(job_id: int, db: Session = Depends(get_db)):
    return db.query(Source).filter(Source.job_id == job_id).order_by(Source.quality_score.desc()).all()
