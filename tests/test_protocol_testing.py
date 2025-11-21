"""
Tests for OUCH/ITCH protocol testing module
"""
import pytest
from datetime import datetime
from sqlalchemy.orm import Session

from app.modules.protocol_testing import (
    ProtocolTestingService,
    ProtocolType,
    MessageDirection,
    TestStatus,
    SessionStatus
)


class TestProtocolTesting:
    """Test suite for protocol testing functionality"""

    def test_create_ouch_session(self, db_session: Session):
        """Test creating an OUCH session"""
        service = ProtocolTestingService(db_session)
        
        session = service.create_session(
            protocol_type=ProtocolType.OUCH,
            host="ouch.test.nasdaq.com",
            port=12345,
            username="testuser",
            password="testpass",
            session_id="TEST001"
        )
        
        assert session.id is not None
        assert session.protocol_type == ProtocolType.OUCH
        assert session.host == "ouch.test.nasdaq.com"
        assert session.port == 12345
        assert session.username == "testuser"
        assert session.status == SessionStatus.CREATED

    def test_create_itch_session(self, db_session: Session):
        """Test creating an ITCH session"""
        service = ProtocolTestingService(db_session)
        
        session = service.create_session(
            protocol_type=ProtocolType.ITCH,
            host="itch.test.nasdaq.com",
            port=54321,
            username="itchuser",
            password="itchpass"
        )
        
        assert session.id is not None
        assert session.protocol_type == ProtocolType.ITCH
        assert session.status == SessionStatus.CREATED

    def test_create_protocol_test(self, db_session: Session):
        """Test creating a protocol test"""
        service = ProtocolTestingService(db_session)
        
        test = service.create_test(
            test_name="Test Enter Order",
            protocol_type=ProtocolType.OUCH,
            test_description="Test OUCH Enter Order message",
            test_config={"order_quantity": 100}
        )
        
        assert test.id is not None
        assert test.test_name == "Test Enter Order"
        assert test.protocol_type == ProtocolType.OUCH
        assert test.status == TestStatus.CREATED
        assert test.messages_sent == 0
        assert test.messages_received == 0

    def test_create_ouch_message(self, db_session: Session):
        """Test creating an OUCH message"""
        service = ProtocolTestingService(db_session)
        
        message = service.create_message(
            protocol_type=ProtocolType.OUCH,
            message_type="EnterOrder",
            message_indicator=65,  # 'A' in ASCII
            direction=MessageDirection.INCOMING,
            fields={
                "orderToken": "ORDER001",
                "orderBookId": 12345,
                "side": "B",
                "quantity": 100,
                "price": 5000
            }
        )
        
        assert message.id is not None
        assert message.protocol_type == ProtocolType.OUCH
        assert message.message_type == "EnterOrder"
        assert message.direction == MessageDirection.INCOMING
        assert message.message_data["quantity"] == 100
        assert message.is_valid == 1  # SQLite boolean

    def test_create_itch_message(self, db_session: Session):
        """Test creating an ITCH message"""
        service = ProtocolTestingService(db_session)
        
        message = service.create_message(
            protocol_type=ProtocolType.ITCH,
            message_type="SystemEvent",
            message_indicator=83,  # 'S' in ASCII
            direction=MessageDirection.OUTGOING,
            fields={
                "stockLocate": 1,
                "trackingNumber": 0,
                "timestamp": 123456789,
                "eventCode": "O"
            }
        )
        
        assert message.id is not None
        assert message.protocol_type == ProtocolType.ITCH
        assert message.message_type == "SystemEvent"
        assert message.direction == MessageDirection.OUTGOING

    def test_get_test(self, db_session: Session):
        """Test retrieving a protocol test"""
        service = ProtocolTestingService(db_session)
        
        # Create test
        test = service.create_test(
            test_name="Test Retrieval",
            protocol_type=ProtocolType.OUCH
        )
        
        # Retrieve test
        retrieved = service.get_test(test.id)
        
        assert retrieved is not None
        assert retrieved.id == test.id
        assert retrieved.test_name == "Test Retrieval"

    def test_list_tests(self, db_session: Session):
        """Test listing protocol tests"""
        service = ProtocolTestingService(db_session)
        
        # Create multiple tests
        service.create_test("OUCH Test 1", ProtocolType.OUCH)
        service.create_test("OUCH Test 2", ProtocolType.OUCH)
        service.create_test("ITCH Test 1", ProtocolType.ITCH)
        
        # List all tests
        tests, total = service.list_tests()
        assert total >= 3
        
        # Filter by protocol type
        ouch_tests, ouch_total = service.list_tests(protocol_type=ProtocolType.OUCH)
        assert ouch_total >= 2
        
        itch_tests, itch_total = service.list_tests(protocol_type=ProtocolType.ITCH)
        assert itch_total >= 1

    def test_delete_test(self, db_session: Session):
        """Test deleting a protocol test"""
        service = ProtocolTestingService(db_session)
        
        # Create test
        test = service.create_test("Test to Delete", ProtocolType.OUCH)
        test_id = test.id
        
        # Delete test
        deleted = service.delete_test(test_id)
        assert deleted is True
        
        # Verify deletion
        retrieved = service.get_test(test_id)
        assert retrieved is None

    def test_test_with_session(self, db_session: Session):
        """Test creating a test with associated session"""
        service = ProtocolTestingService(db_session)
        
        # Create session
        session = service.create_session(
            protocol_type=ProtocolType.OUCH,
            host="test.com",
            port=1234,
            username="user",
            password="pass"
        )
        
        # Create test with session
        test = service.create_test(
            test_name="Test with Session",
            protocol_type=ProtocolType.OUCH,
            session_id=session.id
        )
        
        assert test.session_id == session.id
        assert test.session.host == "test.com"

    def test_message_validation(self, db_session: Session):
        """Test message validation"""
        service = ProtocolTestingService(db_session)
        
        # Valid message
        valid_msg = service.create_message(
            protocol_type=ProtocolType.OUCH,
            message_type="EnterOrder",
            message_indicator=65,
            direction=MessageDirection.INCOMING,
            fields={"orderToken": "ORDER001"}
        )
        assert valid_msg.is_valid == 1  # SQLite boolean


@pytest.fixture
def db_session():
    """Create a test database session"""
    from app.database import SessionLocal, Base, engine
    
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    # Create session
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)
