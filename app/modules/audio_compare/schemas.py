"""Audio comparison schemas."""
from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field

from .models import AudioComparisonStatus


class AudioCompareRequest(BaseModel):
    """Request schema for audio comparison."""
    
    baseline_audio: str = Field(..., description="Base64 encoded baseline audio file or file path")
    current_audio: str = Field(..., description="Base64 encoded current audio file or file path")
    baseline_filename: str = Field(..., description="Baseline audio filename")
    current_filename: str = Field(..., description="Current audio filename")
    test_name: Optional[str] = Field(None, max_length=255, description="Test identifier")
    description: Optional[str] = Field(None, description="Comparison description")
    
    class Config:
        json_schema_extra = {
            "example": {
                "baseline_audio": "base64_encoded_audio_data...",
                "current_audio": "base64_encoded_audio_data...",
                "baseline_filename": "reference.wav",
                "current_filename": "test_output.wav",
                "test_name": "Audio Quality Test",
                "description": "Compare speech synthesis output"
            }
        }


class AudioPropertiesSchema(BaseModel):
    """Schema for audio file properties."""
    
    duration: Optional[float] = None
    sample_rate: Optional[int] = None
    channels: Optional[int] = None
    format: Optional[str] = None
    bitrate: Optional[int] = None
    codec: Optional[str] = None


class AudioComparisonSummary(BaseModel):
    """Schema for comparison summary."""
    
    overall_match: str  # MATCH, PARTIAL_MATCH, MISMATCH
    similarity_score: Optional[float] = None  # 0-100%
    duration_match: Optional[str] = None
    format_match: Optional[str] = None
    sample_rate_match: Optional[str] = None
    channels_match: Optional[str] = None
    issues_found: int = 0
    recommendations: Optional[list[str]] = None


class AudioComparisonResponse(BaseModel):
    """Response schema for audio comparison."""
    
    id: int
    status: AudioComparisonStatus
    test_name: Optional[str]
    description: Optional[str]
    
    baseline_filename: str
    current_filename: str
    
    baseline_duration: Optional[float]
    current_duration: Optional[float]
    baseline_sample_rate: Optional[int]
    current_sample_rate: Optional[int]
    baseline_channels: Optional[int]
    current_channels: Optional[int]
    baseline_format: Optional[str]
    current_format: Optional[str]
    
    similarity_score: Optional[float]
    duration_match: Optional[str]
    format_match: Optional[str]
    sample_rate_match: Optional[str]
    channels_match: Optional[str]
    
    summary: Optional[AudioComparisonSummary]
    differences: Optional[list[Dict[str, Any]]]
    error_message: Optional[str]
    
    created_at: datetime
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class AudioComparisonListResponse(BaseModel):
    """Response schema for list of audio comparisons."""
    
    items: list[AudioComparisonResponse]
    total: int
    page: int
    page_size: int
    
    class Config:
        from_attributes = True
