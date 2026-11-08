"""
Seller Reputation & Historical Risk Analyzer Module
"""
from typing import Dict, Any, Optional


class SellerAnalyzer:
    """
    Evaluates seller trustworthiness using rating, account tenure, historical complaint frequency,
    flagged listing ratio, and identity verification status.
    """

    def analyze(
        self,
        rating: Optional[float] = None,
        account_age_days: Optional[int] = None,
        complaints_count: Optional[int] = None,
        total_listings: Optional[int] = None,
        flagged_listings: Optional[int] = None,
        is_verified: Optional[bool] = None
    ) -> Dict[str, Any]:
        """
        Calculates a composite seller risk score (0.0 to 1.0) and generates explanatory flags.
        Handles missing fields gracefully by defaulting to neutral baseline.
        """
        flags = []
        sub_scores = {}

        # 1. Rating Assessment (Weight: 40%)
        if rating is not None:
            if rating < 2.0:
                rating_score = 1.0
                flags.append(f"Critically low seller rating: {rating:.1f}/5.0 (high buyer dissatisfaction)")
            elif rating < 3.0:
                rating_score = 0.70
                flags.append(f"Poor seller rating: {rating:.1f}/5.0 is well below marketplace average")
            elif rating < 3.8:
                rating_score = 0.35
                flags.append(f"Sub-par seller rating: {rating:.1f}/5.0")
            elif rating < 4.2:
                rating_score = 0.10
            else:
                rating_score = 0.0
            sub_scores["rating"] = rating_score
        else:
            rating_score = 0.20  # Neutral slight uncertainty
            sub_scores["rating"] = rating_score

        # 2. Account Age Assessment (Weight: 25%)
        if account_age_days is not None:
            if account_age_days < 3:
                age_score = 1.0
                flags.append(f"Very new seller account: registered only {account_age_days} day(s) ago (high burner account risk)")
            elif account_age_days < 14:
                age_score = 0.65
                flags.append(f"New seller account: {account_age_days} days old")
            elif account_age_days < 45:
                age_score = 0.25
            else:
                age_score = 0.0
            sub_scores["account_age"] = age_score
        else:
            age_score = 0.15
            sub_scores["account_age"] = age_score

        # 3. Complaints Assessment (Weight: 20%)
        if complaints_count is not None:
            if complaints_count >= 8:
                complaint_score = 1.0
                flags.append(f"Severe complaint history: {complaints_count} reported customer disputes")
            elif complaints_count >= 4:
                complaint_score = 0.65
                flags.append(f"High complaint volume: {complaints_count} customer disputes on record")
            elif complaints_count >= 1:
                complaint_score = 0.25
                flags.append(f"Seller has {complaints_count} recorded complaint(s)")
            else:
                complaint_score = 0.0
            sub_scores["complaints"] = complaint_score
        else:
            complaint_score = 0.0
            sub_scores["complaints"] = complaint_score

        # 4. Flagged Listings Historical Ratio (Weight: 15%)
        if total_listings and total_listings > 0 and flagged_listings is not None:
            flag_ratio = flagged_listings / total_listings
            if flag_ratio > 0.4:
                history_score = 1.0
                flags.append(f"Repeat offender history: {flag_ratio * 100:.1f}% of seller listings previously flagged for fraud")
            elif flag_ratio > 0.2:
                history_score = 0.6
                flags.append(f"Suspicious listing history: {flag_ratio * 100:.1f}% previous listings flagged")
            elif flag_ratio > 0.05:
                history_score = 0.25
            else:
                history_score = 0.0
            sub_scores["listing_history"] = history_score
        else:
            history_score = 0.0
            sub_scores["listing_history"] = history_score

        # Verification Status Modifier
        if is_verified is False:
            flags.append("Unverified merchant identity")
            verification_penalty = 0.10
        else:
            verification_penalty = 0.0

        # Weighted combination
        raw_composite = (
            (rating_score * 0.40) +
            (age_score * 0.25) +
            (complaint_score * 0.20) +
            (history_score * 0.15) +
            verification_penalty
        )
        normalized_score = min(1.0, max(0.0, raw_composite))

        return {
            "normalized_score": round(normalized_score, 4),
            "sub_scores": {k: round(v, 3) for k, v in sub_scores.items()},
            "rating": rating,
            "account_age_days": account_age_days,
            "complaints_count": complaints_count,
            "is_verified": is_verified,
            "flags": flags
        }
