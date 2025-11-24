"""Tests for FIX Messaging API."""
import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_send_fix_message():
    """Test sending a FIX message."""
    response = client.post(
        "/api/fix/messages",
        json={
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
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["msg_type"] == "D"
    assert data["sender_comp_id"] == "SENDER"
    assert data["target_comp_id"] == "TARGET"
    assert data["cl_ord_id"] == "ORDER123"
    assert data["symbol"] == "AAPL"
    # Status can be SENT (if server running) or FAILED (if server not running during test)
    assert data["status"] in ["PENDING", "SENT", "FAILED"]
    assert "id" in data
    # If failed, should have error message
    if data["status"] == "FAILED":
        assert data["error_message"] is not None


def test_get_fix_message():
    """Test retrieving a FIX message."""
    # First create a message
    create_response = client.post(
        "/api/fix/messages",
        json={
            "msg_type": "D",
            "sender_comp_id": "SENDER",
            "target_comp_id": "TARGET",
            "cl_ord_id": "ORDER456",
            "symbol": "MSFT",
            "side": "2",
            "order_qty": "50",
            "ord_type": "1"
        }
    )
    
    message_id = create_response.json()["id"]
    
    # Retrieve it
    response = client.get(f"/api/fix/messages/{message_id}")
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == message_id
    assert data["cl_ord_id"] == "ORDER456"
    assert data["symbol"] == "MSFT"


def test_list_fix_messages():
    """Test listing FIX messages."""
    # Create some messages
    for i in range(3):
        client.post(
            "/api/fix/messages",
            json={
                "msg_type": "D",
                "sender_comp_id": f"SENDER{i}",
                "target_comp_id": "TARGET",
                "cl_ord_id": f"ORDER{i}",
                "symbol": "GOOGL",
                "side": "1",
                "order_qty": "10"
            }
        )
    
    # List messages
    response = client.get("/api/fix/messages")
    
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert data["total"] >= 3
    assert len(data["items"]) >= 3


def test_list_fix_messages_with_filters():
    """Test listing FIX messages with filters."""
    # Create message with specific sender
    client.post(
        "/api/fix/messages",
        json={
            "msg_type": "D",
            "sender_comp_id": "FILTER_TEST",
            "target_comp_id": "TARGET",
            "cl_ord_id": "FILTER_ORDER",
            "symbol": "TSLA",
            "side": "1",
            "order_qty": "25"
        }
    )
    
    # Filter by sender
    response = client.get("/api/fix/messages?sender_comp_id=FILTER_TEST")
    
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 1
    for item in data["items"]:
        assert item["sender_comp_id"] == "FILTER_TEST"


def test_delete_fix_message():
    """Test deleting a FIX message."""
    # Create a message
    create_response = client.post(
        "/api/fix/messages",
        json={
            "msg_type": "D",
            "sender_comp_id": "SENDER",
            "target_comp_id": "TARGET",
            "cl_ord_id": "DELETE_ORDER",
            "symbol": "AMZN",
            "side": "1",
            "order_qty": "5"
        }
    )
    
    message_id = create_response.json()["id"]
    
    # Delete it
    response = client.delete(f"/api/fix/messages/{message_id}")
    
    assert response.status_code == 204
    
    # Verify it's gone
    get_response = client.get(f"/api/fix/messages/{message_id}")
    assert get_response.status_code == 404


def test_send_fix_message_minimal():
    """Test sending a FIX message with minimal fields."""
    response = client.post(
        "/api/fix/messages",
        json={
            "msg_type": "0",  # Heartbeat
            "sender_comp_id": "SENDER",
            "target_comp_id": "TARGET"
        }
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["msg_type"] == "0"
    assert data["sender_comp_id"] == "SENDER"


def test_get_nonexistent_fix_message():
    """Test retrieving a non-existent FIX message."""
    response = client.get("/api/fix/messages/999999")
    
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_delete_nonexistent_fix_message():
    """Test deleting a non-existent FIX message."""
    response = client.delete("/api/fix/messages/999999")
    
    assert response.status_code == 404
