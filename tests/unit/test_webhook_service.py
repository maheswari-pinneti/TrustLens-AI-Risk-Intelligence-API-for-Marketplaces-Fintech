"""
Unit Tests for Webhook & Event Notification Dispatcher Service
"""
import json
from unittest.mock import patch, MagicMock
from app.services.webhook_service import WebhookService


def test_event_envelope_structure():
    svc = WebhookService(secret_key="test_secret_key_123")
    payload = svc.construct_event_payload(
        event_type="listing.risk.critical",
        data={"listing_id": "list_999", "risk_score": 88.5}
    )

    assert payload["event_type"] == "listing.risk.critical"
    assert payload["event_id"].startswith("evt_")
    assert "timestamp" in payload
    assert payload["data"]["listing_id"] == "list_999"
    assert payload["data"]["risk_score"] == 88.5


def test_signature_generation_and_verification():
    secret = "my_crypto_secret_for_fintech_compliance"
    svc = WebhookService(secret_key=secret)

    body = b'{"event":"test","amount":100}'
    sig = svc.compute_signature(body)

    assert sig.startswith("sha256=")
    assert len(sig) == 7 + 64  # "sha256=" + 64 hex chars

    # Verifies correctly
    assert svc.verify_signature(body, sig) is True

    # Tampered body fails
    tampered_body = b'{"event":"test","amount":999}'
    assert svc.verify_signature(tampered_body, sig) is False

    # Wrong signature fails
    assert svc.verify_signature(body, "sha256=0000000000000000000000000000000000000000000000000000000000000000") is False

    # Malformed header fails
    assert svc.verify_signature(body, "invalidsig") is False


def test_wrong_secret_fails_verification():
    svc1 = WebhookService(secret_key="secret_one")
    svc2 = WebhookService(secret_key="secret_two")

    body = b'{"data":"confidential"}'
    sig1 = svc1.compute_signature(body)

    # Verifying with wrong secret fails
    assert svc2.verify_signature(body, sig1) is False


def test_mock_webhook_dispatch_success():
    svc = WebhookService(secret_key="test_secret")

    mock_resp = MagicMock()
    mock_resp.status_code = 200

    with patch("httpx.Client.post", return_value=mock_resp) as mock_post:
        success, code, msg = svc.dispatch(
            url="https://webhook.site/marketplace-alerts",
            event_type="listing.risk.high",
            data={"listing_id": "lst_abc", "score": 75.0}
        )

        assert success is True
        assert code == 200
        assert mock_post.called

        # Inspect headers
        _, kwargs = mock_post.call_args
        headers = kwargs["headers"]
        assert "X-TrustLens-Signature" in headers
        assert headers["X-TrustLens-Event"] == "listing.risk.high"
        assert headers["Content-Type"] == "application/json"
