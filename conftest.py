"""
Pytest configuration and shared fixtures.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

from app.main import app
from app.db import Base, get_db
from app.models.user import User
from app.models.api_key import APIKey
from app.models.device_profile import DeviceProfile
from app.models.template import Template
from app.repositories.user import UserRepository


# Test database setup - SQLite
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    """Set up the test database before running tests."""
    # Create all tables
    Base.metadata.create_all(bind=engine)
    yield
    # Clean up after all tests
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def db_session():
    """Create a fresh database session for each test."""
    # Clean up all data before each test using a separate connection
    try:
        with engine.connect() as cleanup_conn:
            cleanup_conn.execute(text("DELETE FROM api_keys"))
            cleanup_conn.execute(text("DELETE FROM profiles"))
            cleanup_conn.execute(text("DELETE FROM templates"))
            cleanup_conn.execute(text("DELETE FROM users"))
            cleanup_conn.commit()
    except Exception:
        pass  # Ignore cleanup errors
    
    # Create fresh session for test
    session = TestingSessionLocal()
    
    try:
        yield session
    finally:
        session.close()


@pytest.fixture(scope="function")
def client(db_session):
    """Create a test client with database dependency override."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    
    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        app.dependency_overrides.clear()


@pytest.fixture
def test_user(db_session):
    """Create a test user."""
    user = User(
        email="test@example.com"
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def test_api_key(test_user, db_session):
    """Create a test API key for the test user."""
    import hashlib
    from app.settings import settings
    
    # Generate raw key
    raw_key = "test-api-key-12345"
    key_hash = hashlib.sha256(f"{raw_key}{settings.api_key_pepper}".encode()).hexdigest()
    
    api_key = APIKey(
        owner_id=test_user.id,
        key_hash=key_hash
    )
    db_session.add(api_key)
    db_session.commit()
    db_session.refresh(api_key)
    
    return api_key, raw_key


@pytest.fixture
def authenticated_headers(test_api_key):
    """Get authentication headers for API requests."""
    _, raw_key = test_api_key
    return {"Authorization": f"Bearer {raw_key}"}


@pytest.fixture
def sample_device_profile_data():
    """Sample device profile data for testing."""
    return {
        "name": "Test Profile",
        "device_type": "desktop",
        "window_width": 1920,
        "window_height": 1080,
        "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "country": "us",
        "custom_headers": [
            {"name": "Accept-Language", "value": "en-US,en;q=0.9"}
        ],
        "extras": {}
    }


@pytest.fixture
def test_template(db_session):
    """Create a test template."""
    template = Template(
        name="Chrome Desktop",
        description="Latest Chrome on Windows",
        data={
            "device_type": "desktop",
            "window_width": 1920,
            "window_height": 1080,
            "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "country": "us",
            "custom_headers": [],
            "extras": {}
        },
        version="Chrome 120"
    )
    db_session.add(template)
    db_session.commit()
    db_session.refresh(template)
    return template
