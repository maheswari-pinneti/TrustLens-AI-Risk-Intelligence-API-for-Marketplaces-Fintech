"""
Webhook & Event Notification Dispatcher Service
Dispatches cryptographically signed HMAC-SHA256 event payloads to downstream platforms.
"""
import hmac
import hashlib
import json
import uuid
from datetime import datetime, timezone
from typing import Dict, Any, Optional, Tuple
import httpx
from app.config import get_settings

settings = get_settings()


class WebhookService:
    """
    Constructs and signs event payloads for marketplace and payment gateway callbacks.
    """

    def __init__(self, secret_key: Optional[str] = None):
        self.secret_key = secret_key or settings.SECRET_KEY

    def construct_event_payload(self, event_type: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Builds a standardized event envelope with UUID and UTC timestamp."""
        return {
            "event_id": f"evt_{uuid.uuid4().hex[:16]}",
            "event_type": event_type,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "data": data
        }

    def compute_signature(self, payload_bytes: bytes) -> str:
        """Computes HMAC-SHA256 signature over payload bytes."""
        signature = hmac.new(
            self.secret_key.encode("utf-8"),
            payload_bytes,
            hashlib.sha256
        ).hexdigest()
        return f"sha256={signature}"

    def verify_signature(self, payload_bytes: bytes, header_signature: str) -> bool:
        """Constant-time verification of webhook signature against secret key."""
        if not header_signature or not header_signature.startswith("sha256="):
            return False
        expected = self.compute_signature(payload_bytes)
        return hmac.compare_digest(expected, header_signature)

    def dispatch(
        self,
        url: str,
        event_type: str,
        data: Dict[str, Any],
        timeout: float = 5.0
    ) -> Tuple[bool, Optional[int], str]:
        """
        Sends signed JSON payload to consumer webhook endpoint.
        Returns (success: bool, status_code: Optional[int], message: str).
        """
        payload = self.construct_event_payload(event_type, data)
        payload_bytes = json.dumps(payload, separators=(",", ":")).encode("utf-8")
        signature = self.compute_signature(payload_bytes)

        headers = {
            "Content-Type": "application/json",
            "User-Agent": f"TrustLens-Webhook-Agent/{settings.VERSION}",
            "X-TrustLens-Signature": signature,
            "X-TrustLens-Event": event_type
        }

        try:
            with httpx.Client(timeout=timeout) as client:
                response = client.post(url, content=payload_bytes, headers=headers)
                success = (200 <= response.status_code < 300)
                return success, response.status_code, f"Response: {response.status_code}"
        except Exception as e:
            return False, None, f"Webhook delivery error: {str(e)}"
