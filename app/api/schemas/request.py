"""
Pydantic Request Schemas for TrustLens
"""
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, field_validator
from app.security.sanitizer import sanitize_text


class AnalyzeListingRequest(BaseModel):
    listing_id: Optional[str] = Field(default=None, description="Unique listing identifier")
    title: str = Field(..., min_length=2, max_length=255, description="Product listing title", examples=["Nike Air Jordan 1 Retro High"])
    description: str = Field(..., min_length=5, max_length=10000, description="Product description", examples=["Brand new cheap replica nike shoes 1:1 ua quality whatsapp me"])
    price: float = Field(..., gt=0, description="Listing price in chosen currency", examples=[500.0])
    market_price: Optional[float] = Field(default=None, gt=0, description="Average estimated market benchmark price", examples=[5000.0])
    currency: str = Field(default="USD", max_length=5, description="Currency ISO code")
    category: str = Field(default="General", max_length=80, description="Product category", examples=["Footwear & Apparel"])
    
    # Seller / Merchant attributes (either merchant_id or inline metrics)
    merchant_id: Optional[str] = Field(default=None, description="Merchant identifier", examples=["merch_001"])
    seller_rating: Optional[float] = Field(default=None, ge=0.0, le=5.0, description="Seller rating (0.0 to 5.0)", examples=[1.2])
    seller_account_age_days: Optional[int] = Field(default=None, ge=0, description="Account age in days", examples=[4])
    seller_complaints_count: Optional[int] = Field(default=None, ge=0, description="Number of unresolved complaints against seller", examples=[7])
    
    # Image attributes
    image_url: Optional[str] = Field(default=None, description="URL to product image")
    image_base64: Optional[str] = Field(default=None, description="Base64-encoded image string for hash extraction")
    image_hash: Optional[str] = Field(default=None, description="Pre-computed perceptual hash string")

    @field_validator("title", "description")
    @classmethod
    def sanitize_field(cls, v: str) -> str:
        if not v:
            return ""
        return sanitize_text(v.strip())


class BatchAnalyzeRequest(BaseModel):
    listings: List[AnalyzeListingRequest] = Field(..., min_length=1, max_length=100, description="Batch of listings to analyze")


class ListingCreateRequest(AnalyzeListingRequest):
    merchant_id: str = Field(..., description="Required merchant ID for persistent listings")


class InvestigationDecisionRequest(BaseModel):
    status: str = Field(..., description="Investigation status decision: APPROVED, REJECTED, ESCALATED")
    review_notes: Optional[str] = Field(default=None, max_length=1000, description="Investigator rationale and notes")

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: str) -> str:
        valid_statuses = {"APPROVED", "REJECTED", "ESCALATED", "PENDING_REVIEW"}
        v_upper = v.upper()
        if v_upper not in valid_statuses:
            raise ValueError(f"Invalid status '{v}'. Allowed: {', '.join(valid_statuses)}")
        return v_upper


class MerchantCreateRequest(BaseModel):
    merchant_id: str = Field(..., min_length=3, max_length=64)
    name: str = Field(..., min_length=2, max_length=150)
    email: Optional[str] = Field(default=None, max_length=150)
    rating: float = Field(default=5.0, ge=1.0, le=5.0)
    account_age_days: int = Field(default=30, ge=0)
    complaints_count: int = Field(default=0, ge=0)
    is_verified: bool = Field(default=False)


class ThresholdUpdateRequest(BaseModel):
    weight_price_anomaly: float = Field(..., ge=0.0, le=100.0)
    weight_fraud_keywords: float = Field(..., ge=0.0, le=100.0)
    weight_image_similarity: float = Field(..., ge=0.0, le=100.0)
    weight_seller_reputation: float = Field(..., ge=0.0, le=100.0)
    weight_listing_behavior: float = Field(..., ge=0.0, le=100.0)
    risk_threshold_low: float = Field(default=29.0, ge=0.0, le=100.0)
    risk_threshold_medium: float = Field(default=59.0, ge=0.0, le=100.0)
