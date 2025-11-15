# FIX Protocol Messaging Guide

## Overview

The FIX (Financial Information eXchange) Protocol messaging module enables you to create, send, and manage FIX protocol messages for financial trading systems. This module uses the SimpleFIX library for pure Python FIX message handling.

## Supported Features

- **FIX 4.4 Protocol**: Industry-standard financial messaging
- **Message Types**: NewOrderSingle, OrderCancel, Heartbeat, and custom messages
- **Message Storage**: All messages stored in database with full audit trail
- **Status Tracking**: Track message lifecycle (PENDING, SENT, FAILED, ACKNOWLEDGED, REJECTED)
- **REST API**: Programmatic access for automation

## Quick Start

### Send a FIX Message via API

```bash
curl -X POST "http://localhost:8000/api/fix/messages" \
  -H "Content-Type: application/json" \
  -d '{
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
  }'
```

### Send a FIX Message via Python

```python
import requests

response = requests.post(
    "http://localhost:8000/api/fix/messages",
    json={
        "msg_type": "D",  # NewOrderSingle
        "sender_comp_id": "MYCLIENT",
        "target_comp_id": "BROKER",
        "cl_ord_id": "ORDER001",
        "symbol": "MSFT",
        "side": "1",  # Buy
        "order_qty": "100",
        "ord_type": "2",  # Limit
        "price": "300.00",
        "time_in_force": "0"  # Day
    }
)

message = response.json()
print(f"Message ID: {message['id']}")
print(f"Status: {message['status']}")
print(f"Raw FIX: {message['raw_message']}")
```

## FIX Message Types

### Common Message Types

| Code | Message Type | Description |
|------|-------------|-------------|
| D | NewOrderSingle | Submit a new order |
| F | OrderCancelRequest | Request to cancel an order |
| G | OrderCancelReplaceRequest | Modify an existing order |
| H | OrderStatusRequest | Request order status |
| 8 | ExecutionReport | Order execution report |
| 9 | OrderCancelReject | Order cancel rejection |
| 0 | Heartbeat | Connection heartbeat |
| A | Logon | Session logon |
| 5 | Logout | Session logout |

## Field Reference

### Standard Fields for NewOrderSingle (D)

| Field | Tag | Name | Values | Required |
|-------|-----|------|--------|----------|
| cl_ord_id | 11 | Client Order ID | String | Yes |
| symbol | 55 | Symbol | String (e.g., "AAPL") | Yes |
| side | 54 | Side | 1=Buy, 2=Sell | Yes |
| order_qty | 38 | Order Quantity | Integer | Yes |
| ord_type | 40 | Order Type | 1=Market, 2=Limit | Yes |
| price | 44 | Price | Decimal | For Limit orders |
| time_in_force | 59 | Time In Force | 0=Day, 1=GTC, 3=IOC | No |

### Side Codes

- `1` - Buy
- `2` - Sell
- `5` - Sell Short
- `6` - Sell Short Exempt

### Order Type Codes

- `1` - Market
- `2` - Limit
- `3` - Stop
- `4` - Stop Limit

### Time In Force Codes

- `0` - Day (Good for day)
- `1` - GTC (Good till cancel)
- `2` - OPG (At the opening)
- `3` - IOC (Immediate or cancel)
- `4` - FOK (Fill or kill)

## API Reference

### POST /api/fix/messages

Create and send a FIX message.

**Request Body:**
```json
{
  "msg_type": "string",
  "sender_comp_id": "string",
  "target_comp_id": "string",
  "cl_ord_id": "string",
  "symbol": "string",
  "side": "string",
  "order_qty": "string",
  "ord_type": "string",
  "price": "string",
  "time_in_force": "string",
  "session_id": "string",
  "fields": {
    "tag": "value"
  }
}
```

**Response:**
```json
{
  "id": 1,
  "msg_type": "D",
  "msg_seq_num": 1,
  "sender_comp_id": "SENDER",
  "target_comp_id": "TARGET",
  "message_data": "8=FIX.4.4...",
  "raw_message": "8=FIX.4.4...",
  "status": "SENT",
  "cl_ord_id": "ORDER123",
  "symbol": "AAPL",
  "side": "1",
  "order_qty": "100",
  "price": "150.50",
  "created_at": "2025-11-15T20:00:00",
  "sent_at": "2025-11-15T20:00:01"
}
```

### GET /api/fix/messages/{message_id}

Retrieve a specific FIX message by ID.

**Response:** Same as POST response

### GET /api/fix/messages

List FIX messages with optional filters.

**Query Parameters:**
- `skip` (int): Number of records to skip (default: 0)
- `limit` (int): Maximum records to return (default: 20, max: 100)
- `status` (string): Filter by status (PENDING, SENT, FAILED, etc.)
- `msg_type` (string): Filter by message type (D, F, etc.)
- `sender_comp_id` (string): Filter by sender
- `target_comp_id` (string): Filter by target
- `cl_ord_id` (string): Filter by client order ID

**Response:**
```json
{
  "items": [...],
  "total": 100,
  "page": 1,
  "page_size": 20
}
```

