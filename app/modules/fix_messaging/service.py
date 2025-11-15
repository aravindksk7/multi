"""FIX Protocol Messaging Service using SimpleFIX."""
import simplefix
from datetime import datetime
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session

from .models import FixMessage, FixMessageStatus, FixMessageType
from .schemas import SendFixMessageRequest


class FixMessagingService:
    """Service for sending and managing FIX protocol messages."""
    
    def __init__(self):
        """Initialize FIX messaging service."""
        self.msg_seq_num = 1
    
    def create_fix_message(
        self,
        request: SendFixMessageRequest,
        db: Session
    ) -> FixMessage:
        """
        Create and send a FIX message.
        
        Args:
            request: FIX message request data
            db: Database session
            
        Returns:
            FixMessage: Created FIX message record
        """
        try:
            # Build FIX message
            message = self._build_fix_message(request)
            raw_message = message.encode()
            
            # Create database record
            fix_msg = FixMessage(
                msg_type=request.msg_type,
                msg_seq_num=self.msg_seq_num,
                sender_comp_id=request.sender_comp_id,
                target_comp_id=request.target_comp_id,
                message_data=raw_message.decode('latin-1'),
                raw_message=raw_message.decode('latin-1'),
                status=FixMessageStatus.PENDING,
                session_id=request.session_id,
                cl_ord_id=request.cl_ord_id,
                symbol=request.symbol,
                side=request.side,
                order_qty=request.order_qty,
                price=request.price,
                created_at=datetime.utcnow()
            )
            
            db.add(fix_msg)
            db.commit()
            db.refresh(fix_msg)
            
            # Simulate sending (in real scenario, would use QuickFIX session)
            fix_msg.status = FixMessageStatus.SENT
            fix_msg.sent_at = datetime.utcnow()
            db.commit()
            db.refresh(fix_msg)
            
            self.msg_seq_num += 1
            
            return fix_msg
            
        except Exception as e:
            # Create failed message record
            fix_msg = FixMessage(
                msg_type=request.msg_type,
                msg_seq_num=self.msg_seq_num,
                sender_comp_id=request.sender_comp_id,
                target_comp_id=request.target_comp_id,
                message_data="",
                status=FixMessageStatus.FAILED,
                error_message=str(e),
                session_id=request.session_id,
                cl_ord_id=request.cl_ord_id,
                symbol=request.symbol,
                side=request.side,
                order_qty=request.order_qty,
                price=request.price,
                created_at=datetime.utcnow()
            )
            
            db.add(fix_msg)
            db.commit()
            db.refresh(fix_msg)
            
            return fix_msg
    
    def _build_fix_message(self, request: SendFixMessageRequest) -> simplefix.FixMessage:
        """
        Build a FIX protocol message using SimpleFIX.
        
        Args:
            request: FIX message request data
            
        Returns:
            simplefix.FixMessage: Constructed FIX message
        """
        message = simplefix.FixMessage()
        
        # Set standard header fields
        message.append_string("8=FIX.4.4")  # BeginString
        message.append_string(f"35={request.msg_type}")  # MsgType
        message.append_string(f"49={request.sender_comp_id}")  # SenderCompID
        message.append_string(f"56={request.target_comp_id}")  # TargetCompID
        message.append_string(f"34={self.msg_seq_num}")  # MsgSeqNum
        message.append_utc_timestamp(52, datetime.utcnow())  # SendingTime
        
        # Add message-specific fields based on type
        if request.msg_type == "D":  # NewOrderSingle
            if request.cl_ord_id:
                message.append_string(f"11={request.cl_ord_id}")  # ClOrdID
            if request.symbol:
                message.append_string(f"55={request.symbol}")  # Symbol
            if request.side:
                message.append_string(f"54={request.side}")  # Side
            if request.order_qty:
                message.append_string(f"38={request.order_qty}")  # OrderQty
            if request.ord_type:
                message.append_string(f"40={request.ord_type}")  # OrdType
            if request.price:
                message.append_string(f"44={request.price}")  # Price
            if request.time_in_force:
                message.append_string(f"59={request.time_in_force}")  # TimeInForce
            
            # TransactTime is required
            message.append_utc_timestamp(60, datetime.utcnow())
        
        # Add additional custom fields
        if request.fields:
            for tag, value in request.fields.items():
                message.append_string(f"{tag}={value}")
        
        return message
    
    def get_message(self, message_id: int, db: Session) -> Optional[FixMessage]:
        """
        Get a FIX message by ID.
        
        Args:
            message_id: Message ID
            db: Database session
            
        Returns:
            FixMessage or None
        """
        return db.query(FixMessage).filter(FixMessage.id == message_id).first()
    
    def list_messages(
        self,
        db: Session,
        skip: int = 0,
        limit: int = 20,
        status: Optional[str] = None,
        msg_type: Optional[str] = None,
        sender_comp_id: Optional[str] = None,
        target_comp_id: Optional[str] = None,
        cl_ord_id: Optional[str] = None
    ) -> tuple[list[FixMessage], int]:
        """
        List FIX messages with filters.
        
        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return
            status: Filter by status
            msg_type: Filter by message type
            sender_comp_id: Filter by sender
            target_comp_id: Filter by target
            cl_ord_id: Filter by client order ID
            
        Returns:
            Tuple of (messages, total_count)
        """
        query = db.query(FixMessage)
        
        if status:
            query = query.filter(FixMessage.status == status)
        if msg_type:
            query = query.filter(FixMessage.msg_type == msg_type)
        if sender_comp_id:
            query = query.filter(FixMessage.sender_comp_id == sender_comp_id)
        if target_comp_id:
            query = query.filter(FixMessage.target_comp_id == target_comp_id)
        if cl_ord_id:
            query = query.filter(FixMessage.cl_ord_id == cl_ord_id)
        
        total = query.count()
        messages = query.order_by(FixMessage.created_at.desc()).offset(skip).limit(limit).all()
        
        return messages, total
    
    def delete_message(self, message_id: int, db: Session) -> bool:
        """
        Delete a FIX message.
        
        Args:
            message_id: Message ID
            db: Database session
            
        Returns:
            bool: True if deleted, False if not found
        """
        message = db.query(FixMessage).filter(FixMessage.id == message_id).first()
        if message:
            db.delete(message)
            db.commit()
            return True
        return False
