"""
Reporting & Risk Intelligence Analytics Aggregation Service
"""
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from app.database.models import Listing, Merchant, RiskAlert
from app.database.repositories.listing_repo import ListingRepository
from app.services.alert_service import AlertService


class ReportService:

    def __init__(self, db: Session):
        self.db = db
        self.listing_repo = ListingRepository(db)
        self.alert_service = AlertService(db)

    def generate_risk_summary(self) -> Dict[str, Any]:
        """Aggregates system-wide intelligence KPIs."""
        summary = self.listing_repo.get_risk_summary()
        merchants_count = self.db.query(func.count(Merchant.id)).scalar() or 0
        summary["total_merchants_tracked"] = merchants_count

        # Category risk distribution
        category_rows = self.db.query(
            Listing.category,
            func.count(Listing.id).label("count"),
            func.avg(Listing.risk_score).label("avg_risk")
        ).group_by(Listing.category).all()

        category_dist = [
            {
                "category": row[0] or "General",
                "count": row[1],
                "avg_risk": round(float(row[2]), 1) if row[2] else 0.0
            }
            for row in category_rows
        ]
        summary["category_risk_distribution"] = category_dist

        # Top fraud keyword occurrences from JSON flags
        all_listings = self.db.query(Listing.flags).filter(Listing.flags != None).all()
        kw_counts: Dict[str, int] = {}
        for (flags_list,) in all_listings:
            if isinstance(flags_list, list):
                for flag in flags_list:
                    if "Fraud keyword detected:" in flag:
                        # Extract keyword name
                        try:
                            kw = flag.split("'")[1]
                            kw_counts[kw] = kw_counts.get(kw, 0) + 1
                        except Exception:
                            pass

        top_kws = [
            {"keyword": k, "occurrences": v}
            for k, v in sorted(kw_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        ]
        summary["top_fraud_keywords"] = top_kws

        # Recent Alerts
        summary["recent_alerts"] = self.alert_service.get_recent_alerts(limit=10)

        return summary
