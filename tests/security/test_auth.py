"""
Security & Authentication Unit Tests
"""
import pytest
from app.security.authentication import (
    hash_password,
    verify_password,
    create_access_token,
    decode_access_token,
    generate_api_key
)


def test_password_hashing():
    pw = "SuperSecurePassword123!"
    hashed = hash_password(pw)
    assert hashed != pw
    assert verify_password(pw, hashed) is True
    assert verify_password("WrongPassword!", hashed) is False


def test_jwt_token_encode_decode():
    payload = {"sub": "analyst_bob", "role": "analyst"}
    token = create_access_token(payload)
    decoded = decode_access_token(token)
    assert decoded["sub"] == "analyst_bob"
    assert decoded["role"] == "analyst"


def test_api_key_generation():
    key = generate_api_key(prefix="tl_live_")
    assert key.startswith("tl_live_")
    assert len(key) >= 40
