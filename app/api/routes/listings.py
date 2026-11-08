"""
Listings Management & Investigation Endpoints
"""
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.database.models import User
from app.api.schemas.request import ListingCreateRequest, InvestigationDecisionRequest
from app.api.schemas.response import ListingResponse, AnalyzeResponse
from app.database.repositories.listing_repo import ListingRepository
from app.database.repositories.audit_repo import AuditRepository
from app.services.analysis_service import AnalysisService
from app.security.authorization import require_investigator, require_any_authenticated
from app.security.authentication import get_current_user

router = APIRouter(prefix="/listings", tags=["Listings & Investigations"])


@router.get("", summary="List & Filter Evaluated Marketplace Listings")
def list_listings(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
    risk_level: Optional[str] = Query(default=None, description="Low, Medium, or High"),
    category: Optional[str] = Query(default=None),
    merchant_id: Optional[str] = Query(default=None),
    status: Optional[str] = Query(default=None, description="PENDING_REVIEW, APPROVED, REJECTED, ESCALATED"),
    search: Optional[str] = Query(default=None),
    sort_by: str = Query(default="created_at", description="created_at, risk_score, price"),
    sort_order: str = Query(default="desc", description="asc or desc"),
    db: Session = Depends(get_db)
):
    repo = ListingRepository(db)
    items, total = repo.list_listings(
        skip=skip,
        limit=limit,
        risk_level=risk_level,
        category=category,
        merchant_id=merchant_id,
        status=status,
        search=search,
        sort_by=sort_by,
        sort_order=sort_order
    )
    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "items": [ListingResponse.from_orm(item) for item in items]
    }


@router.get("/{listing_id}", response_model=ListingResponse, summary="Get Listing Risk Investigation Details")
def get_listing(listing_id: str, db: Session = Depends(get_db)):
    repo = ListingRepository(db)
    listing = repo.get_by_listing_id(listing_id)
    if not listing:
        raise HTTPException(status_code=404, detail=f"Listing '{listing_id}' not found.")
    return ListingResponse.from_orm(listing)


@router.post("", response_model=AnalyzeResponse, summary="Create and Evaluate New Listing")
def create_listing(
    request: ListingCreateRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    service = AnalysisService(db)
    result = service.analyze_listing(request, persist=True)
    audit = AuditRepository(db)
    audit.log(
        action="CREATE_LISTING",
        resource_type="Listing",
        resource_id=result.listing_id,
        user_id=user.id,
        username=user.username,
        details={"risk_score": result.risk_score, "risk_level": result.risk_level}
    )
    return result


@router.patch("/{listing_id}/decision", response_model=ListingResponse, summary="Investigator Action Decision")
def update_decision(
    listing_id: str,
    req: InvestigationDecisionRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """
    Submits human investigator disposition (APPROVED, REJECTED, ESCALATED).
    """
    repo = ListingRepository(db)
    listing = repo.update_decision(
        listing_id=listing_id,
        status=req.status,
        reviewer_id=user.id,
        review_notes=req.review_notes
    )
    if not listing:
        raise HTTPException(status_code=404, detail=f"Listing '{listing_id}' not found.")

    audit = AuditRepository(db)
    audit.log(
        action="INVESTIGATOR_DECISION",
        resource_type="Listing",
        resource_id=listing_id,
        user_id=user.id,
        username=user.username,
        details={"status": req.status, "notes": req.review_notes}
    )

    return ListingResponse.from_orm(listing)
