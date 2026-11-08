"""
Pytest Test Fixtures and Test Environment Setup
"""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database.connection import Base
from app.database.models import User, Merchant, Listing
from app.core.risk_engine import RiskEngine
from app.detectors.keyword_detector import KeywordDetector
from app.detectors.price_analyzer import PriceAnalyzer
from app.detectors.image_checker import ImageChecker
from app.detectors.seller_analyzer import SellerAnalyzer
from app.detectors.behavior_detector import BehaviorDetector
from app.security.authentication import hash_password

TEST_DATABASE_URL = "sqlite:///:memory:"


@pytest.fixture(scope="function")
def db_session():
    """In-memory SQLite database session isolated per test."""
    engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()

    # Seed test users
    admin = User(
        username="testadmin",
        email="testadmin@test.local",
        hashed_password=hash_password("TestAdmin123!"),
        role="admin",
        api_key="tl_test_admin_key_123",
        is_active=True
    )
    analyst = User(
        username="testanalyst",
        email="testanalyst@test.local",
        hashed_password=hash_password("TestAnalyst123!"),
        role="analyst",
        api_key="tl_test_analyst_key_456",
        is_active=True
    )
    db.add(admin)
    db.add(analyst)
    db.commit()

    yield db

    db.close()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def keyword_detector():
    return KeywordDetector()


@pytest.fixture
def price_analyzer():
    return PriceAnalyzer()


@pytest.fixture
def image_checker():
    return ImageChecker()


@pytest.fixture
def seller_analyzer():
    return SellerAnalyzer()


@pytest.fixture
def behavior_detector():
    return BehaviorDetector()


@pytest.fixture
def risk_engine():
    return RiskEngine()
