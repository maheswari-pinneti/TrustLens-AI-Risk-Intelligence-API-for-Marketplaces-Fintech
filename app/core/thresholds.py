"""
Configurable Risk Thresholds and Factor Weights
"""
from pydantic import BaseModel, Field


class RiskThresholds(BaseModel):
    # Weights allocated to each fraud dimension (sum = 100)
    weight_price_anomaly: float = Field(default=30.0, ge=0.0, le=100.0)
    weight_fraud_keywords: float = Field(default=25.0, ge=0.0, le=100.0)
    weight_image_similarity: float = Field(default=20.0, ge=0.0, le=100.0)
    weight_seller_reputation: float = Field(default=15.0, ge=0.0, le=100.0)
    weight_listing_behavior: float = Field(default=10.0, ge=0.0, le=100.0)

    # Classification boundaries (0 to 100)
    low_max: float = 29.0
    medium_max: float = 59.0

    # Operational decision thresholds matching risk tiers (0-29 Low, 30-59 Medium, 60-100 High)
    auto_approve_cutoff: float = 29.0
    auto_reject_cutoff: float = 60.0

    def total_weight(self) -> float:
        return (
            self.weight_price_anomaly +
            self.weight_fraud_keywords +
            self.weight_image_similarity +
            self.weight_seller_reputation +
            self.weight_listing_behavior
        )
