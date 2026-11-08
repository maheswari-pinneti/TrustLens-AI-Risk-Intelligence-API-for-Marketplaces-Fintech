"""
Unit tests for Behavioral Urgency & Off-Platform Pattern Detector
"""
import pytest
from app.detectors.behavior_detector import BehaviorDetector


def test_normal_behavior(behavior_detector):
    result = behavior_detector.analyze(
        title="Apple MacBook Pro 16 inch Space Black",
        description="Mint condition laptop with charger and protective case."
    )
    assert result["normalized_score"] == 0.0
    assert len(result["flags"]) == 0


def test_excessive_shouting_and_urgency(behavior_detector):
    result = behavior_detector.analyze(
        title="MUST GO TODAY BUY NOW BEST OFFER EVER!!!!!",
        description="Hurry up and buy today only!!!!!"
    )
    assert result["normalized_score"] >= 0.4
    assert any("shouting" in f.lower() for f in result["flags"])
    assert any("urgency" in f.lower() for f in result["flags"])


def test_contact_details_leakage(behavior_detector):
    result = behavior_detector.analyze(
        title="PlayStation 5 Console",
        description="Do not buy here. Call me at 555-123-4567 or email deals@offplatform.com for discount."
    )
    assert result["normalized_score"] >= 0.6
    assert any("phone" in f.lower() for f in result["flags"])
    assert any("email" in f.lower() for f in result["flags"])
