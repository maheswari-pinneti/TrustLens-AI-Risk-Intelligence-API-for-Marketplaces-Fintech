"""
Authentication and User Schemas
"""
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, ConfigDict


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    role: str
    username: str
    api_key: Optional[str] = None


class TokenData(BaseModel):
    username: Optional[str] = None
    role: Optional[str] = None


class LoginRequest(BaseModel):
    username: str = Field(..., description="Username or email", examples=["admin"])
    password: str = Field(..., description="User password", examples=["AdminSecurePass123!"])


class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=100)
    role: str = Field(default="analyst", description="admin, investigator, analyst, client")


class UserResponse(BaseModel):
    id: int
    uuid: str
    username: str
    email: str
    role: str
    api_key: Optional[str] = None
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class APIKeyResponse(BaseModel):
    api_key: str
    created_at: datetime
    role: str
