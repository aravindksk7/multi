"""
Pydantic schemas for OUCH/ITCH protocol testing
"""
from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
from app.modules.protocol_testing.models import ProtocolType, MessageDirection, SessionStatus, TestStatus


# Protocol Session Schemas
class ProtocolSessionCreate(BaseModel):
    protocol_type: ProtocolType
    host: str = Field(..., description="Protocol server hostname or IP")
    port: int = Field(..., gt=0, lt=65536, description="Protocol server port")
    username: str = Field(..., max_length=50, description="Username for SoupBinTCP login")
    password: str = Field(..., max_length=50, description="Password for SoupBinTCP login")
    session_id: Optional[str] = Field(None, max_length=50, description="Session ID (optional)")
    sequence_number: int = Field(default=1, ge=0, description="Starting sequence number")
    client_heartbeat_interval: int = Field(default=10, ge=1, description="Client heartbeat interval in seconds")
    server_heartbeat_interval: int = Field(default=10, ge=1, description="Server heartbeat interval in seconds")
    session_metadata: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True


class ProtocolSessionSchema(BaseModel):
    id: int
    protocol_type: ProtocolType
    host: str
    port: int
    username: str
    session_id: Optional[str]
    status: SessionStatus
    sequence_number: int
    client_heartbeat_interval: int
    server_heartbeat_interval: int
    session_metadata: Optional[Dict[str, Any]]
    error_message: Optional[str]
    created_at: datetime
    connected_at: Optional[datetime]
    disconnected_at: Optional[datetime]

    class Config:
        from_attributes = True


# Protocol Message Schemas
class MessageFieldSchema(BaseModel):
    """Schema for individual message fields"""
    name: str = Field(..., description="Field name")
    value: Any = Field(..., description="Field value")
    type: str = Field(..., description="Field data type")


class SendMessageRequest(BaseModel):
    """Request to send a protocol message"""
    protocol_type: ProtocolType
    message_type: str = Field(..., description="Message type name (e.g., 'EnterOrder', 'SystemEvent')")
    message_indicator: int = Field(..., description="Message type indicator byte")
    direction: MessageDirection
    fields: Dict[str, Any] = Field(..., description="Message field values as key-value pairs")
    session_id: Optional[int] = Field(None, description="Session ID to send message on")
    test_id: Optional[int] = Field(None, description="Test ID to associate message with")

    class Config:
        from_attributes = True


class ProtocolMessageSchema(BaseModel):
    id: int
    protocol_type: ProtocolType
    message_type: str
    message_indicator: int
    direction: MessageDirection
    message_data: Dict[str, Any]
    raw_bytes: Optional[str]
    is_valid: bool
    validation_errors: Optional[Dict[str, Any]]
    sequence_number: Optional[int]
    session_id: Optional[int]
    test_id: Optional[int]
    created_at: datetime
    sent_at: Optional[datetime]
    received_at: Optional[datetime]

    class Config:
        from_attributes = True


# Protocol Test Schemas
class ProtocolTestRequest(BaseModel):
    """Request to create a protocol test"""
    test_name: str = Field(..., max_length=255, description="Test name")
    protocol_type: ProtocolType
    test_description: Optional[str] = Field(None, description="Test description")
    test_config: Optional[Dict[str, Any]] = Field(None, description="Test-specific configuration")
    
    # Session details (if creating new session)
    session_id: Optional[int] = Field(None, description="Existing session ID")
    host: Optional[str] = Field(None, description="Protocol server hostname (if creating new session)")
    port: Optional[int] = Field(None, gt=0, lt=65536, description="Protocol server port (if creating new session)")
    username: Optional[str] = Field(None, max_length=50, description="Username (if creating new session)")
    password: Optional[str] = Field(None, max_length=50, description="Password (if creating new session)")

    class Config:
        from_attributes = True


class ProtocolTestResponse(BaseModel):
    id: int
    test_name: str
    protocol_type: ProtocolType
    test_description: Optional[str]
    test_config: Optional[Dict[str, Any]]
    status: TestStatus
    result_summary: Optional[Dict[str, Any]]
    error_details: Optional[str]
    messages_sent: int
    messages_received: int
    duration_seconds: Optional[int]
    session_id: Optional[int]
    session: Optional[ProtocolSessionSchema]
    created_at: datetime
    started_at: Optional[datetime]
    completed_at: Optional[datetime]

    class Config:
        from_attributes = True


class ProtocolTestListResponse(BaseModel):
    """Response for listing protocol tests"""
    tests: List[ProtocolTestResponse]
    total: int
    page: int
    page_size: int

    class Config:
        from_attributes = True


class ProtocolMessageListResponse(BaseModel):
    """Response for listing protocol messages"""
    messages: List[ProtocolMessageSchema]
    total: int
    page: int
    page_size: int

    class Config:
        from_attributes = True


# Test execution schemas
class ExecuteTestRequest(BaseModel):
    """Request to execute a protocol test"""
    test_id: int
    timeout_seconds: int = Field(default=60, ge=1, le=3600, description="Test execution timeout")


class MessageValidationResult(BaseModel):
    """Result of message validation"""
    is_valid: bool
    message_type: str
    errors: List[str] = []
    warnings: List[str] = []


class TestResultSummary(BaseModel):
    """Summary of test execution results"""
    test_id: int
    test_name: str
    status: TestStatus
    passed: bool
    messages_sent: int
    messages_received: int
    validation_results: List[MessageValidationResult]
    duration_seconds: float
    error_message: Optional[str] = None
