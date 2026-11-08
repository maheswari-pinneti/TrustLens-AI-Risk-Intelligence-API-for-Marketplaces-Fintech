"""
Core Orchestration Risk Engine for TrustLens
"""
import uuid
from typing import Dict, Any, Optional, List
from app.config import get_settings
from app.core.thresholds import RiskThresholds
from app.core.scoring import RiskScorer
from app.core.explainability import ExplainabilityEngine
from app.detectors.keyword_detector import KeywordDetector
from app.detectors.price_analyzer import PriceAnalyzer
from app.detectors.image_checker import ImageChecker
from app.detectors.seller_analyzer import SellerAnalyzer
from app.detectors.behavior_detector import BehaviorDetector


class RiskEngine:
    """
    Main Risk Intelligence Engine: integrates modular detectors, scores risk factors,
    generates auditable evidence, and pairs rule-based decisions with ML predictions.
    """

    def __init__(
        self,
        thresholds: Optional[RiskThresholds] = None,
        image_checker: Optional[ImageChecker] = None,
        ml_predictor: Optional[Any] = None
    ):
        settings = get_settings()
        self.thresholds = thresholds or RiskThresholds(
            weight_price_anomaly=settings.WEIGHT_PRICE_ANOMALY,
            weight_fraud_keywords=settings.WEIGHT_FRAUD_KEYWORDS,
            weight_image_similarity=settings.WEIGHT_IMAGE_SIMILARITY,
            weight_seller_reputation=settings.WEIGHT_SELLER_REPUTATION,
            weight_listing_behavior=settings.WEIGHT_LISTING_BEHAVIOR,
            low_max=settings.RISK_THRESHOLD_LOW,
            medium_max=settings.RISK_THRESHOLD_MEDIUM
        )
        self.scorer = RiskScorer(self.thresholds)
        self.explainability = ExplainabilityEngine()

        # Modular Detectors
        self.keyword_detector = KeywordDetector()
        self.price_analyzer = PriceAnalyzer()
        self.image_checker = image_checker or ImageChecker()
        self.seller_analyzer = SellerAnalyzer()
        self.behavior_detector = BehaviorDetector()

        # Machine Learning Layer (optional inference)
        self.ml_predictor = ml_predictor

    def update_thresholds(self, new_thresholds: RiskThresholds) -> None:
        self.thresholds = new_thresholds
        self.scorer = RiskScorer(new_thresholds)

    def analyze_listing(
        self,
        title: str,
        description: str,
        price: float,
        market_price: Optional[float] = None,
        category: Optional[str] = "General",
        listing_id: Optional[str] = None,
        seller_rating: Optional[float] = None,
        seller_account_age_days: Optional[int] = None,
        seller_complaints_count: Optional[int] = None,
        seller_total_listings: Optional[int] = None,
        seller_flagged_listings: Optional[int] = None,
        is_verified_seller: Optional[bool] = None,
        image_input: Optional[Any] = None,
        image_hash: Optional[str] = None,
        listing_velocity_1h: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Executes end-to-end multi-dimensional risk assessment.
        """
        listing_ref_id = listing_id or f"lst_{uuid.uuid4().hex[:10]}"

        # 1. Keyword Detection
        kw_result = self.keyword_detector.analyze(title=title, description=description)

        # 2. Price Anomaly Detection
        price_result = self.price_analyzer.analyze(
            price=price,
            market_price=market_price,
            category=category
        )

        # 3. Image Similarity Detection
        has_image = bool(image_input or image_hash)
        img_result = self.image_checker.analyze(
            image_input=image_input,
            precomputed_hash=image_hash
        )

        # 4. Seller Reputation Analysis
        seller_result = self.seller_analyzer.analyze(
            rating=seller_rating,
            account_age_days=seller_account_age_days,
            complaints_count=seller_complaints_count,
            total_listings=seller_total_listings,
            flagged_listings=seller_flagged_listings,
            is_verified=is_verified_seller
        )

        # 5. Behavioral Anomaly Detection
        beh_result = self.behavior_detector.analyze(
            title=title,
            description=description,
            listing_velocity_1h=listing_velocity_1h
        )

        # 6. Mathematical Score Aggregation
        total_score, score_breakdown, risk_level = self.scorer.compute_composite_score(
            norm_price=price_result["normalized_score"],
            norm_keywords=kw_result["normalized_score"],
            norm_image=img_result["normalized_score"],
            norm_seller=seller_result["normalized_score"],
            norm_behavior=beh_result["normalized_score"],
            has_image=has_image,
            renormalize_missing=False
        )

        # Collect All Flags
        all_flags: List[str] = (
            kw_result["flags"] +
            price_result["flags"] +
            img_result["flags"] +
            seller_result["flags"] +
            beh_result["flags"]
        )

        # Explainability & Recommendation
        recommendation = self.explainability.generate_recommendation(total_score, self.thresholds)
        ranked_contributions = self.explainability.rank_contributions(score_breakdown)
        explanation_text = self.explainability.build_summary_explanation(
            risk_level=risk_level,
            risk_score=total_score,
            ranked_factors=ranked_contributions,
            flags=all_flags
        )

        # 7. Machine Learning Inference (if model loaded)
        ml_prediction = None
        ml_fraud_prob = None
        if self.ml_predictor is not None:
            try:
                ml_out = self.ml_predictor.predict_single({
                    "price": price,
                    "market_price": market_price or price,
                    "discount_pct": price_result.get("discount_percentage") or 0.0,
                    "keyword_score": kw_result["normalized_score"],
                    "seller_rating": seller_rating or 4.0,
                    "account_age_days": seller_account_age_days or 90,
                    "complaints_count": seller_complaints_count or 0,
                    "image_duplicate": 1 if img_result["is_duplicate"] else 0,
                    "title_len": len(title),
                    "desc_len": len(description)
                })
                ml_prediction = ml_out.get("prediction")
                ml_fraud_prob = ml_out.get("fraud_probability")
            except Exception:
                pass

        return {
            "listing_id": listing_ref_id,
            "title": title,
            "risk_score": total_score,
            "risk_level": risk_level,
            "recommendation": recommendation,
            "ml_prediction": ml_prediction,
            "ml_fraud_probability": ml_fraud_prob,
            "flags": all_flags,
            "score_breakdown": score_breakdown,
            "evidence": {
                "keywords": kw_result,
                "pricing": price_result,
                "image": img_result,
                "seller": seller_result,
                "behavior": beh_result,
                "ranked_contributions": ranked_contributions,
                "summary_explanation": explanation_text
            }
        }
