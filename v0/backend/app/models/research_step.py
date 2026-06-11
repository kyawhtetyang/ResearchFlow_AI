from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from app.db import Base

class ResearchStep(Base):
    __tablename__ = "research_steps"

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("research_jobs.id"))
    step_order = Column(Integer, default=0)
    agent_name = Column(String, index=True)
    status = Column(String, default="completed")
    input = Column(Text, nullable=True)
    output = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
