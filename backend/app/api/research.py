from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db import get_db
from app.agents.orchestrator import run_research_job
from app.schemas import ResearchJobCreate, ResearchJobDetail, ResearchJobResponse, ResearchJobSummary
from app.models.report import Report
from app.models.research_job import ResearchJob
from app.models.research_step import ResearchStep
from app.models.source import Source

router = APIRouter()

@router.post("/", response_model=ResearchJobResponse)
def create_research_job(job_in: ResearchJobCreate, db: Session = Depends(get_db)):
    job = ResearchJob(query=job_in.query, status="pending")
    db.add(job)
    db.commit()
    db.refresh(job)

    if job_in.run_now:
        job = run_research_job(db, job)

    return job

@router.get("/{job_id}", response_model=ResearchJobDetail)
def get_research_job(job_id: int, db: Session = Depends(get_db)):
    job = db.query(ResearchJob).filter(ResearchJob.id == job_id).first()
    if job is None:
        raise HTTPException(status_code=404, detail="research job not found")

    steps = (
        db.query(ResearchStep)
        .filter(ResearchStep.job_id == job_id)
        .order_by(ResearchStep.step_order.asc(), ResearchStep.id.asc())
        .all()
    )
    sources = db.query(Source).filter(Source.job_id == job_id).order_by(Source.quality_score.desc()).all()
    report = db.query(Report).filter(Report.job_id == job_id).order_by(Report.id.desc()).first()

    return {"job": job, "steps": steps, "sources": sources, "report": report}

@router.get("/{job_id}/summary", response_model=ResearchJobSummary)
def get_research_summary(job_id: int, db: Session = Depends(get_db)):
    job = db.query(ResearchJob).filter(ResearchJob.id == job_id).first()
    if job is None:
        raise HTTPException(status_code=404, detail="research job not found")

    step_count = db.query(ResearchStep).filter(ResearchStep.job_id == job_id).count()
    sources = db.query(Source).filter(Source.job_id == job_id).all()
    report = db.query(Report).filter(Report.job_id == job_id).first()
    source_count = len(sources)
    avg_quality = sum(float(s.quality_score or 0) for s in sources) / source_count if source_count else 0.0
    readiness = 0.0
    readiness += 0.25 if job.status == "completed" else 0
    readiness += min(step_count / 4, 1.0) * 0.25
    readiness += min(source_count / 5, 1.0) * 0.25
    readiness += 0.25 if report is not None else 0

    return ResearchJobSummary(
        job_id=job.id,
        status=job.status,
        step_count=step_count,
        source_count=source_count,
        average_source_quality=round(avg_quality, 3),
        has_report=report is not None,
        readiness_score=round(readiness, 3),
    )
