"""
Security Tests: OWASP Security Response Headers Configuration
"""
from app.security.headers import SecurityHeadersMiddleware


def test_owasp_security_headers_configured():
    """Verifies that SecurityHeadersMiddleware defines all OWASP compliance headers."""
    middleware = SecurityHeadersMiddleware(app=None)
    headers_dict = {
        name.decode("latin1").lower(): val.decode("latin1")
        for name, val in middleware.extra_headers
    }

    # Verify OWASP Headers
    assert headers_dict.get("x-content-type-options") == "nosniff"
    assert headers_dict.get("x-frame-options") == "DENY"
    assert headers_dict.get("x-xss-protection") == "1; mode=block"
    assert headers_dict.get("referrer-policy") == "strict-origin-when-cross-origin"
    assert "max-age=31536000" in headers_dict.get("strict-transport-security", "")
    assert "default-src 'self'" in headers_dict.get("content-security-policy", "")
    assert "camera=()" in headers_dict.get("permissions-policy", "")
    assert headers_dict.get("cross-origin-opener-policy") == "same-origin"
    assert headers_dict.get("cross-origin-resource-policy") == "same-origin"
