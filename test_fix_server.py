"""
Simple FIX Server for Testing

This is a minimal FIX server that listens for incoming messages
and prints them to console. Useful for testing the FIX messaging module.

Usage:
    python test_fix_server.py [port]

Default port is 9876.
"""
import socket
import sys
from datetime import datetime


def start_fix_server(port=9876):
    """Start a simple FIX server for testing."""
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    try:
        server_socket.bind(('0.0.0.0', port))
        server_socket.listen(5)
        print(f"🚀 FIX Test Server started on port {port}")
        print(f"📡 Listening for connections...")
        print(f"Press Ctrl+C to stop\n")
        
        while True:
            client_socket, address = server_socket.accept()
            print(f"\n{'='*60}")
            print(f"📥 Connection from {address[0]}:{address[1]}")
            print(f"🕐 Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
            try:
                data = client_socket.recv(4096)
                if data:
                    print(f"\n📨 Received FIX Message:")
                    print("-" * 60)
                    
                    # Try to decode as latin-1 (FIX standard encoding)
                    message = data.decode('latin-1')
                    
                    # Print raw message
                    print(f"Raw: {repr(message)}")
                    
                    # Try to parse FIX tags
                    print("\n🏷️  Parsed FIX Tags:")
                    tags = message.split('\x01')
                    for tag in tags:
                        if '=' in tag:
                            tag_num, tag_value = tag.split('=', 1)
                            tag_name = get_tag_name(tag_num)
                            print(f"  {tag_num:>3} ({tag_name:20}) = {tag_value}")
                    
                    # Send a simple acknowledgment (optional)
                    # ack = "8=FIX.4.4\x019=50\x0135=8\x0149=SERVER\x0156=CLIENT\x0134=1\x0110=000\x01"
                    # client_socket.sendall(ack.encode('latin-1'))
                    # print("\n✅ Sent acknowledgment")
                    
            except Exception as e:
                print(f"❌ Error processing message: {e}")
            finally:
                client_socket.close()
                print(f"\n🔌 Connection closed")
                print("="*60)
                
    except KeyboardInterrupt:
        print("\n\n⏹️  Server stopped by user")
    except Exception as e:
        print(f"❌ Server error: {e}")
    finally:
        server_socket.close()


def get_tag_name(tag_num):
    """Get human-readable name for common FIX tags."""
    tag_names = {
        '8': 'BeginString',
        '9': 'BodyLength',
        '10': 'CheckSum',
        '11': 'ClOrdID',
        '34': 'MsgSeqNum',
        '35': 'MsgType',
        '38': 'OrderQty',
        '40': 'OrdType',
        '44': 'Price',
        '49': 'SenderCompID',
        '52': 'SendingTime',
        '54': 'Side',
        '55': 'Symbol',
        '56': 'TargetCompID',
        '59': 'TimeInForce',
        '60': 'TransactTime',
    }
    return tag_names.get(tag_num, 'Unknown')


if __name__ == '__main__':
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 9876
    start_fix_server(port)
