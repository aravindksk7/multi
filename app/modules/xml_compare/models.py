"""XML Comparison Job Model."""
from datetime import datetime
from enum import Enum as PyEnum
from sqlalchemy import (
    Column, Integer, String, Text, DateTime, Enum, 
    JSON, Index
)

from app.database import Base


class JobStatus(str, PyEnum):
    """Job status enumeration."""
    QUEUED = "QUEUED"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class DiffType(str, PyEnum):
    """Difference type enumeration."""
    ADDED = "ADDED"
    REMOVED = "REMOVED"
    CHANGED = "CHANGED"


class ComparisonJob(Base):
    """Model for XML comparison jobs."""
    
    __tablename__ = "comparison_jobs"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Metadata
    suite_name = Column(String(255), nullable=True, index=True)
    environment = Column(String(100), nullable=True, index=True)
    run_id = Column(String(255), nullable=True, index=True)
    
    # Status
    status = Column(
        Enum(JobStatus), 
        default=JobStatus.QUEUED, 
        nullable=False,
        index=True
    )
    
    # XML Content
    baseline_xml = Column(Text, nullable=False)
    current_xml = Column(Text, nullable=False)
    
    # Results
    summary = Column(JSON, nullable=True)
    differences = Column(JSON, nullable=True)
    error_message = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    
    # Indexes for common queries
    __table_args__ = (
        Index('idx_job_status_created', 'status', 'created_at'),
        Index('idx_job_suite_env', 'suite_name', 'environment'),
    )
    
    def __repr__(self):
        return f"<ComparisonJob(id={self.id}, status={self.status}, suite_name={self.suite_name})>"
