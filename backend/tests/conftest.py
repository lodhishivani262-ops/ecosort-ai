"""EcoSort AI - Pytest Test Configuration and Fixtures (Stage 5)."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.config import settings
from app.core.rate_limit import limiter
from app.db.base import Base
from app.db.database import get_db
from app.main import app
from app.services.ai_service import MockAIService, get_ai_service

# Minimal valid JPEG file (1x1 pixel image with proper JPEG magic bytes)
VALID_JPEG_BYTES = (
    b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00H\x00H\x00\x00"
    b"\xff\xdb\x00C\x00\x08\x06\x06\x07\x06\x05\x08\x07\x07\x07\t\t\x08"
    b"\n\x0c\x14\r\x0c\x0b\x0b\x0c\x19\x12\x13\x0f\x14\x1d\x1a\x1f\x1e"
    b"\x1d\x1a\x1c\x1c $.' \",#\x1c\x1c(7),01444\x1f'9=82<.342\xff\xc0"
    b"\x00\x0b\x08\x00\x01\x00\x01\x01\x01\x11\x00\xff\xc4\x00\x1f\x00"
    b"\x00\x01\x05\x01\x01\x01\x01\x01\x01\x00\x00\x00\x00\x00\x00\x00"
    b"\x00\x01\x02\x03\x04\x05\x06\x07\x08\t\n\x0b\xff\xda\x00\x08\x01"
    b"\x01\x00\x00?\x00\xbf\x00\xff\xd9"
)

# Minimal valid PNG file (1x1 pixel PNG)
VALID_PNG_BYTES = (
    b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01"
    b"\x08\x06\x00\x00\x00\x1f\x15c4\x00\x00\x00\nIDATx\x9cc\x00\x01\x00"
    b"\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82"
)

# Minimal valid WEBP file header structure
VALID_WEBP_BYTES = (
    b"RIFF\x1a\x00\x00\x00WEBPVP8L\x0e\x00\x00\x00/\x00\x00\x00\x00\x07"
    b"\x88\x85\x08\x88\x00\x00\x00"
)

# Malicious Windows PE Executable starting with 'MZ' renamed as an image
DISGUISED_EXE_BYTES = b"MZ\x90\x00\x03\x00\x00\x00\x04\x00\x00\x00\xff\xffThis is a disguised executable binary."

# Isolated in-memory SQLite database for testing (never connects to production)
test_engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


def override_get_db():
    """Overrides get_db with isolated in-memory test session."""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    """Creates all database tables in memory once for the test session."""
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture(autouse=True)
def clean_db_tables():
    """Wipes all rows between tests to guarantee isolated, reproducible test runs."""
    with test_engine.connect() as conn:
        for table in reversed(Base.metadata.sorted_tables):
            conn.execute(table.delete())
        conn.commit()


@pytest.fixture
def db_session() -> Session:
    """Provides a direct database session for unit and repository tests."""
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture(autouse=True)
def reset_rate_limiter():
    """Resets the in-memory rate limiter before each test to prevent test cross-talk."""
    limiter.reset()
    yield
    limiter.reset()


@pytest.fixture(scope="session")
def client() -> TestClient:
    """Provides a synchronous test client connected to the FastAPI application with mock AI and test DB."""
    app.dependency_overrides[get_ai_service] = lambda: MockAIService()
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def valid_jpeg() -> bytes:
    """Returns valid binary JPEG bytes."""
    return VALID_JPEG_BYTES


@pytest.fixture
def valid_png() -> bytes:
    """Returns valid binary PNG bytes."""
    return VALID_PNG_BYTES


@pytest.fixture
def valid_webp() -> bytes:
    """Returns valid binary WEBP bytes."""
    return VALID_WEBP_BYTES


@pytest.fixture
def disguised_exe() -> bytes:
    """Returns executable bytes renamed to .jpg."""
    return DISGUISED_EXE_BYTES


@pytest.fixture
def oversized_image() -> bytes:
    """Returns an image payload exceeding MAX_UPLOAD_SIZE_MB (5 MB)."""
    return VALID_JPEG_BYTES + (b"\x00" * (settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024 + 1024))
