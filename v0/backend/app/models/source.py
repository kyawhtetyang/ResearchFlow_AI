from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, ForeignKey, Float, DateTime
from app.db import Base

class Source(Base):
    __tablename__ = "sources"

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("research_jobs.id"))
    title = Column(String)
    url = Column(String)
    snippet = Column(Text, nullable=True)
    content = Column(Text)
    score = Column(Float, nullable=True)
    quality_score = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
