"""
Unit tests for Core Risk Engine & Scoring Aggregator
"""
import pytest
from app.core.risk_engine import RiskEngine
from app.core.thresholds import RiskThresholds


def test_genuine_listing_low_risk(risk_engine):
    res = risk_engine.analyze_listing(
        title="Nike Air Jordan 1 Retro High Chicago",
        description="Authentic sneaker from Nike store, comes with original receipt and box.",
        price=180.0,
        market_price=200.0,
        category="Footwear & Apparel",
        seller_rating=4.9,
        seller_account_age_days=300,
        seller_complaints_count=0
    )
    assert res["risk_score"] <= 29.0
    assert res["risk_level"] == "Low"
    assert res["recommendation"] == "AUTO_APPROVE"
    assert len(res["flags"]) == 0


def test_fraudulent_counterfeit_listing_high_risk(risk_engine):
    res = risk_engine.analyze_listing(
        title="Rolex Submariner 1:1 Replica Superclone Watch",
        description="Master copy mirror quality aaa grade looks authentic wire transfer only whatsapp me",
        price=150.0,
        market_price=12000.0,
        category="Watches & Jewelry",
        seller_rating=1.2,
        seller_account_age_days=2,
        seller_complaints_count=5
    )
    assert res["risk_score"] >= 60.0
    assert res["risk_level"] == "High"
    assert res["recommendation"] == "AUTO_REJECT"
    assert len(res["flags"]) >= 4

    # Point contributions verification
    breakdown = res["score_breakdown"]
    assert breakdown["price_anomaly_score"] > 20.0
    assert breakdown["fraud_keywords_score"] > 20.0


def test_custom_threshold_update(risk_engine):
    custom = RiskThresholds(
        weight_price_anomaly=50.0,
        weight_fraud_keywords=50.0,
        weight_image_similarity=0.0,
        weight_seller_reputation=0.0,
        weight_listing_behavior=0.0,
        low_max=15.0,
        medium_max=45.0
    )
    risk_engine.update_thresholds(custom)
    assert risk_engine.thresholds.weight_price_anomaly == 50.0
