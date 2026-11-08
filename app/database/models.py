"""
SQLAlchemy ORM Data Models for TrustLens
"""
import uuid
from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Float, Boolean, DateTime,
    ForeignKey, Text, JSON, Index
)
from sqlalchemy.orm import relationship
from app.database.connection import Base


def generate_uuid() -> str:
    return str(uuid.uuid4())


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(String(36), default=generate_uuid, unique=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(20), default="analyst", nullable=False)  # admin, investigator, analyst, client
    api_key = Column(String(64), unique=True, index=True, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    reviews = relationship("Listing", back_populates="reviewer")


class Merchant(Base):
    __tablename__ = "merchants"

    id = Column(Integer, primary_key=True, index=True)
    merchant_id = Column(String(64), unique=True, index=True, nullable=False)
    name = Column(String(150), nullable=False)
    email = Column(String(150), nullable=True)
    rating = Column(Float, default=5.0)  # 1.0 - 5.0
    total_listings = Column(Integer, default=0)
    flagged_listings = Column(Integer, default=0)
    account_age_days = Column(Integer, default=30)
    complaints_count = Column(Integer, default=0)
    is_verified = Column(Boolean, default=False)
    risk_score = Column(Float, default=10.0)
    risk_level = Column(String(20), default="Low")  # Low, Medium, High
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    listings = relationship("Listing", back_populates="merchant")
    alerts = relationship("RiskAlert", back_populates="merchant")


class Listing(Base):
    __tablename__ = "listings"

    id = Column(Integer, primary_key=True, index=True)
    listing_id = Column(String(64), unique=True, index=True, nullable=False)
    merchant_id = Column(String(64), ForeignKey("merchants.merchant_id"), index=True, nullable=False)
    title = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=False)
    category = Column(String(80), default="General", index=True)
    price = Column(Float, nullable=False)
    market_price = Column(Float, nullable=True)
    currency = Column(String(10), default="USD")
    image_url = Column(String(500), nullable=True)
    image_hash = Column(String(64), nullable=True, index=True)

    # Risk Scoring Outcomes
    risk_score = Column(Float, default=0.0, index=True)
    risk_level = Column(String(20), default="Low", index=True)  # Low, Medium, High
    ml_fraud_probability = Column(Float, nullable=True)
    ml_prediction = Column(String(20), nullable=True)  # Genuine, Fraudulent
    
    # Detailed Evidence & Explainability
    flags = Column(JSON, default=list)
    score_breakdown = Column(JSON, default=dict)
    evidence = Column(JSON, default=dict)

    # Human Investigation Status
    status = Column(String(30), default="PENDING_REVIEW", index=True)  # PENDING_REVIEW, APPROVED, REJECTED, ESCALATED
    review_notes = Column(Text, nullable=True)
    reviewed_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    reviewed_at = Column(DateTime, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    merchant = relationship("Merchant", back_populates="listings")
    reviewer = relationship("User", back_populates="reviews")
    fingerprints = relationship("ImageFingerprint", back_populates="listing")
    alerts = relationship("RiskAlert", back_populates="listing")


class ImageFingerprint(Base):
    __tablename__ = "image_fingerprints"

    id = Column(Integer, primary_key=True, index=True)
    listing_id = Column(String(64), ForeignKey("listings.listing_id"), index=True, nullable=False)
    image_hash = Column(String(64), index=True, nullable=False)
    perceptual_hash = Column(String(64), index=True, nullable=False)
    original_filename = Column(String(255), nullable=True)
    file_path = Column(String(500), nullable=True)
    duplicate_of_id = Column(String(64), nullable=True)
    similarity_score = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)

    listing = relationship("Listing", back_populates="fingerprints")


class RiskAlert(Base):
    __tablename__ = "risk_alerts"

    id = Column(Integer, primary_key=True, index=True)
    alert_id = Column(String(36), default=generate_uuid, unique=True)
    severity = Column(String(20), default="HIGH", index=True)  # MEDIUM, HIGH, CRITICAL
    message = Column(String(255), nullable=False)
    listing_id = Column(String(64), ForeignKey("listings.listing_id"), nullable=True)
    merchant_id = Column(String(64), ForeignKey("merchants.merchant_id"), nullable=True)
    is_resolved = Column(Boolean, default=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    listing = relationship("Listing", back_populates="alerts")
    merchant = relationship("Merchant", back_populates="alerts")


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=True)
    username = Column(String(50), nullable=True)
    action = Column(String(100), nullable=False)  # ANALYZE_LISTING, INVESTIGATE_DECISION, UPDATE_THRESHOLDS, etc.
    resource_type = Column(String(50), nullable=True)
    resource_id = Column(String(64), nullable=True)
    details = Column(JSON, default=dict)
    ip_address = Column(String(45), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