### DELETE /api/fix/messages/{message_id}

Delete a FIX message.

**Response:** 204 No Content

## Examples

### Market Order

```json
{
  "msg_type": "D",
  "sender_comp_id": "CLIENT",
  "target_comp_id": "BROKER",
  "cl_ord_id": "MKT001",
  "symbol": "TSLA",
  "side": "1",
  "order_qty": "50",
  "ord_type": "1",
  "time_in_force": "0"
}
```

### Limit Order

```json
{
  "msg_type": "D",
  "sender_comp_id": "CLIENT",
  "target_comp_id": "BROKER",
  "cl_ord_id": "LMT001",
  "symbol": "GOOGL",
  "side": "2",
  "order_qty": "25",
  "ord_type": "2",
  "price": "140.00",
  "time_in_force": "1"
}
```

### Order Cancel Request

```json
{
  "msg_type": "F",
  "sender_comp_id": "CLIENT",
  "target_comp_id": "BROKER",
  "cl_ord_id": "CANCEL001",
  "fields": {
    "41": "ORDER123",
    "11": "CANCEL001"
  }
}
```

### Heartbeat

```json
{
  "msg_type": "0",
  "sender_comp_id": "CLIENT",
  "target_comp_id": "BROKER"
}
```

## Message Status Lifecycle

```
PENDING → SENT → ACKNOWLEDGED
              ↓
            FAILED
              ↓
           REJECTED
```

- **PENDING**: Message created, not yet sent
- **SENT**: Message transmitted successfully
- **FAILED**: Message transmission failed
- **ACKNOWLEDGED**: Message acknowledged by counterparty
- **REJECTED**: Message rejected by counterparty

## Database Schema

### fix_messages Table

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| msg_type | VARCHAR(10) | FIX message type code |
| msg_seq_num | INTEGER | Message sequence number |
| sender_comp_id | VARCHAR(100) | Sender identifier |
| target_comp_id | VARCHAR(100) | Target identifier |
| message_data | TEXT | Full FIX message |
| raw_message | TEXT | Raw wire format |
| status | ENUM | Message status |
| response_message | TEXT | Response from counterparty |
| error_message | TEXT | Error details if failed |
| session_id | VARCHAR(255) | Optional session identifier |
| cl_ord_id | VARCHAR(255) | Client order ID |
| symbol | VARCHAR(50) | Trading symbol |
| side | VARCHAR(10) | Buy/Sell indicator |
| order_qty | VARCHAR(50) | Order quantity |
| price | VARCHAR(50) | Order price |
| created_at | DATETIME | Creation timestamp |
| sent_at | DATETIME | Send timestamp |
| acknowledged_at | DATETIME | Acknowledgment timestamp |

## Testing

Run FIX messaging tests:

```bash
pytest tests/test_fix_messaging.py -v
```

## Integration with Trading Systems

### Connecting to a FIX Server

The current implementation simulates message sending. To connect to a real FIX server, you would need to:

1. Configure FIX session parameters (in `FixSessionConfig`)
2. Establish TCP connection to broker's FIX gateway
3. Handle FIX session logon/logout
4. Implement message acknowledgment handling

Example session configuration:

```python
{
  "sender_comp_id": "YOUR_FIRM",
  "target_comp_id": "BROKER_FIRM",
  "host": "fix.broker.com",
  "port": 9876,
  "begin_string": "FIX.4.4",
  "heartbeat_interval": 30
}
```

## Best Practices

1. **Use Unique Client Order IDs**: Always use unique `cl_ord_id` values
2. **Validate Symbols**: Ensure trading symbols are valid before sending
3. **Handle Errors**: Check response status and handle failures
4. **Sequence Numbers**: Message sequence numbers are auto-incremented
5. **Session Management**: Implement proper logon/logout for production use
6. **Monitoring**: Regularly query message status for tracking

## Troubleshooting

### Message Status is FAILED

Check the `error_message` field:
```bash
curl http://localhost:8000/api/fix/messages/1
```

### Missing Required Fields

NewOrderSingle requires:
- `cl_ord_id`
- `symbol`
- `side`
- `order_qty`
- `ord_type`

### Invalid FIX Format

Ensure field values match FIX specifications:
- Side: "1" or "2"
- OrdType: "1" or "2"
- Prices and quantities: numeric strings

## Resources

- [FIX Protocol Official Site](https://www.fixtrading.org/)
- [FIX 4.4 Specification](https://www.fixtrading.org/standards/fix-4-4/)
- [SimpleFIX Documentation](https://github.com/da4089/simplefix)

## Module Architecture

```
app/modules/fix_messaging/
├── __init__.py          # Module exports
├── models.py            # Database models (FixMessage)
├── schemas.py           # Pydantic schemas (Request/Response)
└── service.py           # Business logic (FixMessagingService)

app/api/
└── fix_messaging.py     # REST API routes
```

## Next Steps

- Implement real FIX server connection
- Add execution report handling
- Support additional message types
- Add web UI for message management
- Implement session management
- Add message validation rules
