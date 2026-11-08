"""
Health Check & System Diagnostics Router
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.config import get_settings
from app.database.connection import get_db
from app.api.schemas.response import HealthResponse
from app.ml.predict import MLFraudPredictor

router = APIRouter(tags=["Health & Diagnostics"])
settings = get_settings()
ml_predictor = MLFraudPredictor()


@router.get("/health", response_model=HealthResponse, summary="System Health & Diagnostic Check")
def health_check(db: Session = Depends(get_db)):
    """
    Returns API health, database connectivity, and ML model loaded status.
    """
    db_ok = False
    try:
        db.execute(text("SELECT 1"))
        db_ok = True
    except Exception:
        db_ok = False

    return HealthResponse(
        status="HEALTHY" if db_ok else "DEGRADED",
        environment=settings.ENVIRONMENT,
        version=settings.VERSION,
        database_connected=db_ok,
        ml_model_loaded=ml_predictor.is_loaded
    )
