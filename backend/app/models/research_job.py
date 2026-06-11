from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text
from app.db import Base

class ResearchJob(Base):
    __tablename__ = "research_jobs"

    id = Column(Integer, primary_key=True, index=True)
    query = Column(Text, nullable=False)
    status = Column(String, default="pending")  # pending, in_progress, completed, failed
    error = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
