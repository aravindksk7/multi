"""
OUCH/ITCH Protocol Testing Module

This module provides functionality to test NASDAQ OUCH and ITCH protocols
using the nasdaq-protocols library. It supports:
- OUCH (Order Entry Protocol) - bidirectional message-based protocol
- ITCH (Market Data Protocol) - unidirectional feed protocol

Features:
- Protocol message creation and validation
- Session management (SoupBinTCP)
- Message sending and receiving
- Protocol conformance testing
- Message history tracking
"""

from .models import ProtocolTest, ProtocolMessage, ProtocolSession, ProtocolType, MessageDirection, SessionStatus, TestStatus
from .schemas import (
    ProtocolTestRequest,
    ProtocolTestResponse,
    ProtocolMessageSchema,
    ProtocolSessionSchema,
    ProtocolSessionCreate,
    SendMessageRequest,
    ProtocolTestListResponse,
    ExecuteTestRequest,
    TestResultSummary
)
from .service import ProtocolTestingService

__all__ = [
    'ProtocolTest',
    'ProtocolMessage',
    'ProtocolSession',
    'ProtocolType',
    'MessageDirection',
    'SessionStatus',
    'TestStatus',
    'ProtocolTestRequest',
    'ProtocolTestResponse',
    'ProtocolMessageSchema',
    'ProtocolSessionSchema',
    'ProtocolSessionCreate',
    'SendMessageRequest',
    'ProtocolTestListResponse',
    'ExecuteTestRequest',
    'TestResultSummary',
    'ProtocolTestingService'
]
