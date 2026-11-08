"""
Explainability & Decision Attribution Engine
"""
from typing import Dict, List, Any
from app.core.thresholds import RiskThresholds


class ExplainabilityEngine:
    """
    Translates raw numbers and flags into human-auditable risk explanations,
    ranking factors by severity and generating concrete operational recommendations.
    """

    @staticmethod
    def generate_recommendation(risk_score: float, thresholds: RiskThresholds) -> str:
        if risk_score >= thresholds.auto_reject_cutoff:
            return "AUTO_REJECT"
        elif risk_score > thresholds.auto_approve_cutoff:
            return "MANUAL_REVIEW"
        else:
            return "AUTO_APPROVE"

    @staticmethod
    def rank_contributions(score_breakdown: Dict[str, float]) -> List[Dict[str, Any]]:
        """Identifies top drivers of risk."""
        factor_labels = {
            "price_anomaly_score": ("Price Anomaly", 30.0),
            "fraud_keywords_score": ("Fraud Keywords", 25.0),
            "image_similarity_score": ("Image Similarity", 20.0),
            "seller_reputation_score": ("Seller Reputation", 15.0),
            "listing_behavior_score": ("Listing Behavior", 10.0),
        }

        ranked = []
        for key, (label, max_pts) in factor_labels.items():
            pts = score_breakdown.get(key, 0.0)
            pct_utilization = (pts / max_pts) * 100 if max_pts > 0 else 0
            ranked.append({
                "factor_key": key,
                "factor_name": label,
                "points_contributed": pts,
                "max_possible_points": max_pts,
                "factor_severity_percentage": round(pct_utilization, 1)
            })

        return sorted(ranked, key=lambda x: x["points_contributed"], reverse=True)

    @staticmethod
    def build_summary_explanation(
        risk_level: str,
        risk_score: float,
        ranked_factors: List[Dict[str, Any]],
        flags: List[str]
    ) -> str:
        if risk_score <= 29.0:
            return "Listing exhibits typical e-commerce attributes within safe threshold tolerances. Low risk profile."

        top_factors = [f["factor_name"] for f in ranked_factors if f["points_contributed"] > 5.0]
        if not top_factors and flags:
            top_factors = ["listing attributes"]

        factors_str = ", ".join(top_factors[:3])
        if risk_level == "High":
            return (
                f"High fraud probability ({risk_score:.1f}/100) driven by critical alerts in: {factors_str}. "
                f"Contains {len(flags)} high-confidence risk indicators requiring immediate rejection or escalation."
            )
        else:
            return (
                f"Moderate risk profile ({risk_score:.1f}/100) identified due to anomalies in: {factors_str}. "
                "Listing warrants secondary compliance review before publishing."
            )
