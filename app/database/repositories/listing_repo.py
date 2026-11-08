"""
Listing Database Repository
"""
from datetime import datetime, timezone
from typing import Optional, List, Tuple, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import desc, asc, func
from app.database.models import Listing, RiskAlert


class ListingRepository:

    def __init__(self, db: Session):
        self.db = db

    def get_by_listing_id(self, listing_id: str) -> Optional[Listing]:
        return self.db.query(Listing).filter(Listing.listing_id == listing_id).first()

    def get_by_id(self, id: int) -> Optional[Listing]:
        return self.db.query(Listing).filter(Listing.id == id).first()

    def create(self, listing_data: Dict[str, Any]) -> Listing:
        listing = Listing(**listing_data)
        self.db.add(listing)
        self.db.commit()
        self.db.refresh(listing)
        return listing

    def update_decision(
        self,
        listing_id: str,
        status: str,
        reviewer_id: int,
        review_notes: Optional[str] = None
    ) -> Optional[Listing]:
        listing = self.get_by_listing_id(listing_id)
        if not listing:
            return None
        listing.status = status
        listing.review_notes = review_notes
        listing.reviewed_by_id = reviewer_id
        listing.reviewed_at = datetime.now(timezone.utc)
        self.db.commit()
        self.db.refresh(listing)
        return listing

    def list_listings(
        self,
        skip: int = 0,
        limit: int = 50,
        risk_level: Optional[str] = None,
        category: Optional[str] = None,
        merchant_id: Optional[str] = None,
        status: Optional[str] = None,
        search: Optional[str] = None,
        sort_by: str = "created_at",
        sort_order: str = "desc"
    ) -> Tuple[List[Listing], int]:
        query = self.db.query(Listing)

        if risk_level:
            query = query.filter(Listing.risk_level.ilike(risk_level))
        if category:
            query = query.filter(Listing.category.ilike(f"%{category}%"))
        if merchant_id:
            query = query.filter(Listing.merchant_id == merchant_id)
        if status:
            query = query.filter(Listing.status == status)
        if search:
            pattern = f"%{search}%"
            query = query.filter(
                (Listing.title.ilike(pattern)) |
                (Listing.description.ilike(pattern)) |
                (Listing.listing_id.ilike(pattern))
            )

        total = query.count()

        # Sorting
        sort_column = getattr(Listing, sort_by, Listing.created_at)
        if sort_order.lower() == "asc":
            query = query.order_by(asc(sort_column))
        else:
            query = query.order_by(desc(sort_column))

        items = query.offset(skip).limit(limit).all()
        return items, total

    def get_risk_summary(self) -> Dict[str, Any]:
        total = self.db.query(func.count(Listing.id)).scalar() or 0
        high = self.db.query(func.count(Listing.id)).filter(Listing.risk_level == "High").scalar() or 0
        medium = self.db.query(func.count(Listing.id)).filter(Listing.risk_level == "Medium").scalar() or 0
        low = self.db.query(func.count(Listing.id)).filter(Listing.risk_level == "Low").scalar() or 0
        pending = self.db.query(func.count(Listing.id)).filter(Listing.status == "PENDING_REVIEW").scalar() or 0
        resolved = self.db.query(func.count(Listing.id)).filter(Listing.status.in_(["APPROVED", "REJECTED"])).scalar() or 0
        avg_score = self.db.query(func.avg(Listing.risk_score)).scalar() or 0.0

        return {
            "total_listings_analyzed": total,
            "high_risk_listings": high,
            "medium_risk_listings": medium,
            "low_risk_listings": low,
            "pending_investigation_count": pending,
            "resolved_investigation_count": resolved,
            "average_risk_score": round(float(avg_score), 2)
        }
