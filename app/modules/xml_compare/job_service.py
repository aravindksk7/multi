"""Job service for managing comparison jobs."""
from datetime import datetime
from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from app.models import ComparisonJob, JobStatus
from app.schemas import XMLCompareRequest, JobQueryParams
from app.services.xml_compare import compare_xml


class JobService:
    """Service for managing comparison jobs."""
    
    def __init__(self, db: Session):
        """
        Initialize job service.
        
        Args:
            db: Database session
        """
        self.db = db
    
    def create_and_run_job(self, request: XMLCompareRequest) -> ComparisonJob:
        """
        Create and execute a comparison job.
        
        Args:
            request: Job creation request
            
        Returns:
            Created job with results
        """
        # Create job record
        job = ComparisonJob(
            suite_name=request.suite_name,
            environment=request.environment,
            run_id=request.run_id,
            baseline_xml=request.baseline_xml,
            current_xml=request.current_xml,
            status=JobStatus.RUNNING,
            started_at=datetime.utcnow()
        )
        
        self.db.add(job)
        self.db.commit()
        self.db.refresh(job)
        
        # Run comparison
        try:
            result = compare_xml(request.baseline_xml, request.current_xml)
            
            job.summary = result["summary"]
            job.differences = result["differences"]
            job.status = JobStatus.COMPLETED
            job.completed_at = datetime.utcnow()
            job.error_message = None
            
        except Exception as e:
            job.status = JobStatus.FAILED
            job.completed_at = datetime.utcnow()
            job.error_message = str(e)
        
        self.db.commit()
        self.db.refresh(job)
        
        return job
    
    def get_job(self, job_id: int) -> Optional[ComparisonJob]:
        """
        Get job by ID.
        
        Args:
            job_id: Job identifier
            
        Returns:
            Job or None if not found
        """
        return self.db.query(ComparisonJob).filter(ComparisonJob.id == job_id).first()
    
    def list_jobs(self, params: JobQueryParams) -> tuple[List[ComparisonJob], int]:
        """
        List jobs with filtering and pagination.
        
        Args:
            params: Query parameters
            
        Returns:
            Tuple of (jobs list, total count)
        """
        query = self.db.query(ComparisonJob)
        
        # Apply filters
        filters = []
        
        if params.status:
            filters.append(ComparisonJob.status == params.status)
        
        if params.suite_name:
            filters.append(ComparisonJob.suite_name == params.suite_name)
        
        if params.environment:
            filters.append(ComparisonJob.environment == params.environment)
        
        if params.from_date:
            filters.append(ComparisonJob.created_at >= params.from_date)
        
        if params.to_date:
            filters.append(ComparisonJob.created_at <= params.to_date)
        
        if filters:
            query = query.filter(and_(*filters))
        
        # Get total count
        total = query.count()
        
        # Apply pagination and sorting
        jobs = (
            query
            .order_by(ComparisonJob.created_at.desc())
            .offset((params.page - 1) * params.page_size)
            .limit(params.page_size)
            .all()
        )
        
        return jobs, total
    
    def delete_job(self, job_id: int) -> bool:
        """
        Delete a job.
        
        Args:
            job_id: Job identifier
            
        Returns:
            True if deleted, False if not found
        """
        job = self.get_job(job_id)
        if job:
            self.db.delete(job)
            self.db.commit()
            return True
        return False
