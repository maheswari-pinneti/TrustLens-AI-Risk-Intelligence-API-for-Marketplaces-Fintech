"""
Unit tests for Price Anomaly & Valuation Analyzer
"""
import pytest
from app.detectors.price_analyzer import PriceAnalyzer


def test_normal_pricing(price_analyzer):
    result = price_analyzer.analyze(
        price=180.0,
        market_price=200.0,
        category="Footwear & Apparel"
    )
    assert result["normalized_score"] == 0.0
    assert result["discount_percentage"] == 10.0
    assert result["anomaly_type"] == "NORMAL_PRICING"
    assert len(result["flags"]) == 0


def test_extreme_discount_counterfeit_indicator(price_analyzer):
    result = price_analyzer.analyze(
        price=25.0,
        market_price=500.0,
        category="Smartphones"
    )
    # 95% discount
    assert result["discount_percentage"] == 95.0
    assert result["normalized_score"] >= 0.9
    assert result["anomaly_type"] == "CRITICAL_UNDERPRICING"
    assert len(result["flags"]) >= 1


def test_missing_market_price_below_category_floor(price_analyzer):
    # Luxury Goods min reasonable is $150
    result = price_analyzer.analyze(
        price=15.0,
        market_price=None,
        category="Luxury Goods"
    )
    assert result["normalized_score"] >= 0.7
    assert result["anomaly_type"] == "BELOW_CATEGORY_MINIMUM"
    assert len(result["flags"]) >= 1


def test_zero_or_negative_price(price_analyzer):
    result = price_analyzer.analyze(price=0.0)
    assert result["normalized_score"] == 1.0
    assert result["anomaly_type"] == "INVALID_PRICE"

    result_neg = price_analyzer.analyze(price=-50.0)
    assert result_neg["normalized_score"] == 1.0


def test_extreme_price_gouging(price_analyzer):
    result = price_analyzer.analyze(
        price=5000.0,
        market_price=1000.0,
        category="Electronics"
    )
    assert result["normalized_score"] >= 0.6
    assert result["anomaly_type"] == "PRICE_GOUGING"
