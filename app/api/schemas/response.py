"""
Pydantic Response Schemas for TrustLens
"""
from datetime import datetime
from enum import Enum
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict


class RiskLevelEnum(str, Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"


class RecommendationEnum(str, Enum):
    AUTO_APPROVE = "AUTO_APPROVE"
    MANUAL_REVIEW = "MANUAL_REVIEW"
    AUTO_REJECT = "AUTO_REJECT"


class ScoreBreakdown(BaseModel):
    price_anomaly_score: float = Field(..., description="Points from price anomaly factor (max 30)")
    fraud_keywords_score: float = Field(..., description="Points from keyword detector (max 25)")
    image_similarity_score: float = Field(..., description="Points from duplicate/counterfeit image detector (max 20)")
    seller_reputation_score: float = Field(..., description="Points from seller risk metrics (max 15)")
    listing_behavior_score: float = Field(..., description="Points from listing behavioral patterns (max 10)")
    total_score: float = Field(..., description="Sum of weighted scores (0 to 100)")


class AnalyzeResponse(BaseModel):
    listing_id: str
    title: str
    risk_score: float
    risk_level: RiskLevelEnum
    recommendation: RecommendationEnum
    ml_prediction: Optional[str] = None
    ml_fraud_probability: Optional[float] = None
    flags: List[str]
    score_breakdown: ScoreBreakdown
    evidence: Dict[str, Any]
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class BatchAnalyzeResponse(BaseModel):
    total_processed: int
    high_risk_count: int
    medium_risk_count: int
    low_risk_count: int
    average_risk_score: float
    results: List[AnalyzeResponse]


class ListingResponse(BaseModel):
    id: int
    listing_id: str
    merchant_id: str
    title: str
    description: str
    category: str
    price: float
    market_price: Optional[float] = None
    currency: str
    image_url: Optional[str] = None
    image_hash: Optional[str] = None
    risk_score: float
    risk_level: str
    ml_fraud_probability: Optional[float] = None
    ml_prediction: Optional[str] = None
    flags: List[str]
    score_breakdown: Dict[str, Any]
    evidence: Dict[str, Any]
    status: str
    review_notes: Optional[str] = None
    reviewed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class MerchantResponse(BaseModel):
    id: int
    merchant_id: str
    name: str
    email: Optional[str] = None
    rating: float
    total_listings: int
    flagged_listings: int
    account_age_days: int
    complaints_count: int
    is_verified: bool
    risk_score: float
    risk_level: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class RiskSummaryResponse(BaseModel):
    total_listings_analyzed: int
    total_merchants_tracked: int
    high_risk_listings: int
    medium_risk_listings: int
    low_risk_listings: int
    pending_investigation_count: int
    resolved_investigation_count: int
    average_risk_score: float
    top_fraud_keywords: List[Dict[str, Any]]
    category_risk_distribution: List[Dict[str, Any]]
    recent_alerts: List[Dict[str, Any]]


class ImageCheckResponse(BaseModel):
    image_hash: str
    perceptual_hash: str
    is_duplicate: bool
    duplicate_listing_id: Optional[str] = None
    similarity_score: float
    flags: List[str]


class HealthResponse(BaseModel):
    status: str
    environment: str
    version: str
    database_connected: bool
    ml_model_loaded: bool
    timestamp: datetime = Field(default_factory=datetime.utcnow)
