"""FIX Protocol Message Schemas."""
from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field, validator


class SendFixMessageRequest(BaseModel):
    """Request schema for sending FIX messages."""
    
    msg_type: str = Field(..., description="FIX message type (e.g., 'D' for NewOrderSingle)")
    sender_comp_id: str = Field(..., description="Sender CompID")
    target_comp_id: str = Field(..., description="Target CompID")
    
    # Order fields (for NewOrderSingle)
    cl_ord_id: Optional[str] = Field(None, description="Client Order ID")
    symbol: Optional[str] = Field(None, description="Trading symbol")
    side: Optional[str] = Field(None, description="Side: 1=Buy, 2=Sell")
    order_qty: Optional[str] = Field(None, description="Order quantity")
    ord_type: Optional[str] = Field(None, description="Order type: 1=Market, 2=Limit")
    price: Optional[str] = Field(None, description="Price (for limit orders)")
    time_in_force: Optional[str] = Field(None, description="Time in force: 0=Day, 1=GTC")
    
    # Additional fields
    fields: Optional[Dict[int, str]] = Field(None, description="Additional FIX tag=value pairs")
    session_id: Optional[str] = Field(None, description="Optional session identifier")
    
    class Config:
        schema_extra = {
            "example": {
                "msg_type": "D",
                "sender_comp_id": "SENDER",
                "target_comp_id": "TARGET",
                "cl_ord_id": "ORDER123",
                "symbol": "AAPL",
                "side": "1",
                "order_qty": "100",
                "ord_type": "2",
                "price": "150.50",
                "time_in_force": "0"
            }
        }


class FixMessageResponse(BaseModel):
    """Response schema for FIX messages."""
    
    id: int
    msg_type: str
    msg_seq_num: Optional[int]
    sender_comp_id: str
    target_comp_id: str
    message_data: str
    raw_message: Optional[str]
    status: str
    response_message: Optional[str]
    error_message: Optional[str]
    session_id: Optional[str]
    cl_ord_id: Optional[str]
    symbol: Optional[str]
    side: Optional[str]
    order_qty: Optional[str]
    price: Optional[str]
    created_at: datetime
    sent_at: Optional[datetime]
    acknowledged_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class FixMessageListResponse(BaseModel):
    """Response schema for list of FIX messages."""
    
    items: list[FixMessageResponse]
    total: int
    page: int
    page_size: int
    
    class Config:
        from_attributes = True


class FixSessionConfig(BaseModel):
    """Configuration for FIX session."""
    
    sender_comp_id: str = Field(..., description="Sender CompID")
    target_comp_id: str = Field(..., description="Target CompID")
    host: str = Field("localhost", description="Target host")
    port: int = Field(9876, description="Target port")
    begin_string: str = Field("FIX.4.4", description="FIX protocol version")
    heartbeat_interval: int = Field(30, description="Heartbeat interval in seconds")
    
    class Config:
        schema_extra = {
            "example": {
                "sender_comp_id": "SENDER",
                "target_comp_id": "TARGET",
                "host": "localhost",
                "port": 9876,
                "begin_string": "FIX.4.4",
                "heartbeat_interval": 30
            }
        }
