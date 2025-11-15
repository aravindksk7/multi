"""Pytest configuration and fixtures."""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from app.database import Base, get_db
from app.main import app


# Test database URL (using SQLite for tests)
TEST_DATABASE_URL = "sqlite:///./test.db"

# Create test engine
test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False}
)

# Create test session
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture(scope="function")
def db_session():
    """Create a fresh database for each test."""
    Base.metadata.create_all(bind=test_engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=test_engine)


@pytest.fixture(scope="function")
def client(db_session):
    """Create a test client with database override."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def sample_xml_baseline():
    """Sample baseline XML for testing."""
    return """<?xml version="1.0" encoding="UTF-8"?>
<testsuite name="Sample Suite" tests="3" failures="0" errors="0" time="5.123">
    <testcase name="test_login" classname="tests.TestAuth" time="1.234" status="pass">
        <result>PASSED</result>
    </testcase>
    <testcase name="test_logout" classname="tests.TestAuth" time="0.567" status="pass">
        <result>PASSED</result>
    </testcase>
    <testcase name="test_profile" classname="tests.TestUser" time="3.322" status="pass">
        <result>PASSED</result>
    </testcase>
</testsuite>"""


@pytest.fixture
def sample_xml_current_changed():
    """Sample current XML with changes."""
    return """<?xml version="1.0" encoding="UTF-8"?>
<testsuite name="Sample Suite" tests="3" failures="1" errors="0" time="6.456">
    <testcase name="test_login" classname="tests.TestAuth" time="1.500" status="pass">
        <result>PASSED</result>
    </testcase>
    <testcase name="test_logout" classname="tests.TestAuth" time="0.567" status="fail">
        <result>FAILED</result>
        <failure message="Logout failed">Session not cleared</failure>
    </testcase>
    <testcase name="test_profile" classname="tests.TestUser" time="4.389" status="pass">
        <result>PASSED</result>
    </testcase>
</testsuite>"""


@pytest.fixture
def sample_xml_current_added():
    """Sample current XML with added test case."""
    return """<?xml version="1.0" encoding="UTF-8"?>
<testsuite name="Sample Suite" tests="4" failures="0" errors="0" time="7.123">
    <testcase name="test_login" classname="tests.TestAuth" time="1.234" status="pass">
        <result>PASSED</result>
    </testcase>
    <testcase name="test_logout" classname="tests.TestAuth" time="0.567" status="pass">
        <result>PASSED</result>
    </testcase>
    <testcase name="test_profile" classname="tests.TestUser" time="3.322" status="pass">
        <result>PASSED</result>
    </testcase>
    <testcase name="test_new_feature" classname="tests.TestFeatures" time="2.000" status="pass">
        <result>PASSED</result>
    </testcase>
</testsuite>"""
