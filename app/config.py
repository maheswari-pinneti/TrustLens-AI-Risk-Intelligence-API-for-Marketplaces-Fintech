"""
Application Configuration Module using Pydantic Settings
"""
from functools import lru_cache
from pathlib import Path
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

    PROJECT_NAME: str = "TrustLens AI Risk Intelligence API"
    VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    API_V1_PREFIX: str = "/api/v1"

    # Security
    SECRET_KEY: str = "trustlens-secret-super-key-change-in-production-marketplaces-fintech"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    ALGORITHM: str = "HS256"
    ADMIN_API_KEY: str = "tl_live_admin_secret_key_998877"

    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 120

    # Database
    DATABASE_URL: str = "sqlite:///./trustlens.db"

    # Storage paths
    DATA_DIR: Path = BASE_DIR / "data"
    UPLOAD_DIR: Path = BASE_DIR / "data" / "uploads"
    FRAUD_KEYWORDS_FILE: Path = BASE_DIR / "data" / "fraud_keywords.txt"
    ML_MODELS_DIR: Path = BASE_DIR / "app" / "ml" / "models"

    # Risk Scoring Weights (sum = 100)
    WEIGHT_PRICE_ANOMALY: float = Field(default=30.0, ge=0.0, le=100.0)
    WEIGHT_FRAUD_KEYWORDS: float = Field(default=25.0, ge=0.0, le=100.0)
    WEIGHT_IMAGE_SIMILARITY: float = Field(default=20.0, ge=0.0, le=100.0)
    WEIGHT_SELLER_REPUTATION: float = Field(default=15.0, ge=0.0, le=100.0)
    WEIGHT_LISTING_BEHAVIOR: float = Field(default=10.0, ge=0.0, le=100.0)

    # Risk Classification Thresholds
    RISK_THRESHOLD_LOW: float = 29.0
    RISK_THRESHOLD_MEDIUM: float = 59.0

    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "*"
    ]


@lru_cache()
def get_settings() -> Settings:
    settings = Settings()
    settings.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    settings.ML_MODELS_DIR.mkdir(parents=True, exist_ok=True)
    return settings
