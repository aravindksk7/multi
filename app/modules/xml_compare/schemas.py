"""Pydantic schemas for request/response validation."""
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, validator

from .models import JobStatus, DiffType


# Request Schemas
class XMLCompareRequest(BaseModel):
    """Request schema for creating XML comparison job."""
    
    baseline_xml: str = Field(..., description="Baseline XML content")
    current_xml: str = Field(..., description="Current XML content")
    suite_name: Optional[str] = Field(None, max_length=255, description="Test suite name")
    environment: Optional[str] = Field(None, max_length=100, description="Environment (e.g., dev, staging, prod)")
    run_id: Optional[str] = Field(None, max_length=255, description="Run identifier")
    
    @validator('baseline_xml', 'current_xml')
    def validate_xml_not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError("XML content cannot be empty")
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "baseline_xml": "<testsuite><testcase name='TC1' status='pass'/></testsuite>",
                "current_xml": "<testsuite><testcase name='TC1' status='fail'/></testsuite>",
                "suite_name": "Regression Suite",
                "environment": "staging",
                "run_id": "run-123"
            }
        }


# Response Schemas
class DifferenceDetail(BaseModel):
    """Schema for individual difference."""
    
    type: DiffType
    path: str
    baseline_value: Optional[str] = None
    current_value: Optional[str] = None
    description: Optional[str] = None


class ComparisonSummary(BaseModel):
    """Schema for comparison summary."""
    
    added: int = 0
    removed: int = 0
    changed: int = 0
    status: str = "PASSED"  # PASSED or FAILED
    total_differences: int = 0


class JobResponse(BaseModel):
    """Response schema for comparison job."""
    
    id: int
    status: JobStatus
    suite_name: Optional[str]
    environment: Optional[str]
    run_id: Optional[str]
    summary: Optional[ComparisonSummary]
    created_at: datetime
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    error_message: Optional[str]
    
    class Config:
        from_attributes = True


class JobDetailResponse(JobResponse):
    """Detailed response schema including differences."""
    
    differences: Optional[List[Dict[str, Any]]] = None


class JobListResponse(BaseModel):
    """Response schema for paginated job list."""
    
    total: int
    page: int
    page_size: int
    jobs: List[JobResponse]


# Query Parameters
class JobQueryParams(BaseModel):
    """Query parameters for filtering jobs."""
    
    status: Optional[JobStatus] = None
    suite_name: Optional[str] = None
    environment: Optional[str] = None
    from_date: Optional[datetime] = None
    to_date: Optional[datetime] = None
    page: int = Field(1, ge=1)
    page_size: int = Field(20, ge=1, le=100)
