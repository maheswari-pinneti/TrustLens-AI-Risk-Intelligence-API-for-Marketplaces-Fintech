"""
Unit tests for Keyword Fraud & Counterfeit Detector
"""
import pytest
from app.detectors.keyword_detector import KeywordDetector


def test_clean_text_no_flags(keyword_detector):
    result = keyword_detector.analyze(
        title="Apple iPhone 15 Pro Max 256GB Titanium",
        description="Brand new in original sealed retail packaging with official warranty."
    )
    assert result["normalized_score"] == 0.0
    assert result["matches_count"] == 0
    assert len(result["flags"]) == 0


def test_high_severity_replica_keywords(keyword_detector):
    result = keyword_detector.analyze(
        title="Nike Jordan 1 Replica Shoes",
        description="High quality 1:1 replica, unauthorized authentic fake sneaker. Whatsapp me!"
    )
    assert result["normalized_score"] >= 0.8
    assert result["matches_count"] >= 3
    assert any("replica" in flag.lower() for flag in result["flags"])
    assert any("fake" in flag.lower() for flag in result["flags"])


def test_off_platform_payment_keywords(keyword_detector):
    result = keyword_detector.analyze(
        title="MacBook Pro M3",
        description="Must pay via wire transfer only or friends and family paypal. Contact outside app."
    )
    assert result["normalized_score"] >= 0.7
    assert any("wire transfer only" in flag for flag in result["flags"])
    assert any("contact outside app" in flag for flag in result["flags"])


def test_case_insensitivity_and_punctuation(keyword_detector):
    result = keyword_detector.analyze(
        title="SUPERCLONE WATCH !!!",
        description="LOOKS AUTHENTIC, 1:1 REPLICA MIRROR QUALITY."
    )
    assert result["normalized_score"] >= 0.8
    assert "superclone" in result["matched_keywords"]
