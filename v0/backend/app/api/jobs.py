from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.db import get_db
from app.schemas import ResearchJobResponse, ResearchStepResponse
from app.models.research_job import ResearchJob
from app.models.research_step import ResearchStep

router = APIRouter()

@router.get("/{job_id}", response_model=ResearchJobResponse)
def get_job(job_id: int, db: Session = Depends(get_db)):
    job = db.query(ResearchJob).filter(ResearchJob.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job

@router.get("/{job_id}/steps", response_model=List[ResearchStepResponse])
def get_job_steps(job_id: int, db: Session = Depends(get_db)):
    steps = db.query(ResearchStep).filter(ResearchStep.job_id == job_id).all()
    return steps
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db import get_db
from app.models.research_job import ResearchJob
from app.schemas import ResearchJobResponse

router = APIRouter()


@router.get("/", response_model=list[ResearchJobResponse])
def list_jobs(db: Session = Depends(get_db)):
    return db.query(ResearchJob).order_by(ResearchJob.created_at.desc()).limit(25).all()


@router.get("/{job_id}", response_model=ResearchJobResponse)
def get_job(job_id: int, db: Session = Depends(get_db)):
    job = db.query(ResearchJob).filter(ResearchJob.id == job_id).first()
    if job is None:
        raise HTTPException(status_code=404, detail="job not found")
    return job
