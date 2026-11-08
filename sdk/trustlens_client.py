"""
TrustLens Python SDK Client
Enables marketplaces, fintechs, and merchant platforms to easily integrate
real-time fraud risk intelligence into their Python backends.
"""
from typing import Dict, Any, Optional, List
import requests


class TrustLensError(Exception):
    """Base exception raised for TrustLens API errors."""
    pass


class RiskAnalysisResult:
    """Convenience wrapper for risk scoring responses."""

    def __init__(self, data: Dict[str, Any]):
        self.raw = data
        self.listing_id: str = data.get("listing_id", "")
        self.title: str = data.get("title", "")
        self.risk_score: float = data.get("risk_score", 0.0)
        self.risk_level: str = data.get("risk_level", "Low")
        self.recommendation: str = data.get("recommendation", "MANUAL_REVIEW")
        self.ml_prediction: Optional[str] = data.get("ml_prediction")
        self.ml_fraud_probability: Optional[float] = data.get("ml_fraud_probability")
        self.flags: List[str] = data.get("flags", [])
        self.score_breakdown: Dict[str, float] = data.get("score_breakdown", {})
        self.evidence: Dict[str, Any] = data.get("evidence", {})

    @property
    def is_high_risk(self) -> bool:
        return self.risk_level == "High" or self.risk_score >= 60.0

    @property
    def is_auto_approved(self) -> bool:
        return self.recommendation == "AUTO_APPROVE"

    def __repr__(self) -> str:
        return f"<RiskAnalysisResult id='{self.listing_id}' score={self.risk_score} level='{self.risk_level}'>"


class TrustLensClient:
    """Official TrustLens Python SDK Client."""

    def __init__(
        self,
        base_url: str = "http://127.0.0.1:8000",
        api_key: Optional[str] = None,
        timeout: int = 10
    ):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.timeout = timeout
        self.session = requests.Session()
        if self.api_key:
            self.session.headers.update({"X-API-Key": self.api_key})

    def _request(self, method: str, path: str, **kwargs) -> Dict[str, Any]:
        url = f"{self.base_url}{path}"
        try:
            resp = self.session.request(method, url, timeout=self.timeout, **kwargs)
            if not resp.ok:
                try:
                    err_payload = resp.json()
                    detail = err_payload.get("detail", resp.text)
                except Exception:
                    detail = resp.text
                raise TrustLensError(f"HTTP {resp.status_code}: {detail}")
            return resp.json()
        except requests.RequestException as e:
            raise TrustLensError(f"Connection failure to {url}: {e}") from e

    def health(self) -> Dict[str, Any]:
        """Checks API health and machine learning model loaded status."""
        return self._request("GET", "/health")

    def analyze(
        self,
        title: str,
        description: str,
        price: float,
        market_price: Optional[float] = None,
        category: str = "General",
        merchant_id: Optional[str] = None,
        seller_rating: Optional[float] = None,
        seller_account_age_days: Optional[int] = None,
        seller_complaints_count: Optional[int] = None,
        persist: bool = True
    ) -> RiskAnalysisResult:
        """
        Executes real-time multi-dimensional risk evaluation on a listing.
        """
        payload = {
            "title": title,
            "description": description,
            "price": price,
            "market_price": market_price,
            "category": category,
            "merchant_id": merchant_id,
            "seller_rating": seller_rating,
            "seller_account_age_days": seller_account_age_days,
            "seller_complaints_count": seller_complaints_count
        }
        res_data = self._request("POST", f"/api/v1/analyze?persist={str(persist).lower()}", json=payload)
        return RiskAnalysisResult(res_data)

    def get_risk_summary(self) -> Dict[str, Any]:
        """Retrieves system-wide executive fraud KPI statistics."""
        return self._request("GET", "/api/v1/risk/summary")
