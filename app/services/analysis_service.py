"""
Analysis Service: End-to-End Orchestration of Fraud Detection & DB Persistence
"""
import uuid
from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session
from app.api.schemas.request import AnalyzeListingRequest, BatchAnalyzeRequest
from app.api.schemas.response import AnalyzeResponse, BatchAnalyzeResponse, ScoreBreakdown, RiskLevelEnum, RecommendationEnum
from app.core.risk_engine import RiskEngine
from app.detectors.image_checker import ImageChecker
from app.ml.predict import MLFraudPredictor
from app.database.models import Listing, Merchant, ImageFingerprint
from app.database.repositories.listing_repo import ListingRepository
from app.database.repositories.merchant_repo import MerchantRepository
from app.services.alert_service import AlertService
from app.services.merchant_service import MerchantService

# Singleton inference predictor
ml_predictor = MLFraudPredictor()


class AnalysisService:

    def __init__(self, db: Session):
        self.db = db
        self.listing_repo = ListingRepository(db)
        self.merchant_repo = MerchantRepository(db)
        self.alert_service = AlertService(db)
        self.merchant_service = MerchantService(db)

        # Build image checker with all previously known fingerprints from database
        known_hashes = {}
        fingerprints = db.query(ImageFingerprint).all()
        for fp in fingerprints:
            known_hashes[fp.image_hash] = fp.listing_id

        self.image_checker = ImageChecker(known_hashes=known_hashes)
        self.risk_engine = RiskEngine(
            image_checker=self.image_checker,
            ml_predictor=ml_predictor
        )

    def analyze_listing(
        self,
        req: AnalyzeListingRequest,
        persist: bool = False
    ) -> AnalyzeResponse:
        """
        Analyzes a single marketplace listing, optionally persisting it to the database.
        """
        listing_ref_id = req.listing_id or f"lst_{uuid.uuid4().hex[:10]}"

        # Look up merchant if provided
        merchant = None
        s_rating = req.seller_rating
        s_age = req.seller_account_age_days
        s_complaints = req.seller_complaints_count
        s_total_listings = None
        s_flagged_listings = None
        is_verified = None

        if req.merchant_id:
            merchant = self.merchant_repo.get_by_merchant_id(req.merchant_id)
            if merchant:
                s_rating = merchant.rating if s_rating is None else s_rating
                s_age = merchant.account_age_days if s_age is None else s_age
                s_complaints = merchant.complaints_count if s_complaints is None else s_complaints
                s_total_listings = merchant.total_listings
                s_flagged_listings = merchant.flagged_listings
                is_verified = merchant.is_verified

        # Execute Multi-Dimensional Risk Evaluation
        eval_result = self.risk_engine.analyze_listing(
            title=req.title,
            description=req.description,
            price=req.price,
            market_price=req.market_price,
            category=req.category,
            listing_id=listing_ref_id,
            seller_rating=s_rating,
            seller_account_age_days=s_age,
            seller_complaints_count=s_complaints,
            seller_total_listings=s_total_listings,
            seller_flagged_listings=s_flagged_listings,
            is_verified_seller=is_verified,
            image_input=req.image_base64 or req.image_url,
            image_hash=req.image_hash
        )

        score_breakdown_dict = eval_result["score_breakdown"]
        score_breakdown_obj = ScoreBreakdown(
            price_anomaly_score=score_breakdown_dict["price_anomaly_score"],
            fraud_keywords_score=score_breakdown_dict["fraud_keywords_score"],
            image_similarity_score=score_breakdown_dict["image_similarity_score"],
            seller_reputation_score=score_breakdown_dict["seller_reputation_score"],
            listing_behavior_score=score_breakdown_dict["listing_behavior_score"],
            total_score=score_breakdown_dict["total_score"]
        )

        # Persist to database if requested
        if persist:
            # Ensure merchant exists in DB
            merchant_id = req.merchant_id or "merch_anonymous"
            if not self.merchant_repo.get_by_merchant_id(merchant_id):
                self.merchant_repo.create_or_update({
                    "merchant_id": merchant_id,
                    "name": f"Merchant {merchant_id}",
                    "rating": s_rating or 4.5,
                    "account_age_days": s_age or 30,
                    "complaints_count": s_complaints or 0,
                    "is_verified": False,
                    "risk_score": 15.0,
                    "risk_level": "Low"
                })

            computed_hash = eval_result["evidence"]["image"].get("image_hash")
            existing_listing = self.listing_repo.get_by_listing_id(listing_ref_id)
            if not existing_listing:
                created_listing = self.listing_repo.create({
                    "listing_id": listing_ref_id,
                    "merchant_id": merchant_id,
                    "title": req.title,
                    "description": req.description,
                    "category": req.category,
                    "price": req.price,
                    "market_price": req.market_price,
                    "currency": req.currency,
                    "image_url": req.image_url,
                    "image_hash": computed_hash,
                    "risk_score": eval_result["risk_score"],
                    "risk_level": eval_result["risk_level"],
                    "ml_fraud_probability": eval_result.get("ml_fraud_probability"),
                    "ml_prediction": eval_result.get("ml_prediction"),
                    "flags": eval_result["flags"],
                    "score_breakdown": score_breakdown_dict,
                    "evidence": eval_result["evidence"],
                    "status": "REJECTED" if eval_result["recommendation"] == "AUTO_REJECT" else (
                        "APPROVED" if eval_result["recommendation"] == "AUTO_APPROVE" else "PENDING_REVIEW"
                    )
                })

                # Register image fingerprint
                if computed_hash:
                    fp = ImageFingerprint(
                        listing_id=listing_ref_id,
                        image_hash=computed_hash,
                        perceptual_hash=computed_hash,
                        duplicate_of_id=eval_result["evidence"]["image"].get("matches", [{}])[0].get("source_id") if eval_result["evidence"]["image"].get("is_duplicate") else None,
                        similarity_score=eval_result["evidence"]["image"].get("similarity_score", 0.0)
                    )
                    self.db.add(fp)
                    self.db.commit()

            # Trigger alert for high risk
            self.alert_service.create_alert_if_needed(
                listing_id=listing_ref_id,
                risk_score=eval_result["risk_score"],
                risk_level=eval_result["risk_level"],
                flags=eval_result["flags"],
                merchant_id=merchant_id
            )

            # Update merchant risk stats
            self.merchant_service.update_merchant_risk_profile(merchant_id)

        return AnalyzeResponse(
            listing_id=eval_result["listing_id"],
            title=eval_result["title"],
            risk_score=eval_result["risk_score"],
            risk_level=RiskLevelEnum(eval_result["risk_level"]),
            recommendation=RecommendationEnum(eval_result["recommendation"]),
            ml_prediction=eval_result.get("ml_prediction"),
            ml_fraud_probability=eval_result.get("ml_fraud_probability"),
            flags=eval_result["flags"],
            score_breakdown=score_breakdown_obj,
            evidence=eval_result["evidence"]
        )

    def analyze_batch(self, req: BatchAnalyzeRequest, persist: bool = False) -> BatchAnalyzeResponse:
        results = [self.analyze_listing(item, persist=persist) for item in req.listings]
        total = len(results)
        high = sum(1 for r in results if r.risk_level == RiskLevelEnum.HIGH)
        med = sum(1 for r in results if r.risk_level == RiskLevelEnum.MEDIUM)
        low = sum(1 for r in results if r.risk_level == RiskLevelEnum.LOW)
        avg_score = round(sum(r.risk_score for r in results) / total, 2) if total > 0 else 0.0

        return BatchAnalyzeResponse(
            total_processed=total,
            high_risk_count=high,
            medium_risk_count=med,
            low_risk_count=low,
            average_risk_score=avg_score,
            results=results
        )
