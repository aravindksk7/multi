"""Audio Comparison Model."""
from datetime import datetime
from enum import Enum as PyEnum
from sqlalchemy import Column, Integer, String, Text, DateTime, Enum, JSON, Float, Index

from app.database import Base


class AudioComparisonStatus(str, PyEnum):
    """Audio comparison status enumeration."""
    QUEUED = "QUEUED"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class AudioComparison(Base):
    """Model for audio file comparisons."""
    
    __tablename__ = "audio_comparisons"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Metadata
    test_name = Column(String(255), nullable=True, index=True)
    description = Column(Text, nullable=True)
    
    # File Information
    baseline_filename = Column(String(500), nullable=False)
    current_filename = Column(String(500), nullable=False)
    baseline_file_path = Column(Text, nullable=True)  # Server-side path
    current_file_path = Column(Text, nullable=True)   # Server-side path
    
    # Audio Properties
    baseline_duration = Column(Float, nullable=True)
    current_duration = Column(Float, nullable=True)
    baseline_sample_rate = Column(Integer, nullable=True)
    current_sample_rate = Column(Integer, nullable=True)
    baseline_channels = Column(Integer, nullable=True)
    current_channels = Column(Integer, nullable=True)
    baseline_format = Column(String(50), nullable=True)
    current_format = Column(String(50), nullable=True)
    
    # Comparison Results
    status = Column(
        Enum(AudioComparisonStatus),
        default=AudioComparisonStatus.QUEUED,
        nullable=False,
        index=True
    )
    similarity_score = Column(Float, nullable=True)  # 0-100%
    duration_match = Column(String(20), nullable=True)  # EXACT, CLOSE, DIFFERENT
    format_match = Column(String(20), nullable=True)
    sample_rate_match = Column(String(20), nullable=True)
    channels_match = Column(String(20), nullable=True)
    
    # Detailed Results
    summary = Column(JSON, nullable=True)
    differences = Column(JSON, nullable=True)
    error_message = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    
    # Indexes for common queries
    __table_args__ = (
        Index('idx_audio_status_created', 'status', 'created_at'),
        Index('idx_audio_test_name', 'test_name'),
    )
    
    def __repr__(self):
        return f"<AudioComparison(id={self.id}, status={self.status}, test_name={self.test_name})>"
