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
            "name": "Chrome Desktop Profile",
            "device_type": "desktop",
            "window_width": 1920,
            "window_height": 1080,
            "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "country": "us",
            "custom_headers": [
                {"name": "Accept-Language", "value": "en-US,en;q=0.9"}
            ],
            "extras": {"browser": "chrome"}
        },
        version="Chrome 120"
    )
    db_session.add(template)
    db_session.commit()
    db_session.refresh(template)
    return template


@pytest.fixture
def test_templates(db_session):
    """Create multiple test templates."""
    templates = [
        Template(
            name="Chrome Desktop (Latest)",
            description="Latest Chrome browser on Windows desktop",
            version="Chrome 120",
            data={
                "name": "Chrome Desktop Profile",
                "device_type": "desktop",
                "window_width": 1920,
                "window_height": 1080,
                "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "country": "us",
                "custom_headers": [
                    {"name": "Accept-Language", "value": "en-US,en;q=0.9"},
                    {"name": "Accept-Encoding", "value": "gzip, deflate, br"},
                    {"name": "Accept", "value": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"}
                ],
                "extras": {
                    "browser": "chrome",
                    "os": "windows",
                    "version": "120.0.0.0"
                }
            }
        ),
        Template(
            name="Safari Mobile (iOS 17)",
            description="Safari browser on iPhone with iOS 17",
            version="iOS 17",
            data={
                "name": "Safari Mobile Profile",
                "device_type": "mobile",
                "window_width": 375,
                "window_height": 667,
                "user_agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",
                "country": "us",
                "custom_headers": [
                    {"name": "Accept-Language", "value": "en-US,en;q=0.9"},
                    {"name": "Accept-Encoding", "value": "gzip, deflate, br"},
                    {"name": "Accept", "value": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"}
                ],
                "extras": {
                    "browser": "safari",
                    "os": "ios",
                    "version": "17.0",
                    "device": "iphone"
                }
            }
        ),
        Template(
            name="Firefox Desktop (Latest)",
            description="Latest Firefox browser on Linux desktop",
            version="Firefox 121",
            data={
                "name": "Firefox Desktop Profile",
                "device_type": "desktop",
                "window_width": 1920,
                "window_height": 1080,
                "user_agent": "Mozilla/5.0 (X11; Linux x86_64; rv:121.0) Gecko/20100101 Firefox/121.0",
                "country": "us",
                "custom_headers": [
                    {"name": "Accept-Language", "value": "en-US,en;q=0.5"},
                    {"name": "Accept-Encoding", "value": "gzip, deflate, br"},
                    {"name": "Accept", "value": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8"}
                ],
                "extras": {
                    "browser": "firefox",
                    "os": "linux",
                    "version": "121.0"
                }
            }
        )
    ]
    
    for template in templates:
        db_session.add(template)
    db_session.commit()
    
    for template in templates:
        db_session.refresh(template)
    
    return templates
