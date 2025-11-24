# FIX Protocol Messaging - Server Endpoint Integration

## Overview

The FIX Protocol Messaging Module has been enhanced to send messages directly to FIX server endpoints via TCP socket connections. This enables real-time communication with FIX trading servers and gateways.

## Features

### 1. Direct Server Communication
- **TCP Socket Connection**: Messages are sent via TCP sockets to specified FIX server endpoints
- **Configurable Endpoints**: Specify host and port for each message or configure session defaults
- **Connection Timeout**: 10-second timeout prevents hanging on unreachable servers
- **Error Handling**: Comprehensive error messages for connection failures

### 2. Message Status Tracking
Messages are tracked with the following statuses:
- **PENDING**: Message created but not yet sent
- **SENT**: Successfully delivered to FIX server
- **ACKNOWLEDGED**: Server acknowledged receipt (if response received)
- **FAILED**: Connection or send failure

### 3. Session Configuration
Pre-configure FIX session parameters for reuse:
```json
{
  "sender_comp_id": "CLIENT1",
  "target_comp_id": "BROKER1",
  "host": "fix.example.com",
  "port": 9876,
  "begin_string": "FIX.4.4",
  "heartbeat_interval": 30
}
```

## API Usage

### Configure a Session
```bash
POST /api/fix/sessions/{session_id}/config
Content-Type: application/json

{
  "sender_comp_id": "CLIENT1",
  "target_comp_id": "BROKER1",
  "host": "fix.example.com",
  "port": 9876,
  "begin_string": "FIX.4.4",
  "heartbeat_interval": 30
}
```

### Send a Message
```bash
POST /api/fix/messages?host=localhost&port=9876
Content-Type: application/json

{
  "msg_type": "D",
  "sender_comp_id": "CLIENT1",
  "target_comp_id": "BROKER1",
  "cl_ord_id": "ORDER123",
  "symbol": "AAPL",
  "side": "1",
  "order_qty": "100",
  "ord_type": "2",
  "price": "150.50",
  "time_in_force": "0"
}
```

Query Parameters:
- `host` (optional): Override FIX server host (default: localhost)
- `port` (optional): Override FIX server port (default: 9876)

## Web Interface

The updated web form includes:
- **FIX Server Host**: Hostname or IP address field
- **Port**: TCP port number field
- **Session ID**: Optional session identifier for tracking

Default values:
- Host: `localhost`
- Port: `9876`

## Testing

### Start Test FIX Server
A test server is provided for local testing:

```bash
python test_fix_server.py [port]
```

This starts a simple FIX server that:
- Listens for incoming connections
- Prints received messages with parsed FIX tags
- Shows connection details and timestamps

### Send Test Messages
1. Start the test server in one terminal:
   ```bash
   python test_fix_server.py 9876
   ```

2. Start the application in another terminal:
   ```bash
   uvicorn app.main:app --reload
   ```

3. Navigate to http://localhost:8000/fix/send and submit a message

4. View the message in the test server console

## Connection Details

### Socket Configuration
- **Protocol**: TCP
- **Encoding**: latin-1 (FIX standard)
- **Timeout**: 10 seconds for connection
- **Response Timeout**: 2 seconds (optional)

### Error Scenarios
| Error | Status | Error Message |
|-------|--------|---------------|
| Connection Refused | FAILED | "Connection refused by host:port" |
| Connection Timeout | FAILED | "Connection timeout to host:port" |
| DNS Resolution Failure | FAILED | "DNS resolution failed for host" |
| Socket Error | FAILED | "Failed to send message: [details]" |

## Code Structure

### Service Layer
**File**: `app/modules/fix_messaging/service.py`

Key methods:
- `configure_session()`: Store session configuration
- `_send_to_fix_server()`: Send message via TCP socket
- `create_fix_message()`: Build and send FIX message

### API Layer
**File**: `app/api/fix_messaging.py`

Endpoints:
- `POST /api/fix/sessions/{session_id}/config`: Configure session
- `POST /api/fix/messages`: Send message with optional host/port

### Web Routes
**File**: `app/api/web.py`

Routes:
- `GET /fix/send`: Display form
- `POST /fix/send`: Process form submission with host/port

## Example Workflow

1. **Configure Session** (optional):
   ```python
   import requests
   
   config = {
       "sender_comp_id": "CLIENT1",
       "target_comp_id": "BROKER1",
       "host": "fix.example.com",
       "port": 9876
   }
   
   response = requests.post(
       "http://localhost:8000/api/fix/sessions/SESSION_001/config",
       json=config
   )
   ```

2. **Send Message**:
   ```python
   message = {
       "msg_type": "D",
       "sender_comp_id": "CLIENT1",
       "target_comp_id": "BROKER1",
       "cl_ord_id": "ORD001",
       "symbol": "AAPL",
       "side": "1",
       "order_qty": "100",
       "ord_type": "2",
       "price": "150.50",
       "session_id": "SESSION_001"
   }
   
   response = requests.post(
       "http://localhost:8000/api/fix/messages",
       json=message
   )
   ```

3. **Check Status**:
   ```python
   message_id = response.json()["id"]
   status = requests.get(f"http://localhost:8000/api/fix/messages/{message_id}")
   print(status.json()["status"])  # SENT, FAILED, etc.
   ```

## Integration with Trading Systems

For production use:
1. Configure your FIX server's host and port
2. Ensure network connectivity (firewall rules, security groups)
3. Use session configuration for consistent settings
4. Monitor message status for failures
5. Implement retry logic for failed messages
6. Handle acknowledgments and responses appropriately

## Security Considerations

- **Network Security**: Ensure secure network connections (VPN, private network)
- **Authentication**: Implement FIX logon sequence with credentials
- **Encryption**: Consider TLS/SSL for encrypted connections
- **Access Control**: Restrict who can send messages
- **Audit Logging**: All messages are logged in the database

## Troubleshooting

### Connection Refused
- Verify FIX server is running
- Check host and port are correct
- Verify firewall allows connections

### Connection Timeout
- Increase timeout if needed (modify `socket_timeout` in service)
- Check network connectivity
- Verify no network blocks (proxies, firewalls)

### DNS Resolution Failed
- Verify hostname is correct
- Use IP address instead of hostname
- Check DNS server configuration

## Future Enhancements

Potential improvements:
- Session persistence (maintain connection)
- Heartbeat management
- Sequence number tracking
- Message acknowledgment handling
- Async/concurrent message sending
- TLS/SSL encryption support
- Connection pooling
- Automatic reconnection
