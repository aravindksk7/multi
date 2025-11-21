# OUCH/ITCH Protocol Testing Guide

## Overview

The OUCH/ITCH Protocol Testing module provides comprehensive testing capabilities for NASDAQ financial protocols:

- **OUCH (Order Entry Protocol)**: Bidirectional message-based protocol for order entry, modification, and execution
- **ITCH (Market Data Protocol)**: Unidirectional feed protocol for real-time market data consumption

Both protocols operate over **SoupBinTCP** sessions, which provide reliable message delivery with heartbeat monitoring and sequence number management.

## Features

### Protocol Support
- ✅ OUCH protocol message creation and validation
- ✅ ITCH protocol message reception and parsing
- ✅ SoupBinTCP session management
- ✅ Heartbeat monitoring (client and server)
- ✅ Sequence number tracking
- ✅ Protocol conformance testing

### Testing Capabilities
- Create and manage protocol test scenarios
- Send OUCH messages (order entry, cancel, replace)
- Receive and validate ITCH messages (market data)
- Track message history and validation results
- Generate test reports with detailed metrics

## Quick Start

### 1. Install Dependencies

The module requires the `nasdaq-protocols` library:

```bash
pip install nasdaq-protocols>=1.1.4
```

### 2. Run Database Migration

Apply the database migration to create protocol testing tables:

```bash
alembic upgrade head
```

This creates:
- `protocol_sessions` - SoupBinTCP session information
- `protocol_tests` - Test definitions and results
- `protocol_messages` - Message history and validation

### 3. Access the Module

Navigate to: **http://localhost:8000/protocols/**

## Usage Guide

### Creating a Protocol Test

#### Web UI

1. Go to `/protocols/test/create`
2. Fill in the test configuration:
   - **Test Name**: Descriptive name for the test
   - **Protocol Type**: Select OUCH or ITCH
   - **Test Description**: Optional description
3. Configure the session:
   - **Server Host**: Protocol server hostname/IP
   - **Server Port**: Protocol server port
   - **Username**: SoupBinTCP username (max 6 characters)
   - **Password**: SoupBinTCP password (max 10 characters)
   - **Session ID**: Optional session identifier
4. Click **Create Test**

#### REST API

```bash
curl -X POST "http://localhost:8000/protocols/test" \
  -H "Content-Type: application/json" \
  -d '{
    "test_name": "OUCH Enter Order Test",
    "protocol_type": "OUCH",
    "test_description": "Test order entry functionality",
    "host": "ouch.test.nasdaq.com",
    "port": 12345,
    "username": "testuser",
    "password": "testpass"
  }'
```

### Creating Protocol Messages

#### OUCH Messages (Order Entry)

Example: **Enter Order**

```python
{
  "protocol_type": "OUCH",
  "message_type": "EnterOrder",
  "message_indicator": 65,  # 'A' in ASCII
  "direction": "incoming",
  "fields": {
    "orderToken": "ORDER12345",
    "orderBookId": 1001,
    "side": "B",  # Buy
    "quantity": 100,
    "price": 5000,  # Price in cents
    "timeInForce": 0,  # Day order
    "firm": "TEST"
  },
  "session_id": 1,
  "test_id": 1
}
```

Example: **Cancel Order**

```python
{
  "protocol_type": "OUCH",
  "message_type": "CancelOrder",
  "message_indicator": 88,  # 'X' in ASCII
  "direction": "incoming",
  "fields": {
    "orderToken": "ORDER12345",
    "quantity": 100
  },
  "session_id": 1,
  "test_id": 1
}
```

#### ITCH Messages (Market Data)

Example: **System Event** (receive only)

```python
{
  "protocol_type": "ITCH",
  "message_type": "SystemEvent",
  "message_indicator": 83,  # 'S' in ASCII
  "direction": "outgoing",
  "fields": {
    "stockLocate": 1,
    "trackingNumber": 0,
    "timestamp": 123456789,
    "eventCode": "O"  # Start of Messages
  },
  "session_id": 2,
  "test_id": 2
}
```

### Managing Sessions

#### Create Session

```bash
curl -X POST "http://localhost:8000/protocols/session" \
  -H "Content-Type: application/json" \
  -d '{
    "protocol_type": "OUCH",
    "host": "ouch.test.nasdaq.com",
    "port": 12345,
    "username": "testuser",
    "password": "testpass",
    "sequence_number": 1,
    "client_heartbeat_interval": 10,
    "server_heartbeat_interval": 10
  }'
```

#### Connect Session

```bash
curl -X POST "http://localhost:8000/protocols/session/{session_id}/connect"
```

### Executing Tests

```bash
curl -X POST "http://localhost:8000/protocols/test/{test_id}/execute" \
  -H "Content-Type: application/json" \
  -d '{
    "test_id": 1,
    "timeout_seconds": 60
  }'
```

## API Reference

### Endpoints

