"""
Mathematical Risk Scoring & Normalization Engine
"""
from typing import Dict, Any, Tuple
from app.core.thresholds import RiskThresholds


class RiskScorer:
    """
    Computes weighted risk scores, applies dampening to prevent disproportionate double-counting,
    and maps the final composite score to standardized risk levels.
    """

    def __init__(self, thresholds: RiskThresholds):
        self.thresholds = thresholds

    def compute_composite_score(
        self,
        norm_price: float,
        norm_keywords: float,
        norm_image: float,
        norm_seller: float,
        norm_behavior: float,
        has_image: bool = True,
        renormalize_missing: bool = False
    ) -> Tuple[float, Dict[str, float], str]:
        """
        Calculates individual factor point contributions and final total score (0 to 100).
        """
        w_price = self.thresholds.weight_price_anomaly
        w_kw = self.thresholds.weight_fraud_keywords
        w_img = self.thresholds.weight_image_similarity if has_image else 0.0
        w_seller = self.thresholds.weight_seller_reputation
        w_beh = self.thresholds.weight_listing_behavior

        total_active_weight = w_price + w_kw + w_img + w_seller + w_beh

        # Raw points for each factor
        pts_price = norm_price * self.thresholds.weight_price_anomaly
        pts_kw = norm_keywords * self.thresholds.weight_fraud_keywords
        pts_img = norm_image * self.thresholds.weight_image_similarity
        pts_seller = norm_seller * self.thresholds.weight_seller_reputation
        pts_beh = norm_behavior * self.thresholds.weight_listing_behavior

        raw_total = pts_price + pts_kw + pts_img + pts_seller + pts_beh

        if renormalize_missing and not has_image and total_active_weight > 0:
            # Scale proportionally so 100 max points is still attainable
            scale_factor = 100.0 / total_active_weight
            final_total = raw_total * scale_factor
        else:
            final_total = raw_total

        # Clamp cleanly to [0.0, 100.0]
        final_total = min(100.0, max(0.0, final_total))

        # Risk Classification
        if final_total <= self.thresholds.low_max:
            risk_level = "Low"
        elif final_total <= self.thresholds.medium_max:
            risk_level = "Medium"
        else:
            risk_level = "High"

        breakdown = {
            "price_anomaly_score": round(pts_price, 2),
            "fraud_keywords_score": round(pts_kw, 2),
            "image_similarity_score": round(pts_img, 2),
            "seller_reputation_score": round(pts_seller, 2),
            "listing_behavior_score": round(pts_beh, 2),
            "total_score": round(final_total, 2)
        }

        return round(final_total, 2), breakdown, risk_level
