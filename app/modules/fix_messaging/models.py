"""FIX Protocol Message Model."""
from datetime import datetime
from enum import Enum as PyEnum
from sqlalchemy import (
    Column, Integer, String, Text, DateTime, Enum, Index
)

from app.database import Base


class FixMessageStatus(str, PyEnum):
    """FIX message status enumeration."""
    PENDING = "PENDING"
    SENT = "SENT"
    FAILED = "FAILED"
    ACKNOWLEDGED = "ACKNOWLEDGED"
    REJECTED = "REJECTED"


class FixMessageType(str, PyEnum):
    """FIX message types."""
    NEW_ORDER_SINGLE = "D"  # NewOrderSingle
    ORDER_CANCEL_REQUEST = "F"  # OrderCancelRequest
    ORDER_STATUS_REQUEST = "H"  # OrderStatusRequest
    EXECUTION_REPORT = "8"  # ExecutionReport
    ORDER_CANCEL_REJECT = "9"  # OrderCancelReject
    LOGON = "A"  # Logon
    LOGOUT = "5"  # Logout
    HEARTBEAT = "0"  # Heartbeat
    TEST_REQUEST = "1"  # TestRequest


class FixMessage(Base):
    """Model for FIX protocol messages."""
    
    __tablename__ = "fix_messages"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Message Identity
    msg_type = Column(String(10), nullable=False, index=True)
    msg_seq_num = Column(Integer, nullable=True)
    sender_comp_id = Column(String(100), nullable=False, index=True)
    target_comp_id = Column(String(100), nullable=False, index=True)
    
    # Message Content
    message_data = Column(Text, nullable=False)  # Full FIX message
    raw_message = Column(Text, nullable=True)  # Raw wire format
    
    # Status
    status = Column(
        Enum(FixMessageStatus),
        default=FixMessageStatus.PENDING,
        nullable=False,
        index=True
    )
    
    # Response/Acknowledgment
    response_message = Column(Text, nullable=True)
    error_message = Column(Text, nullable=True)
    
    # Metadata
    session_id = Column(String(255), nullable=True, index=True)
    cl_ord_id = Column(String(255), nullable=True, index=True)  # Client Order ID
    symbol = Column(String(50), nullable=True, index=True)
    side = Column(String(10), nullable=True)  # Buy/Sell
    order_qty = Column(String(50), nullable=True)
    price = Column(String(50), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    sent_at = Column(DateTime, nullable=True)
    acknowledged_at = Column(DateTime, nullable=True)
    
    # Indexes for common queries
    __table_args__ = (
        Index('idx_fix_status_created', 'status', 'created_at'),
        Index('idx_fix_sender_target', 'sender_comp_id', 'target_comp_id'),
        Index('idx_fix_cl_ord_id', 'cl_ord_id'),
    )
    
    def __repr__(self):
        return f"<FixMessage(id={self.id}, type={self.msg_type}, status={self.status})>"
