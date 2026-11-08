"""
OWASP Recommended HTTP Security Headers ASGI Middleware
Ensures all API responses carry strict security and privacy headers without BaseHTTPMiddleware buffering overhead.
"""
from typing import Callable, Dict, Any, List, Tuple


class SecurityHeadersMiddleware:
    """
    Pure ASGI Middleware that appends OWASP-recommended security headers to every HTTP response:
    - Content-Security-Policy (CSP)
    - X-Content-Type-Options (nosniff)
    - X-Frame-Options (DENY to prevent clickjacking)
    - X-XSS-Protection
    - Strict-Transport-Security (HSTS)
    - Referrer-Policy
    - Permissions-Policy
    """

    def __init__(self, app: Any):
        self.app = app
        self.extra_headers: List[Tuple[bytes, bytes]] = [
            (b"x-content-type-options", b"nosniff"),
            (b"x-frame-options", b"DENY"),
            (b"x-xss-protection", b"1; mode=block"),
            (b"referrer-policy", b"strict-origin-when-cross-origin"),
            (b"permissions-policy", b"camera=(), microphone=(), geolocation=(), payment=(), usb=()"),
            (b"strict-transport-security", b"max-age=31536000; includeSubDomains"),
            (
                b"content-security-policy",
                b"default-src 'self'; img-src 'self' data: https:; script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; frame-ancestors 'none';"
            ),
            (b"cross-origin-opener-policy", b"same-origin"),
            (b"cross-origin-resource-policy", b"same-origin")
        ]

    async def __call__(self, scope: Dict[str, Any], receive: Callable, send: Callable) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        async def send_wrapper(message: Dict[str, Any]) -> None:
            if message["type"] == "http.response.start":
                existing_headers = list(message.get("headers", []))
                existing_names = {h[0].lower() for h in existing_headers}
                for header_name, header_val in self.extra_headers:
                    if header_name not in existing_names:
                        existing_headers.append((header_name, header_val))
                message["headers"] = existing_headers
            await send(message)

        await self.app(scope, receive, send_wrapper)
