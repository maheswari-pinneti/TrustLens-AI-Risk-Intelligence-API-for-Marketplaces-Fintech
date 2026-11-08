"""
Authentication & Access Control Router
Includes Brute-Force Throttling, Password Strength Verification, and RBAC Privilege Escalation Defense.
"""
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.database.models import User
from app.database.repositories.user_repo import UserRepository
from app.api.schemas.auth import LoginRequest, Token, UserCreate, UserResponse, APIKeyResponse
from app.security.authentication import (
    verify_password,
    create_access_token,
    get_current_user,
    hash_password,
    generate_api_key,
    validate_password_strength,
)
from app.security.authorization import require_admin
from app.security.rate_limiter import login_throttler
from app.security.sanitizer import sanitize_text

router = APIRouter(prefix="/auth", tags=["Authentication & Access"])


@router.post("/login", response_model=Token, summary="Authenticate & obtain JWT Token")
def login(req: LoginRequest, request: Request, db: Session = Depends(get_db)):
    """Logs in with username and password, returning a JWT bearer token with brute-force defense."""
    client_ip = request.client.host if request.client else "unknown"
    identifier = f"{client_ip}:{req.username}"

    # 1. Check if identifier is currently throttled/locked
    is_locked, remaining_seconds = login_throttler.is_locked(identifier)
    if is_locked:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Too many failed login attempts. Account temporarily locked for security. Try again in {remaining_seconds} seconds.",
            headers={"Retry-After": str(remaining_seconds)}
        )

    user_repo = UserRepository(db)
    user = user_repo.get_by_username(req.username) or user_repo.get_by_email(req.username)

    # Auto-seed default admin if first time
    if not user and req.username == "admin" and req.password == "AdminSecurePass123!":
        user = user_repo.create("admin", "admin@trustlens.internal", "AdminSecurePass123!", role="admin")

    if not user or not verify_password(req.password, user.hashed_password):
        locked_now, lockout_sec = login_throttler.record_failure(identifier)
        if locked_now:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Maximum failed attempts exceeded. Temporarily locked for {lockout_sec} seconds.",
                headers={"Retry-After": str(lockout_sec)}
            )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials. Verify username and password."
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is deactivated."
        )

    # Login succeeded - clear failed attempt history
    login_throttler.record_success(identifier)

    token = create_access_token(data={"sub": user.username, "role": user.role})
    return Token(
        access_token=token,
        token_type="bearer",
        expires_in=1440 * 60,
        role=user.role,
        username=user.username,
        api_key=user.api_key
    )


@router.post("/register", response_model=UserResponse, summary="Register user account")
def register(req: UserCreate, db: Session = Depends(get_db)):
    """
    Registers a new user (analyst or client).
    Enforces strong password policy and blocks self-privilege escalation to admin/investigator.
    """
    # 1. Enforce password complexity policy
    is_strong, reason = validate_password_strength(req.password)
    if not is_strong:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Insecure Password: {reason}"
        )

    # 2. Block Privilege Escalation (disallow self-assignment of admin/investigator)
    normalized_role = req.role.strip().lower()
    if normalized_role in ["admin", "investigator"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Privilege escalation prohibited: Role '{req.role}' cannot be self-provisioned. Contact an administrator."
        )

    # Default to analyst if an unknown role was passed
    if normalized_role not in ["analyst", "client"]:
        normalized_role = "analyst"

    clean_username = sanitize_text(req.username)
    user_repo = UserRepository(db)
    if user_repo.get_by_username(clean_username):
        raise HTTPException(status_code=400, detail="Username already registered")
    if user_repo.get_by_email(req.email):
        raise HTTPException(status_code=400, detail="Email already registered")

    user = user_repo.create(clean_username, req.email, req.password, role=normalized_role)
    return user


@router.get("/me", response_model=UserResponse, summary="Current user profile")
def get_me(user: User = Depends(get_current_user)):
    return user


@router.post("/api-key", response_model=APIKeyResponse, summary="Regenerate API Key")
def refresh_api_key(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    user_repo = UserRepository(db)
    new_key = user_repo.regenerate_api_key(user.id)
    return APIKeyResponse(
        api_key=new_key,
        created_at=user.updated_at,
        role=user.role
    )
