"""Audio comparison API routes."""
from fastapi import APIRouter, Depends, HTTPException, Request, Form, File, UploadFile
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import Optional
import base64

from app.database import get_db
from app.modules.audio_compare import (
    AudioComparator,
    AudioCompareRequest,
    AudioComparisonResponse,
    AudioComparisonListResponse,
    AudioComparison
)

router = APIRouter(prefix="/audio", tags=["audio"])
templates = Jinja2Templates(directory="app/templates")


@router.get("/", response_class=HTMLResponse)
async def audio_home(request: Request):
    """Audio comparison home page."""
    return templates.TemplateResponse(
        "audio_home.html",
        {"request": request}
    )


@router.get("/compare", response_class=HTMLResponse)
async def audio_compare_form(request: Request):
    """Audio comparison form page."""
    return templates.TemplateResponse(
        "audio_compare_form.html",
        {"request": request}
    )


@router.post("/compare", response_model=AudioComparisonResponse)
async def compare_audio_files(
    baseline_file: UploadFile = File(...),
    current_file: UploadFile = File(...),
    test_name: str = Form(...),
    description: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """
    Compare two audio files.
    
    - **baseline_file**: Baseline audio file
    - **current_file**: Current audio file to compare
    - **test_name**: Name of the test
    - **description**: Optional description
    """
    # Read file contents
    baseline_content = await baseline_file.read()
    current_content = await current_file.read()
    
    # Encode to base64
    baseline_b64 = base64.b64encode(baseline_content).decode('utf-8')
    current_b64 = base64.b64encode(current_content).decode('utf-8')
    
    # Create request
    compare_request = AudioCompareRequest(
        baseline_audio=baseline_b64,
        current_audio=current_b64,
        baseline_filename=baseline_file.filename,
        current_filename=current_file.filename,
        test_name=test_name,
        description=description
    )
    
    # Perform comparison
    comparator = AudioComparator()
    comparison = comparator.compare_audio_files(compare_request, db)
    
    return comparison


@router.get("/api/comparisons", response_model=AudioComparisonListResponse)
async def list_audio_comparisons(
    page: int = 1,
    page_size: int = 20,
    status: Optional[str] = None,
    test_name: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    List audio comparisons with pagination.
    
    - **page**: Page number (default: 1)
    - **page_size**: Items per page (default: 20)
    - **status**: Filter by status (QUEUED, PROCESSING, COMPLETED, FAILED)
    - **test_name**: Filter by test name (partial match)
    """
    skip = (page - 1) * page_size
    
    comparator = AudioComparator()
    comparisons, total = comparator.list_comparisons(
        db=db,
        skip=skip,
        limit=page_size,
        status=status,
        test_name=test_name
    )
    
    return AudioComparisonListResponse(
        items=comparisons,
        total=total,
        page=page,
        page_size=page_size
    )


@router.get("/comparisons", response_class=HTMLResponse)
async def audio_comparisons_list(
    request: Request,
    page: int = 1,
    status: Optional[str] = None,
    test_name: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Audio comparisons list page."""
    page_size = 20
    skip = (page - 1) * page_size
    
    comparator = AudioComparator()
    comparisons, total = comparator.list_comparisons(
        db=db,
        skip=skip,
        limit=page_size,
        status=status,
        test_name=test_name
    )
    
    total_pages = (total + page_size - 1) // page_size
    
    return templates.TemplateResponse(
        "audio_comparisons_list.html",
        {
            "request": request,
            "comparisons": comparisons,
            "page": page,
            "total_pages": total_pages,
            "total": total,
            "status": status,
            "test_name": test_name
        }
    )


@router.get("/api/comparisons/{comparison_id}", response_model=AudioComparisonResponse)
async def get_audio_comparison(
    comparison_id: int,
    db: Session = Depends(get_db)
):
    """
    Get audio comparison by ID.
    
    - **comparison_id**: Comparison ID
    """
    comparator = AudioComparator()
    comparison = comparator.get_comparison(comparison_id, db)
    
    if not comparison:
        raise HTTPException(status_code=404, detail="Comparison not found")
    
    return comparison


@router.get("/comparisons/{comparison_id}", response_class=HTMLResponse)
async def audio_comparison_detail(
    request: Request,
    comparison_id: int,
    db: Session = Depends(get_db)
):
    """Audio comparison detail page."""
    comparator = AudioComparator()
    comparison = comparator.get_comparison(comparison_id, db)
    
    if not comparison:
        raise HTTPException(status_code=404, detail="Comparison not found")
    
    return templates.TemplateResponse(
        "audio_comparison_detail.html",
        {
            "request": request,
            "comparison": comparison
        }
    )


@router.delete("/api/comparisons/{comparison_id}")
async def delete_audio_comparison(
    comparison_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete audio comparison.
    
    - **comparison_id**: Comparison ID
    """
    comparator = AudioComparator()
    success = comparator.delete_comparison(comparison_id, db)
    
    if not success:
        raise HTTPException(status_code=404, detail="Comparison not found")
    
    return {"message": "Comparison deleted successfully"}
