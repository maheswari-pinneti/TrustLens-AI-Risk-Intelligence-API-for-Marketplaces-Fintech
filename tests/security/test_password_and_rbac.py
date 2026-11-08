"""
Security Tests: Password Strength, Brute-Force Throttling & Privilege Escalation Defense
"""
import pytest
from fastapi import HTTPException
from app.api.schemas.auth import UserCreate
from app.api.routes.auth import register
from app.security.authentication import validate_password_strength
from app.security.rate_limiter import LoginThrottler
from app.security.authorization import RoleChecker, require_admin, require_investigator
from app.database.models import User


def test_password_strength_validation():
    # Too short
    valid, msg = validate_password_strength("Short1!")
    assert valid is False
    assert "8 characters" in msg

    # Missing uppercase
    valid, msg = validate_password_strength("nouppercase123!")
    assert valid is False
    assert "uppercase" in msg

    # Missing lowercase
    valid, msg = validate_password_strength("NOLOWERCASE123!")
    assert valid is False
    assert "lowercase" in msg

    # Missing digit
    valid, msg = validate_password_strength("NoDigitsHere!@#")
    assert valid is False
    assert "number" in msg

    # Missing special character
    valid, msg = validate_password_strength("NoSpecialChar123")
    assert valid is False
    assert "special character" in msg

    # Compliant
    valid, msg = validate_password_strength("StrongPass#2026!")
    assert valid is True


def test_login_throttler_lockout():
    throttler = LoginThrottler(max_attempts=3, lockout_seconds=100)
    user_id = "test_user_lockout"

    is_locked, _ = throttler.is_locked(user_id)
    assert is_locked is False

    # 1st failure
    locked, _ = throttler.record_failure(user_id)
    assert locked is False

    # 2nd failure
    locked, _ = throttler.record_failure(user_id)
    assert locked is False

    # 3rd failure triggers lockout
    locked, lockout_sec = throttler.record_failure(user_id)
    assert locked is True
    assert lockout_sec == 100

    # Next check confirms locked
    is_locked, remaining = throttler.is_locked(user_id)
    assert is_locked is True
    assert remaining > 0

    # Successful login resets
    throttler.record_success(user_id)
    is_locked, _ = throttler.is_locked(user_id)
    assert is_locked is False


def test_privilege_escalation_blocked_on_register(db_session):
    # Attempting to self-register as admin must raise 403 Forbidden
    payload = UserCreate(
        username="unauth_admin_try",
        email="unauth_admin@example.com",
        password="SecurePassword123!",
        role="admin"
    )
    with pytest.raises(HTTPException) as exc_info:
        register(payload, db_session)
    assert exc_info.value.status_code == 403
    assert "Privilege escalation" in exc_info.value.detail


def test_weak_password_rejected_on_register(db_session):
    # Attempting to register with a password missing required complexity must raise 400 Bad Request
    payload = UserCreate(
        username="weak_pass_user",
        email="weak@example.com",
        password="alllowercaseonly",
        role="analyst"
    )
    with pytest.raises(HTTPException) as exc_info:
        register(payload, db_session)
    assert exc_info.value.status_code == 400
    assert "Insecure Password" in exc_info.value.detail


def test_role_checker_enforces_permissions():
    admin_user = User(id=1, username="admin1", role="admin")
    analyst_user = User(id=2, username="analyst1", role="analyst")
    client_user = User(id=3, username="client1", role="client")

    # require_admin checks
    assert require_admin(admin_user).username == "admin1"
    with pytest.raises(HTTPException) as exc:
        require_admin(analyst_user)
    assert exc.value.status_code == 403

    # require_investigator checks
    assert require_investigator(admin_user).username == "admin1"
    with pytest.raises(HTTPException) as exc:
        require_investigator(client_user)
    assert exc.value.status_code == 403
