"""
Integration Tests for REST API Business Logic
"""
import pytest
from app.services.analysis_service import AnalysisService
from app.services.merchant_service import MerchantService
from app.services.report_service import ReportService
from app.api.schemas.request import AnalyzeListingRequest, BatchAnalyzeRequest, InvestigationDecisionRequest
from app.database.models import User, Listing, Merchant


def test_analyze_service_single_listing(db_session):
    service = AnalysisService(db_session)
    req = AnalyzeListingRequest(
        title="Nike Shoes Cheap Replica",
        description="1:1 replica fake shoes whatsapp me",
        price=35.0,
        market_price=200.0,
        seller_rating=1.5
    )
    res = service.analyze_listing(req, persist=True)
    assert res.risk_score >= 50.0
    assert len(res.flags) >= 2
    assert res.score_breakdown.price_anomaly_score > 0
    assert res.score_breakdown.fraud_keywords_score > 0

    # Ensure saved in DB
    saved = db_session.query(Listing).filter(Listing.listing_id == res.listing_id).first()
    assert saved is not None
    assert saved.title == req.title


def test_batch_analyze_service(db_session):
    service = AnalysisService(db_session)
    req1 = AnalyzeListingRequest(
        title="Authentic Sony Headphones",
        description="Original brand new sealed with warranty",
        price=320.0,
        market_price=350.0
    )
    req2 = AnalyzeListingRequest(
        title="Counterfeit Rolex Watch",
        description="Superclone replica 1:1 master copy wire transfer only",
        price=100.0,
        market_price=10000.0,
        seller_rating=1.2,
        seller_account_age_days=2,
        seller_complaints_count=5
    )
    batch_req = BatchAnalyzeRequest(listings=[req1, req2])
    batch_res = service.analyze_batch(batch_req, persist=True)

    assert batch_res.total_processed == 2
    assert len(batch_res.results) == 2
    assert batch_res.high_risk_count >= 1


def test_investigator_decision_update(db_session):
    service = AnalysisService(db_session)
    req = AnalyzeListingRequest(
        title="Suspicious Camera",
        description="Super cheap camera must go today",
        price=20.0,
        market_price=200.0
    )
    res = service.analyze_listing(req, persist=True)

    # Human investigator rejects
    user = db_session.query(User).filter(User.username == "testadmin").first()
    updated = service.listing_repo.update_decision(
        listing_id=res.listing_id,
        status="REJECTED",
        reviewer_id=user.id,
        review_notes="Confirmed counterfeit serial number."
    )
    assert updated.status == "REJECTED"
    assert updated.review_notes == "Confirmed counterfeit serial number."


def test_report_service_generation(db_session):
    service = AnalysisService(db_session)
    req = AnalyzeListingRequest(
        title="Chanel Handbag Replica",
        description="Replica mirror quality handbag",
        price=150.0,
        market_price=5000.0,
        category="Luxury Goods"
    )
    service.analyze_listing(req, persist=True)

    report_service = ReportService(db_session)
    summary = report_service.generate_risk_summary()

    assert summary["total_listings_analyzed"] >= 1
    assert len(summary["category_risk_distribution"]) >= 1
    assert any(k["keyword"] == "replica" for k in summary["top_fraud_keywords"])
