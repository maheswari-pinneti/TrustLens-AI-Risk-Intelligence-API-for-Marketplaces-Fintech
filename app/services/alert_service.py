"""
Alert and Incident Notification Service
"""
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.database.models import RiskAlert


class AlertService:

    def __init__(self, db: Session):
        self.db = db

    def create_alert_if_needed(
        self,
        listing_id: str,
        risk_score: float,
        risk_level: str,
        flags: List[str],
        merchant_id: Optional[str] = None
    ) -> Optional[RiskAlert]:
        """Triggers an alert if risk score is high/critical."""
        if risk_score >= 60.0:
            severity = "CRITICAL" if risk_score >= 80.0 else "HIGH"
            top_flag = flags[0] if flags else "High risk composite score"
            message = f"High Risk Alert ({risk_score:.1f}/100): {top_flag}"

            alert = RiskAlert(
                severity=severity,
                message=message,
                listing_id=listing_id,
                merchant_id=merchant_id,
                is_resolved=False
            )
            self.db.add(alert)
            self.db.commit()
            self.db.refresh(alert)
            return alert
        return None

    def get_recent_alerts(self, limit: int = 10, unresolved_only: bool = False) -> List[Dict[str, Any]]:
        query = self.db.query(RiskAlert)
        if unresolved_only:
            query = query.filter(RiskAlert.is_resolved == False)
        alerts = query.order_by(desc(RiskAlert.created_at)).limit(limit).all()
        return [
            {
                "id": a.id,
                "alert_id": a.alert_id,
                "severity": a.severity,
                "message": a.message,
                "listing_id": a.listing_id,
                "merchant_id": a.merchant_id,
                "is_resolved": a.is_resolved,
                "created_at": a.created_at.isoformat() if a.created_at else None
            }
            for a in alerts
        ]

    def resolve_alert(self, alert_id: str) -> Optional[RiskAlert]:
        """Marks a security/risk alert as resolved."""
        alert = self.db.query(RiskAlert).filter(RiskAlert.alert_id == alert_id).first()
        if alert:
            alert.is_resolved = True
            self.db.commit()
            self.db.refresh(alert)
            return alert
        return None