#### Tests
- `POST /protocols/test` - Create a protocol test
- `GET /protocols/test/{test_id}` - Get test details
- `GET /protocols/tests/list` - List all tests
- `POST /protocols/test/{test_id}/execute` - Execute a test
- `DELETE /protocols/test/{test_id}` - Delete a test

#### Sessions
- `POST /protocols/session` - Create a protocol session
- `POST /protocols/session/{session_id}/connect` - Connect to server

#### Messages
- `POST /protocols/message` - Create a message
- `POST /protocols/message/{message_id}/send` - Send a message

#### Web UI
- `GET /protocols/` - Protocol testing home
- `GET /protocols/test/create` - Create test form
- `GET /protocols/tests` - List tests page
- `GET /protocols/test/{test_id}` - Test detail page

## Protocol Specifications

### OUCH Protocol

**Common OUCH Message Types:**

| Message Type | Indicator | Direction | Description |
|-------------|-----------|-----------|-------------|
| EnterOrder | 65 ('A') | Incoming | Submit a new order |
| ReplaceOrder | 85 ('U') | Incoming | Replace an existing order |
| CancelOrder | 88 ('X') | Incoming | Cancel an order |
| OrderAccepted | 65 ('A') | Outgoing | Order accepted by system |
| OrderRejected | 74 ('J') | Outgoing | Order rejected |
| OrderExecuted | 69 ('E') | Outgoing | Order execution report |
| OrderCanceled | 67 ('C') | Outgoing | Order canceled confirmation |

### ITCH Protocol

**Common ITCH Message Types:**

| Message Type | Indicator | Direction | Description |
|-------------|-----------|-----------|-------------|
| SystemEvent | 83 ('S') | Outgoing | System event notification |
| StockDirectory | 82 ('R') | Outgoing | Stock trading information |
| StockTradingAction | 72 ('H') | Outgoing | Trading status change |
| AddOrder | 65 ('A') | Outgoing | New order added to book |
| OrderExecuted | 69 ('E') | Outgoing | Order execution |
| OrderCancel | 88 ('X') | Outgoing | Order cancellation |
| Trade | 80 ('P') | Outgoing | Non-displayed trade |

## Advanced Configuration

### Custom Message Definitions

To use custom OUCH/ITCH messages:

1. Create message specification XML file
2. Use `nasdaq-protocols` codegen to generate Python classes
3. Import generated classes in your test code

Example XML specification:

```xml
<root>
    <messages-root>
        <message id="CustomOrder" message-id="99" direction="incoming">
            <fields>
                <field name="orderToken" type="str_ascii_n" length="14"/>
                <field name="quantity" type="int_4_be"/>
                <field name="price" type="int_8_be"/>
            </fields>
        </message>
    </messages-root>
</root>
```

Generate classes:

```bash
nasdaq-protocols-ouch-codegen \
  --spec-file custom_messages.xml \
  --app-name myapp \
  --op-dir output/
```

### SoupBinTCP Configuration

**Heartbeat Settings:**
- `client_heartbeat_interval`: How often client sends heartbeats (seconds)
- `server_heartbeat_interval`: Maximum time to wait for server heartbeat (seconds)

**Sequence Numbers:**
- Set `sequence_number=0` to receive from HEAD (latest)
- Set `sequence_number=1` to receive from START (beginning)
- Set `sequence_number=N` to receive from specific sequence

## Troubleshooting

### Connection Issues

**Problem**: Session fails to connect

**Solutions**:
1. Verify host and port are correct
2. Check username/password credentials
3. Ensure firewall allows connection
4. Verify SoupBinTCP server is running

### Message Validation Errors

**Problem**: Message marked as invalid

**Solutions**:
1. Check message field types match specification
2. Verify all required fields are present
3. Ensure field values are within valid ranges
4. Review validation_errors in message details

### Sequence Number Mismatches

**Problem**: Sequence number errors

**Solutions**:
1. Start from correct sequence number
2. Check for missing messages
3. Verify session wasn't reset on server
4. Monitor sequence_number field in session

## Best Practices

1. **Use Descriptive Test Names**: Include protocol type and scenario
2. **Configure Realistic Heartbeats**: Match production settings
3. **Start from Known Sequence**: Use sequence=1 for testing
4. **Validate Messages Before Sending**: Check fields and types
5. **Monitor Session Status**: Track connected/disconnected states
6. **Review Test Results**: Check result_summary for issues

## References

- [NASDAQ Protocols GitHub](https://github.com/Nasdaq/nasdaq-protocols)
- [OUCH Specification](https://www.nasdaqtrader.com/content/technicalsupport/specifications/tradingproducts/ouch4.2.pdf)
- [ITCH Specification](https://www.nasdaqtrader.com/content/technicalsupport/specifications/dataproducts/NQTVITCHspecification.pdf)
- [SoupBinTCP Specification](https://www.nasdaqtrader.com/content/technicalsupport/specifications/dataproducts/soupbintcp.pdf)

## Support

For issues or questions:
- Check the API documentation: `/api/docs`
- Review test results for detailed error messages
- Examine protocol_messages table for message history
- Consult NASDAQ protocol specifications
