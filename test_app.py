"""Test script to verify the application endpoints"""
import requests
import time
import json

BASE_URL = "http://127.0.0.1:8000"

def test_homepage():
    """Test the main homepage"""
    try:
        response = requests.get(f"{BASE_URL}/")
        print(f"✓ Homepage: HTTP {response.status_code}")
        assert "Test Tool Platform" in response.text
        print("  - Found 'Test Tool Platform' in content")
        return True
    except Exception as e:
        print(f"✗ Homepage failed: {e}")
        return False

def test_fix_home():
    """Test FIX module homepage"""
    try:
        response = requests.get(f"{BASE_URL}/fix")
        print(f"✓ FIX Home: HTTP {response.status_code}")
        assert "FIX Protocol Messaging" in response.text
        print("  - Found 'FIX Protocol Messaging' in content")
        return True
    except Exception as e:
        print(f"✗ FIX Home failed: {e}")
        return False

def test_fix_send_form():
    """Test FIX send message form"""
    try:
        response = requests.get(f"{BASE_URL}/fix/send")
        print(f"✓ FIX Send Form: HTTP {response.status_code}")
        assert "Send FIX Message" in response.text
        print("  - Found 'Send FIX Message' form")
        return True
    except Exception as e:
        print(f"✗ FIX Send Form failed: {e}")
        return False

def test_api_fix_send():
    """Test FIX API endpoint for sending a message"""
    try:
        payload = {
            "msg_type": "D",
            "sender_comp_id": "TEST_CLIENT",
            "target_comp_id": "TEST_BROKER",
            "cl_ord_id": "TEST-001",
            "symbol": "AAPL",
            "side": "1",
            "order_qty": "100",
            "ord_type": "2",
            "price": "150.50",
            "time_in_force": "0"
        }
        response = requests.post(f"{BASE_URL}/api/fix/messages", json=payload)
        print(f"✓ FIX API Send: HTTP {response.status_code}")
        if response.status_code != 201:
            print(f"  - Error: {response.text}")
            return None
        data = response.json()
        print(f"  - Created message ID: {data['id']}")
        print(f"  - Status: {data['status']}")
        return data['id']
    except Exception as e:
        print(f"✗ FIX API Send failed: {e}")
        return None

def test_api_fix_get(message_id):
    """Test FIX API endpoint for getting a message"""
    try:
        response = requests.get(f"{BASE_URL}/api/fix/messages/{message_id}")
        print(f"✓ FIX API Get: HTTP {response.status_code}")
        data = response.json()
        print(f"  - Message type: {data['msg_type']}")
        print(f"  - Symbol: {data['symbol']}")
        return True
    except Exception as e:
        print(f"✗ FIX API Get failed: {e}")
        return False

def test_api_fix_list():
    """Test FIX API endpoint for listing messages"""
    try:
        response = requests.get(f"{BASE_URL}/api/fix/messages")
        print(f"✓ FIX API List: HTTP {response.status_code}")
        data = response.json()
        print(f"  - Total messages: {data['total']}")
        print(f"  - Messages in page: {len(data['items'])}")
        return True
    except Exception as e:
        print(f"✗ FIX API List failed: {e}")
        return False

def test_xml_compare_page():
    """Test XML comparison page"""
    try:
        response = requests.get(f"{BASE_URL}/compare/new")
        print(f"✓ XML Compare Page: HTTP {response.status_code}")
        assert "New XML Comparison" in response.text
        print("  - Found XML comparison form")
        return True
    except Exception as e:
        print(f"✗ XML Compare Page failed: {e}")
        return False

def test_api_docs():
    """Test API documentation"""
    try:
        response = requests.get(f"{BASE_URL}/api/docs")
        print(f"✓ API Docs: HTTP {response.status_code}")
        print("  - Swagger UI accessible")
        return True
    except Exception as e:
        print(f"✗ API Docs failed: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("Testing Modular Application")
    print("=" * 60)
    print()
    
    # Wait for server to be ready
    print("Waiting for server to start...")
    time.sleep(2)
    
    results = []
    
    print("\n--- Web UI Tests ---")
    results.append(("Homepage", test_homepage()))
    results.append(("XML Compare Page", test_xml_compare_page()))
    results.append(("FIX Home", test_fix_home()))
    results.append(("FIX Send Form", test_fix_send_form()))
    
    print("\n--- API Tests ---")
    results.append(("API Docs", test_api_docs()))
    message_id = test_api_fix_send()
    results.append(("FIX API Send", message_id is not None))
    
    if message_id:
        results.append(("FIX API Get", test_api_fix_get(message_id)))
    
    results.append(("FIX API List", test_api_fix_list()))
    
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    passed = sum(1 for _, result in results if result)
    total = len(results)
    print(f"Passed: {passed}/{total}")
    print(f"Failed: {total - passed}/{total}")
    
    if passed == total:
        print("\n✓ All tests passed!")
    else:
        print("\n✗ Some tests failed")
        for name, result in results:
            if not result:
                print(f"  - {name}")
