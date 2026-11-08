"""
Integration tests for Human Feedback Collection & Active Learning Loop
"""
import pytest
from app.services.analysis_service import AnalysisService
from app.services.feedback_service import FeedbackService
from app.api.schemas.request import AnalyzeListingRequest


def test_feedback_collection_and_stats(db_session):
    analysis_svc = AnalysisService(db_session)
    feedback_svc = FeedbackService(db_session)

    # 1. Evaluate a listing
    req = AnalyzeListingRequest(
        title="Questionable Luxury Bag",
        description="Replica bag must go today",
        price=50.0,
        market_price=2000.0
    )
    res = analysis_svc.analyze_listing(req, persist=True)

    # 2. Confirm investigator rejection
    analysis_svc.listing_repo.update_decision(
        listing_id=res.listing_id,
        status="REJECTED",
        reviewer_id=1,
        review_notes="Confirmed unauthorized clone."
    )

    # 3. Check feedback stats
    stats = feedback_svc.get_feedback_statistics()
    assert stats["total_human_reviewed"] >= 1
    assert stats["rejected_as_fraud"] >= 1
    assert stats["label_ratio_fraud_pct"] > 0
