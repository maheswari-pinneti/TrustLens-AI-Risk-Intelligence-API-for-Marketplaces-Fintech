"""
Merchant Risk Intelligence & Profile Management Service
"""
from typing import Optional, List, Dict, Any, Tuple
from sqlalchemy.orm import Session
from app.database.models import Merchant, Listing
from app.database.repositories.merchant_repo import MerchantRepository


class MerchantService:

    def __init__(self, db: Session):
        self.db = db
        self.repo = MerchantRepository(db)

    def get_merchant(self, merchant_id: str) -> Optional[Merchant]:
        return self.repo.get_by_merchant_id(merchant_id)

    def list_merchants(
        self,
        skip: int = 0,
        limit: int = 50,
        risk_level: Optional[str] = None,
        search: Optional[str] = None
    ) -> Tuple[List[Merchant], int]:
        return self.repo.list_merchants(skip, limit, risk_level, search)

    def update_merchant_risk_profile(self, merchant_id: str) -> Optional[Merchant]:
        """
        Recalculates merchant risk score based on their aggregate listings,
        flagged listings ratio, customer complaints, and account tenure.
        """
        merchant = self.repo.get_by_merchant_id(merchant_id)
        if not merchant:
            return None

        # Fetch all listings from merchant
        listings = self.db.query(Listing).filter(Listing.merchant_id == merchant_id).all()
        total_listings = len(listings)
        flagged_listings = sum(1 for l in listings if l.risk_level == "High")

        merchant.total_listings = total_listings
        merchant.flagged_listings = flagged_listings

        # Compute dynamic seller risk
        rating_penalty = max(0.0, (5.0 - merchant.rating) * 12.0)
        complaint_penalty = min(30.0, merchant.complaints_count * 5.0)
        
        flag_ratio = (flagged_listings / total_listings) if total_listings > 0 else 0.0
        flag_penalty = flag_ratio * 40.0

        age_penalty = 15.0 if merchant.account_age_days < 7 else (8.0 if merchant.account_age_days < 30 else 0.0)
        unverified_penalty = 10.0 if not merchant.is_verified else 0.0

        computed_risk = rating_penalty + complaint_penalty + flag_penalty + age_penalty + unverified_penalty
        merchant.risk_score = round(min(100.0, max(5.0, computed_risk)), 1)

        if merchant.risk_score <= 29.0:
            merchant.risk_level = "Low"
        elif merchant.risk_score <= 59.0:
            merchant.risk_level = "Medium"
        else:
            merchant.risk_level = "High"

        self.db.commit()
        self.db.refresh(merchant)
        return merchant
