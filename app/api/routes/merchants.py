"""
Merchant Intelligence API Router
"""
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.database.models import User
from app.api.schemas.request import MerchantCreateRequest
from app.api.schemas.response import MerchantResponse, ListingResponse
from app.database.repositories.merchant_repo import MerchantRepository
from app.database.repositories.listing_repo import ListingRepository
from app.services.merchant_service import MerchantService
from app.security.authentication import get_current_user

router = APIRouter(prefix="/merchants", tags=["Merchant Risk Intelligence"])


@router.get("", summary="List & Search Tracked Merchants")
def list_merchants(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
    risk_level: Optional[str] = Query(default=None, description="Low, Medium, or High"),
    search: Optional[str] = Query(default=None),
    db: Session = Depends(get_db)
):
    service = MerchantService(db)
    items, total = service.list_merchants(skip=skip, limit=limit, risk_level=risk_level, search=search)
    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "items": [MerchantResponse.from_orm(m) for m in items]
    }


@router.get("/{merchant_id}", summary="Get Merchant Profile & Associated Listings")
def get_merchant_profile(merchant_id: str, db: Session = Depends(get_db)):
    service = MerchantService(db)
    merchant = service.get_merchant(merchant_id)
    if not merchant:
        raise HTTPException(status_code=404, detail=f"Merchant '{merchant_id}' not found.")

    listing_repo = ListingRepository(db)
    listings, total_listings = listing_repo.list_listings(merchant_id=merchant_id, limit=20)

    return {
        "merchant": MerchantResponse.from_orm(merchant),
        "recent_listings": [ListingResponse.from_orm(l) for l in listings],
        "total_listings_count": total_listings
    }


@router.post("", response_model=MerchantResponse, summary="Register or Update Merchant Profile")
def create_merchant(
    req: MerchantCreateRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    repo = MerchantRepository(db)
    merchant = repo.create_or_update(req.dict())
    return MerchantResponse.from_orm(merchant)
