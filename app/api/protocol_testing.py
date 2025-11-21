"""
FastAPI routes for OUCH/ITCH protocol testing
"""
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import Optional

from app.database import get_db
from app.modules.protocol_testing import (
    ProtocolTestingService,
    ProtocolTestRequest,
    ProtocolTestResponse,
    ProtocolTestListResponse,
    SendMessageRequest,
    ProtocolMessageSchema,
    ProtocolSessionCreate,
    ProtocolSessionSchema,
    ExecuteTestRequest,
    TestResultSummary,
    ProtocolType,
    TestStatus
)

router = APIRouter(prefix="/protocols", tags=["Protocol Testing"])
templates = Jinja2Templates(directory="app/templates")


# Web UI Routes

@router.get("/", response_class=HTMLResponse)
async def protocol_home(request: Request):
    """Protocol testing home page"""
    return templates.TemplateResponse("protocol_home.html", {"request": request})


@router.get("/test/create", response_class=HTMLResponse)
async def create_test_form(request: Request):
    """Form to create a new protocol test"""
    return templates.TemplateResponse("protocol_test_form.html", {"request": request})


@router.get("/tests", response_class=HTMLResponse)
async def list_tests_page(
    request: Request,
    protocol_type: Optional[str] = None,
    status: Optional[str] = None,
    page: int = 1,
    page_size: int = 20,
    db: Session = Depends(get_db)
):
    """List protocol tests page"""
    service = ProtocolTestingService(db)
    
    # Parse filters
    protocol_filter = ProtocolType(protocol_type) if protocol_type else None
    status_filter = TestStatus(status) if status else None
    
    skip = (page - 1) * page_size
    tests, total = service.list_tests(
        protocol_type=protocol_filter,
        status=status_filter,
        skip=skip,
        limit=page_size
    )
    
    return templates.TemplateResponse("protocol_tests_list.html", {
        "request": request,
        "tests": tests,
        "total": total,
        "page": page,
        "page_size": page_size,
        "protocol_type": protocol_type,
        "status": status
    })


@router.get("/test/{test_id}", response_class=HTMLResponse)
async def view_test_detail(
    request: Request,
    test_id: int,
    db: Session = Depends(get_db)
):
    """View protocol test details"""
    service = ProtocolTestingService(db)
    test = service.get_test(test_id)
    
    if not test:
        raise HTTPException(status_code=404, detail="Test not found")
    
    return templates.TemplateResponse("protocol_test_detail.html", {
        "request": request,
        "test": test
    })


# API Routes

@router.post("/test", response_model=ProtocolTestResponse)
async def create_test(
    request: ProtocolTestRequest,
    db: Session = Depends(get_db)
):
    """
    Create a new protocol test
    
    - **test_name**: Test name
    - **protocol_type**: OUCH or ITCH
    - **test_description**: Optional test description
    - **test_config**: Optional test-specific configuration
    - **session_id**: Existing session ID (or provide host/port/username/password to create new)
    """
    service = ProtocolTestingService(db)
    
    # Create session if needed
    session_id = request.session_id
    if not session_id and request.host and request.port and request.username and request.password:
        session = service.create_session(
            protocol_type=request.protocol_type,
            host=request.host,
            port=request.port,
            username=request.username,
            password=request.password
        )
        session_id = session.id
    
    test = service.create_test(
        test_name=request.test_name,
        protocol_type=request.protocol_type,
        test_description=request.test_description,
        test_config=request.test_config,
        session_id=session_id
    )
    
    return test


@router.get("/test/{test_id}", response_model=ProtocolTestResponse)
async def get_test(test_id: int, db: Session = Depends(get_db)):
    """Get protocol test by ID"""
    service = ProtocolTestingService(db)
    test = service.get_test(test_id)
    
    if not test:
        raise HTTPException(status_code=404, detail="Test not found")
    
    return test


