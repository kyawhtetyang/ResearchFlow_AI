from datetime import datetime
from sqlalchemy import Column, Integer, Text, DateTime, ForeignKey
from app.db import Base

class Report(Base):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("research_jobs.id"))
    markdown = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
