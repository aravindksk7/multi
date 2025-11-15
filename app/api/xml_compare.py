"""API routes for XML comparison jobs."""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import (
    XMLCompareRequest, JobResponse, JobDetailResponse, 
    JobListResponse, JobQueryParams
)
from app.services.job_service import JobService
from app.models import JobStatus

router = APIRouter(prefix="/api/xml-compare", tags=["XML Compare"])


@router.post("/jobs", response_model=JobDetailResponse, status_code=201)
def create_comparison_job(
    request: XMLCompareRequest,
    db: Session = Depends(get_db)
):
    """
    Create and execute a new XML comparison job.
    
    Args:
        request: Job creation request with XML content and metadata
        db: Database session
        
    Returns:
        Created job with comparison results
    """
    service = JobService(db)
    job = service.create_and_run_job(request)
    
    return JobDetailResponse(
        id=job.id,
        status=job.status,
        suite_name=job.suite_name,
        environment=job.environment,
        run_id=job.run_id,
        summary=job.summary,
        differences=job.differences,
        created_at=job.created_at,
        started_at=job.started_at,
        completed_at=job.completed_at,
        error_message=job.error_message
    )


@router.get("/jobs/{job_id}", response_model=JobDetailResponse)
def get_job(
    job_id: int,
    db: Session = Depends(get_db)
):
    """
    Get detailed information about a specific job.
    
    Args:
        job_id: Job identifier
        db: Database session
        
    Returns:
        Job details including all differences
        
    Raises:
        HTTPException: If job not found
    """
    service = JobService(db)
    job = service.get_job(job_id)
    
    if not job:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
    
    return JobDetailResponse(
        id=job.id,
        status=job.status,
        suite_name=job.suite_name,
        environment=job.environment,
        run_id=job.run_id,
        summary=job.summary,
        differences=job.differences,
        created_at=job.created_at,
        started_at=job.started_at,
        completed_at=job.completed_at,
        error_message=job.error_message
    )


@router.get("/jobs", response_model=JobListResponse)
def list_jobs(
    status: Optional[JobStatus] = Query(None, description="Filter by status"),
    suite_name: Optional[str] = Query(None, description="Filter by suite name"),
    environment: Optional[str] = Query(None, description="Filter by environment"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db)
):
    """
    List comparison jobs with filtering and pagination.
    
    Args:
        status: Filter by job status
        suite_name: Filter by suite name
        environment: Filter by environment
        page: Page number (1-indexed)
        page_size: Number of items per page
        db: Database session
        
    Returns:
        Paginated list of jobs
    """
    params = JobQueryParams(
        status=status,
        suite_name=suite_name,
        environment=environment,
        page=page,
        page_size=page_size
    )
    
    service = JobService(db)
    jobs, total = service.list_jobs(params)
    
    return JobListResponse(
        total=total,
        page=page,
        page_size=page_size,
        jobs=[JobResponse(
            id=job.id,
            status=job.status,
            suite_name=job.suite_name,
            environment=job.environment,
            run_id=job.run_id,
            summary=job.summary,
            created_at=job.created_at,
            started_at=job.started_at,
            completed_at=job.completed_at,
            error_message=job.error_message
        ) for job in jobs]
    )


@router.delete("/jobs/{job_id}", status_code=204)
def delete_job(
    job_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete a comparison job.
    
    Args:
        job_id: Job identifier
        db: Database session
        
    Raises:
        HTTPException: If job not found
    """
    service = JobService(db)
    deleted = service.delete_job(job_id)
    
    if not deleted:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