@router.get("/tests/list", response_model=ProtocolTestListResponse)
async def list_tests(
    protocol_type: Optional[ProtocolType] = None,
    status: Optional[TestStatus] = None,
    page: int = 1,
    page_size: int = 20,
    db: Session = Depends(get_db)
):
    """
    List protocol tests with optional filtering
    
    - **protocol_type**: Filter by OUCH or ITCH
    - **status**: Filter by test status
    - **page**: Page number (1-indexed)
    - **page_size**: Items per page
    """
    service = ProtocolTestingService(db)
    skip = (page - 1) * page_size
    
    tests, total = service.list_tests(
        protocol_type=protocol_type,
        status=status,
        skip=skip,
        limit=page_size
    )
    
    return ProtocolTestListResponse(
        tests=tests,
        total=total,
        page=page,
        page_size=page_size
    )


@router.post("/test/{test_id}/execute", response_model=TestResultSummary)
async def execute_test(
    test_id: int,
    request: ExecuteTestRequest,
    db: Session = Depends(get_db)
):
    """
    Execute a protocol conformance test
    
    - **test_id**: Test ID to execute
    - **timeout_seconds**: Execution timeout in seconds
    """
    service = ProtocolTestingService(db)
    test = await service.execute_test(test_id, request.timeout_seconds)
    
    return TestResultSummary(
        test_id=test.id,
        test_name=test.test_name,
        status=test.status,
        passed=test.status == TestStatus.PASSED,
        messages_sent=test.messages_sent,
        messages_received=test.messages_received,
        validation_results=[],
        duration_seconds=test.duration_seconds or 0,
        error_message=test.error_details
    )


@router.delete("/test/{test_id}")
async def delete_test(test_id: int, db: Session = Depends(get_db)):
    """Delete a protocol test"""
    service = ProtocolTestingService(db)
    deleted = service.delete_test(test_id)
    
    if not deleted:
        raise HTTPException(status_code=404, detail="Test not found")
    
    return {"message": "Test deleted successfully"}


# Session management routes

@router.post("/session", response_model=ProtocolSessionSchema)
async def create_session(
    request: ProtocolSessionCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new protocol session
    
    - **protocol_type**: OUCH or ITCH
    - **host**: Protocol server hostname or IP
    - **port**: Protocol server port
    - **username**: SoupBinTCP username
    - **password**: SoupBinTCP password
    - **session_id**: Optional session ID
    - **sequence_number**: Starting sequence number
    """
    service = ProtocolTestingService(db)
    session = service.create_session(
        protocol_type=request.protocol_type,
        host=request.host,
        port=request.port,
        username=request.username,
        password=request.password,
        session_id=request.session_id,
        sequence_number=request.sequence_number,
        client_heartbeat_interval=request.client_heartbeat_interval,
        server_heartbeat_interval=request.server_heartbeat_interval,
        session_metadata=request.session_metadata
    )
    
    return session


@router.post("/session/{session_id}/connect", response_model=ProtocolSessionSchema)
async def connect_session(session_id: int, db: Session = Depends(get_db)):
    """Connect to a protocol server"""
    service = ProtocolTestingService(db)
    session = await service.connect_session(session_id)
    return session


# Message management routes

@router.post("/message", response_model=ProtocolMessageSchema)
async def create_message(
    request: SendMessageRequest,
    db: Session = Depends(get_db)
):
    """
    Create a protocol message
    
    - **protocol_type**: OUCH or ITCH
    - **message_type**: Message type name (e.g., 'EnterOrder')
    - **message_indicator**: Message type indicator byte
    - **direction**: INCOMING or OUTGOING
    - **fields**: Message field values as key-value pairs
    - **session_id**: Optional session ID
    - **test_id**: Optional test ID
    """
    service = ProtocolTestingService(db)
    message = service.create_message(
        protocol_type=request.protocol_type,
        message_type=request.message_type,
        message_indicator=request.message_indicator,
        direction=request.direction,
        fields=request.fields,
        session_id=request.session_id,
        test_id=request.test_id
    )
    
    return message


@router.post("/message/{message_id}/send", response_model=ProtocolMessageSchema)
async def send_message(message_id: int, db: Session = Depends(get_db)):
    """Send a protocol message"""
    service = ProtocolTestingService(db)
    message = await service.send_message(message_id)
    return message
