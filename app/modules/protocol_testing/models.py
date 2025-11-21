"""
Database models for OUCH/ITCH protocol testing
"""
from datetime import datetime
from enum import Enum as PyEnum
from sqlalchemy import Column, Integer, String, Text, DateTime, Enum, ForeignKey, JSON, BigInteger
from sqlalchemy.orm import relationship
from app.database import Base


class ProtocolType(PyEnum):
    """Supported protocol types"""
    OUCH = "OUCH"
    ITCH = "ITCH"


class MessageDirection(PyEnum):
    """Message direction relative to server"""
    INCOMING = "incoming"  # Client to Server
    OUTGOING = "outgoing"  # Server to Client


class SessionStatus(PyEnum):
    """Protocol session status"""
    CREATED = "CREATED"
    CONNECTING = "CONNECTING"
    CONNECTED = "CONNECTED"
    DISCONNECTED = "DISCONNECTED"
    ERROR = "ERROR"


class TestStatus(PyEnum):
    """Protocol test execution status"""
    CREATED = "CREATED"
    RUNNING = "RUNNING"
    PASSED = "PASSED"
    FAILED = "FAILED"
    ERROR = "ERROR"


class ProtocolSession(Base):
    """
    Represents a SoupBinTCP protocol session for OUCH/ITCH
    """
    __tablename__ = "protocol_sessions"

    id = Column(Integer, primary_key=True, index=True)
    protocol_type = Column(Enum(ProtocolType), nullable=False, index=True)
    
    # Connection details
    host = Column(String(255), nullable=False)
    port = Column(Integer, nullable=False)
    username = Column(String(50), nullable=False)
    session_id = Column(String(50), nullable=True)
    
    # Session info
    status = Column(Enum(SessionStatus), default=SessionStatus.CREATED, index=True)
    sequence_number = Column(BigInteger, default=1)
    
    # Heartbeat settings
    client_heartbeat_interval = Column(Integer, default=10)
    server_heartbeat_interval = Column(Integer, default=10)
    
    # Metadata
    session_metadata = Column(JSON, nullable=True)
    error_message = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    connected_at = Column(DateTime, nullable=True)
    disconnected_at = Column(DateTime, nullable=True)
    
    # Relationships
    tests = relationship("ProtocolTest", back_populates="session", cascade="all, delete-orphan")
    messages = relationship("ProtocolMessage", back_populates="session", cascade="all, delete-orphan")


class ProtocolTest(Base):
    """
    Represents a protocol conformance test
    """
    __tablename__ = "protocol_tests"

    id = Column(Integer, primary_key=True, index=True)
    test_name = Column(String(255), nullable=False, index=True)
    protocol_type = Column(Enum(ProtocolType), nullable=False, index=True)
    
    # Test configuration
    test_description = Column(Text, nullable=True)
    test_config = Column(JSON, nullable=True)  # Test-specific configuration
    
    # Status tracking
    status = Column(Enum(TestStatus), default=TestStatus.CREATED, index=True)
    
    # Results
    result_summary = Column(JSON, nullable=True)  # Test result summary
    error_details = Column(Text, nullable=True)
    
    # Metrics
    messages_sent = Column(Integer, default=0)
    messages_received = Column(Integer, default=0)
    duration_seconds = Column(Integer, nullable=True)
    
    # Session relationship
    session_id = Column(Integer, ForeignKey("protocol_sessions.id"), nullable=True)
    session = relationship("ProtocolSession", back_populates="tests")
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    
    # Relationships
    messages = relationship("ProtocolMessage", back_populates="test", cascade="all, delete-orphan")


class ProtocolMessage(Base):
    """
    Represents a protocol message (OUCH/ITCH)
    """
    __tablename__ = "protocol_messages"

    id = Column(Integer, primary_key=True, index=True)
    protocol_type = Column(Enum(ProtocolType), nullable=False, index=True)
    
    # Message details
    message_type = Column(String(100), nullable=False, index=True)  # e.g., "EnterOrder", "SystemEvent"
    message_indicator = Column(Integer, nullable=False)  # Message type indicator
    direction = Column(Enum(MessageDirection), nullable=False, index=True)
    
    # Message content
    message_data = Column(JSON, nullable=False)  # Message fields as JSON
    raw_bytes = Column(Text, nullable=True)  # Hex-encoded raw bytes
    
    # Validation
    is_valid = Column(Integer, default=1)  # SQLite boolean (1=True, 0=False)
    validation_errors = Column(JSON, nullable=True)
    
    # Context
    sequence_number = Column(BigInteger, nullable=True)
    
    # Relationships
    session_id = Column(Integer, ForeignKey("protocol_sessions.id"), nullable=True)
    session = relationship("ProtocolSession", back_populates="messages")
    
    test_id = Column(Integer, ForeignKey("protocol_tests.id"), nullable=True)
    test = relationship("ProtocolTest", back_populates="messages")
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    sent_at = Column(DateTime, nullable=True)
    received_at = Column(DateTime, nullable=True)
