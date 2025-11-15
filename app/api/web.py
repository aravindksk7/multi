"""Web routes for HTML UI."""
from typing import Optional
from fastapi import APIRouter, Depends, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import XMLCompareRequest, JobQueryParams
from app.services.job_service import JobService
from app.models import JobStatus

router = APIRouter(tags=["Web UI"])
templates = Jinja2Templates(directory="app/templates")


@router.get("/", response_class=HTMLResponse)
def index(request: Request):
    """Home page."""
    return templates.TemplateResponse("index.html", {"request": request})


@router.get("/compare/new", response_class=HTMLResponse)
def new_comparison(request: Request):
    """New comparison form page."""
    return templates.TemplateResponse("new_comparison.html", {"request": request})


@router.post("/compare")
async def create_comparison(
    request: Request,
    baseline_xml: str = Form(...),
    current_xml: str = Form(...),
    suite_name: Optional[str] = Form(None),
    environment: Optional[str] = Form(None),
    run_id: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """
    Handle form submission for new comparison.
    
    Redirects to job detail page on success.
    """
    try:
        compare_request = XMLCompareRequest(
            baseline_xml=baseline_xml,
            current_xml=current_xml,
            suite_name=suite_name,
            environment=environment,
            run_id=run_id
        )
        
        service = JobService(db)
        job = service.create_and_run_job(compare_request)
        
        return RedirectResponse(url=f"/jobs/{job.id}", status_code=303)
    
    except Exception as e:
        return templates.TemplateResponse(
            "new_comparison.html",
            {"request": request, "error": str(e)},
            status_code=400
        )


@router.get("/jobs", response_class=HTMLResponse)
def list_jobs(
    request: Request,
    status: Optional[str] = None,
    suite_name: Optional[str] = None,
    environment: Optional[str] = None,
    page: int = 1,
    db: Session = Depends(get_db)
):
    """Jobs list page with filtering."""
    # Convert status string to enum if provided
    status_enum = None
    if status:
        try:
            status_enum = JobStatus(status)
        except ValueError:
            pass
    
    params = JobQueryParams(
        status=status_enum,
        suite_name=suite_name,
        environment=environment,
        page=page,
        page_size=20
    )
    
    service = JobService(db)
    jobs, total = service.list_jobs(params)
    
    # Calculate pagination info
    total_pages = (total + params.page_size - 1) // params.page_size
    
    return templates.TemplateResponse(
        "jobs_list.html",
        {
            "request": request,
            "jobs": jobs,
            "total": total,
            "page": page,
            "total_pages": total_pages,
            "status": status,
            "suite_name": suite_name,
            "environment": environment
        }
    )


@router.get("/jobs/{job_id}", response_class=HTMLResponse)
def job_detail(
    request: Request,
    job_id: int,
    db: Session = Depends(get_db)
):
    """Job detail page."""
    service = JobService(db)
    job = service.get_job(job_id)
    
    if not job:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
    
    return templates.TemplateResponse(
        "job_detail.html",
        {
            "request": request,
            "job": job
        }
    )
