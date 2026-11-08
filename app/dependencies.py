"""
FastAPI Global Dependency Injection Providers
"""
from fastapi import Depends
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.database.models import User
from app.security.authentication import get_current_user
from app.services.analysis_service import AnalysisService
from app.services.merchant_service import MerchantService
from app.services.report_service import ReportService


def get_analysis_service(db: Session = Depends(get_db)) -> AnalysisService:
    return AnalysisService(db)


def get_merchant_service(db: Session = Depends(get_db)) -> MerchantService:
    return MerchantService(db)


def get_report_service(db: Session = Depends(get_db)) -> ReportService:
    return ReportService(db)
