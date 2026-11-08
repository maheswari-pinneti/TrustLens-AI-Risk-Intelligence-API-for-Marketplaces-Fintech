"""
Reporting & Risk Intelligence Analytics Router
"""
import io
import csv
from fastapi import APIRouter, Depends, Response, HTTPException, Query
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.api.schemas.response import RiskSummaryResponse
from app.services.report_service import ReportService
from app.services.feedback_service import FeedbackService
from app.services.alert_service import AlertService
from app.database.repositories.audit_repo import AuditRepository
from app.database.models import Listing
from app.security.authorization import require_admin, require_investigator
from app.database.models import User

router = APIRouter(tags=["Analytics & Reports"])


@router.get("/risk/summary", response_model=RiskSummaryResponse, summary="Executive Risk Analytics Summary")
def get_risk_summary(db: Session = Depends(get_db)):
    service = ReportService(db)
    return service.generate_risk_summary()


@router.get("/reports", summary="Audit & Comprehensive Risk Reports")
def get_reports(db: Session = Depends(get_db)):
    service = ReportService(db)
    return service.generate_risk_summary()


@router.get("/reports/export-csv", summary="Export Evaluated Listings as CSV")
def export_csv(
    db: Session = Depends(get_db),
    user: User = Depends(require_investigator)
):
    listings = db.query(Listing).all()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "listing_id", "merchant_id", "title", "category",
        "price", "market_price", "risk_score", "risk_level",
        "recommendation", "status", "created_at"
    ])

    for l in listings:
        writer.writerow([
            l.listing_id,
            l.merchant_id,
            l.title,
            l.category,
            l.price,
            l.market_price or "",
            l.risk_score,
            l.risk_level,
            l.evidence.get("recommendation", "") if isinstance(l.evidence, dict) else "",
            l.status,
            l.created_at.isoformat() if l.created_at else ""
        ])

    response = Response(content=output.getvalue(), media_type="text/csv")
    response.headers["Content-Disposition"] = "attachment; filename=trustlens_risk_audit_export.csv"
    return response


@router.get("/reports/ml-vs-rules", summary="Comparative ML vs Rule-Based Detection Analysis")
def get_ml_vs_rules(db: Session = Depends(get_db)):
    """
    Compares rule-based scoring distributions against ML model probabilities.
    """
    listings = db.query(Listing).filter(Listing.ml_fraud_probability != None).limit(100).all()
    comparison_data = []
    concordant = 0
    discordant = 0

    for l in listings:
        rule_high = l.risk_score >= 60.0
        ml_high = (l.ml_fraud_probability or 0.0) >= 0.5
        is_agree = (rule_high == ml_high)
        if is_agree:
            concordant += 1
        else:
            discordant += 1

        comparison_data.append({
            "listing_id": l.listing_id,
            "title": l.title,
            "rule_risk_score": l.risk_score,
            "rule_risk_level": l.risk_level,
            "ml_fraud_probability": round((l.ml_fraud_probability or 0.0) * 100, 1),
            "ml_prediction": l.ml_prediction,
            "agreement": is_agree
        })

    total = concordant + discordant
    agreement_rate = (concordant / total * 100) if total > 0 else 100.0

    return {
        "total_analyzed": total,
        "concordant_count": concordant,
        "discordant_count": discordant,
        "agreement_rate_pct": round(agreement_rate, 2),
        "comparison_samples": comparison_data[:25]
    }


@router.get("/reports/feedback-stats", summary="Get Active Learning Feedback Statistics")
def get_feedback_stats(db: Session = Depends(get_db)):
    """Returns the volume of human investigator decisions available for model retraining."""
    svc = FeedbackService(db)
    return svc.get_feedback_statistics()


@router.post("/reports/retrain", summary="Trigger Active Learning Continuous Retraining")
def trigger_retrain(
    db: Session = Depends(get_db),
    user: User = Depends(require_admin)
):
    """
    Ingests ground-truth decisions submitted by compliance investigators,
    augments training vectors, and updates the Random Forest model.
    Requires Administrator privileges.
    """
    svc = FeedbackService(db)
    return svc.trigger_retraining()


@router.get("/alerts", summary="List Security & High Risk Alerts")
def list_alerts(
    limit: int = Query(default=20, ge=1, le=100),
    unresolved_only: bool = Query(default=False),
    db: Session = Depends(get_db),
    user: User = Depends(require_investigator)
):
    """Retrieves operational security and high-risk alerts flagged by the detection engine."""
    svc = AlertService(db)
    return svc.get_recent_alerts(limit=limit, unresolved_only=unresolved_only)


@router.patch("/alerts/{alert_id}/resolve", summary="Resolve Security Risk Alert")
def resolve_alert(
    alert_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(require_investigator)
):
    """Marks an active high-risk security alert as resolved with investigator audit logging."""
    svc = AlertService(db)
    alert = svc.resolve_alert(alert_id)
    if not alert:
        raise HTTPException(status_code=404, detail=f"Alert '{alert_id}' not found.")

    audit = AuditRepository(db)
    audit.log(
        action="RESOLVE_ALERT",
        resource_type="RiskAlert",
        resource_id=alert_id,
        user_id=user.id,
        username=user.username,
        details={"status": "RESOLVED"}
    )
    return {"message": f"Alert '{alert_id}' marked as resolved.", "alert_id": alert_id, "is_resolved": True}
