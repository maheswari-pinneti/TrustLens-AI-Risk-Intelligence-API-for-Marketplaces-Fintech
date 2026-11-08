"""
Unit tests for Seller Reputation & Historical Risk Analyzer
"""
import pytest
from app.detectors.seller_analyzer import SellerAnalyzer


def test_veteran_high_reputation_seller(seller_analyzer):
    result = seller_analyzer.analyze(
        rating=4.9,
        account_age_days=365,
        complaints_count=0,
        total_listings=50,
        flagged_listings=0,
        is_verified=True
    )
    assert result["normalized_score"] == 0.0
    assert len(result["flags"]) == 0


def test_fresh_burner_account_with_complaints(seller_analyzer):
    result = seller_analyzer.analyze(
        rating=1.5,
        account_age_days=2,
        complaints_count=6,
        is_verified=False
    )
    assert result["normalized_score"] >= 0.75
    assert any("rating" in f.lower() for f in result["flags"])
    assert any("burner" in f.lower() for f in result["flags"])
    assert any("complaint" in f.lower() for f in result["flags"])


def test_repeat_offender_flagged_ratio(seller_analyzer):
    result = seller_analyzer.analyze(
        rating=3.8,
        account_age_days=100,
        complaints_count=1,
        total_listings=20,
        flagged_listings=12  # 60% flagged
    )
    assert result["normalized_score"] >= 0.20
    assert any("repeat offender" in f.lower() for f in result["flags"])
