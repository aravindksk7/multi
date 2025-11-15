"""FIX Protocol Messaging API Routes."""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.database import get_db
from app.modules.fix_messaging import (
    FixMessagingService,
    SendFixMessageRequest,
    FixMessageResponse,
    FixMessageListResponse
)

router = APIRouter(prefix="/api/fix", tags=["FIX Messaging"])

fix_service = FixMessagingService()


@router.post("/messages", response_model=FixMessageResponse, status_code=201)
async def send_fix_message(
    request: SendFixMessageRequest,
    db: Session = Depends(get_db)
):
    """
    Send a FIX protocol message.
    
    This endpoint creates and sends a FIX message using the QuickFIX library.
    
    Example for NewOrderSingle (D):
    ```json
    {
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
    ```
    """
    fix_msg = fix_service.create_fix_message(request, db)
    return fix_msg


@router.get("/messages/{message_id}", response_model=FixMessageResponse)
async def get_fix_message(
    message_id: int,
    db: Session = Depends(get_db)
):
    """Get a FIX message by ID."""
    fix_msg = fix_service.get_message(message_id, db)
    if not fix_msg:
        raise HTTPException(status_code=404, detail="FIX message not found")
    return fix_msg


@router.get("/messages", response_model=FixMessageListResponse)
async def list_fix_messages(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(20, ge=1, le=100, description="Maximum records to return"),
    status: Optional[str] = Query(None, description="Filter by status"),
    msg_type: Optional[str] = Query(None, description="Filter by message type"),
    sender_comp_id: Optional[str] = Query(None, description="Filter by sender CompID"),
    target_comp_id: Optional[str] = Query(None, description="Filter by target CompID"),
    cl_ord_id: Optional[str] = Query(None, description="Filter by client order ID"),
    db: Session = Depends(get_db)
):
    """
    List FIX messages with optional filters.
    
    Supports pagination and filtering by:
    - status: PENDING, SENT, FAILED, ACKNOWLEDGED, REJECTED
    - msg_type: D (NewOrderSingle), F (OrderCancelRequest), etc.
    - sender_comp_id: Sender identifier
    - target_comp_id: Target identifier
    - cl_ord_id: Client order ID
    """
    messages, total = fix_service.list_messages(
        db, skip, limit, status, msg_type,
        sender_comp_id, target_comp_id, cl_ord_id
    )
    
    return FixMessageListResponse(
        items=messages,
        total=total,
        page=skip // limit + 1,
        page_size=limit
    )


@router.delete("/messages/{message_id}", status_code=204)
async def delete_fix_message(
    message_id: int,
    db: Session = Depends(get_db)
):
    """Delete a FIX message by ID."""
    deleted = fix_service.delete_message(message_id, db)
    if not deleted:
        raise HTTPException(status_code=404, detail="FIX message not found")
    return None
