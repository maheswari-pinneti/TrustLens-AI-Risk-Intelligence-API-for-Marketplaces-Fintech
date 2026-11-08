"""
Unit Tests for TrustLens Python SDK
"""
import pytest
from unittest.mock import MagicMock
from sdk.trustlens_client import TrustLensClient, RiskAnalysisResult, TrustLensError


def test_sdk_result_parsing():
    mock_payload = {
        "listing_id": "lst_demo_123",
        "title": "Cheap Fake Watch",
        "risk_score": 75.5,
        "risk_level": "High",
        "recommendation": "AUTO_REJECT",
        "ml_prediction": "Fraudulent",
        "ml_fraud_probability": 0.92,
        "flags": ["Fraud keyword detected: fake", "Severe price anomaly"],
        "score_breakdown": {
            "price_anomaly_score": 30.0,
            "fraud_keywords_score": 25.0,
            "total_score": 75.5
        }
    }
    result = RiskAnalysisResult(mock_payload)
    assert result.listing_id == "lst_demo_123"
    assert result.is_high_risk is True
    assert result.is_auto_approved is False
    assert result.risk_score == 75.5
    assert len(result.flags) == 2


def test_sdk_client_initialization():
    client = TrustLensClient(base_url="http://localhost:8000", api_key="tl_test_key")
    assert client.base_url == "http://localhost:8000"
    assert client.api_key == "tl_test_key"
    assert client.session.headers.get("X-API-Key") == "tl_test_key"
