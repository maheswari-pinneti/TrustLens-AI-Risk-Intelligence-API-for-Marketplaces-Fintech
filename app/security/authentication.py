"""
Security & Authentication Layer (JWT, API Keys, Passwords)
"""
import secrets
import re
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any, Union, Tuple
import bcrypt
import jwt
from fastapi import Depends, HTTPException, Security, Request, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials, APIKeyHeader
from sqlalchemy.orm import Session
from app.config import get_settings
from app.database.connection import get_db
from app.database.models import User

settings = get_settings()

security_bearer = HTTPBearer(auto_error=False)
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


def hash_password(plain_password: str) -> str:
    """Hashes password using bcrypt with salt."""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(plain_password.encode("utf-8"), salt).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies plain password against stored bcrypt hash."""
    try:
        return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))
    except Exception:
        return False


def validate_password_strength(plain_password: str) -> Tuple[bool, str]:
    """
    Validates enterprise password complexity:
    - At least 8 characters
    - At least 1 uppercase letter
    - At least 1 lowercase letter
    - At least 1 number
    - At least 1 special character
    """
    if len(plain_password) < 8:
        return False, "Password must be at least 8 characters long."
    if not re.search(r"[A-Z]", plain_password):
        return False, "Password must contain at least one uppercase letter."
    if not re.search(r"[a-z]", plain_password):
        return False, "Password must contain at least one lowercase letter."
    if not re.search(r"\d", plain_password):
        return False, "Password must contain at least one number."
    if not re.search(r"[!@#$%^&*()_+\-=\[\]{};':\"\\|,.<>/?]", plain_password):
        return False, "Password must contain at least one special character (!@#$%^&*...)."
    return True, "Password meets complexity requirements."


def generate_api_key(prefix: str = "tl_live_") -> str:
    """Generates a cryptographically strong API key."""
    return f"{prefix}{secrets.token_hex(24)}"


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Creates signed JWT token with expiration timestamp."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire, "iat": datetime.now(timezone.utc)})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_access_token(token: str) -> Dict[str, Any]:
    """Decodes and validates JWT token signature and expiration."""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication token has expired. Please log in again."
        )
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token credentials."
        )


def get_current_user(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Security(security_bearer),
    api_key: Optional[str] = Security(api_key_header),
    db: Session = Depends(get_db)
) -> User:
    """
    Validates Bearer JWT token, X-API-Key header, or ?api_key= query parameter.
    Returns authenticated database User object.
    """
    # 1. Try API Key (Header or Query Param)
    effective_api_key = api_key or request.query_params.get("api_key")
    if effective_api_key:
        if effective_api_key == settings.ADMIN_API_KEY:
            # System root service user
            admin_user = db.query(User).filter(User.username == "admin").first()
            if not admin_user:
                admin_user = User(
                    username="admin",
                    email="admin@trustlens.internal",
                    hashed_password=hash_password("AdminSecurePass123!"),
                    role="admin",
                    api_key=settings.ADMIN_API_KEY,
                    is_active=True
                )
                db.add(admin_user)
                db.commit()
                db.refresh(admin_user)
            return admin_user

        user_by_key = db.query(User).filter(User.api_key == effective_api_key, User.is_active == True).first()
        if user_by_key:
            return user_by_key

    # 2. Try JWT Bearer Token
    if credentials:
        token = credentials.credentials
        payload = decode_access_token(token)
        username: str = payload.get("sub")
        if not username:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token payload missing subject identity."
            )
        user = db.query(User).filter(User.username == username, User.is_active == True).first()
        if user:
            return user

    # Neither provided or valid
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Missing or invalid authentication credentials. Provide a valid Bearer token or X-API-Key header.",
        headers={"WWW-Authenticate": "Bearer"}
    )
