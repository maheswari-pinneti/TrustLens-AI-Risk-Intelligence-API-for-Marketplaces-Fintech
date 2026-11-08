# 07 - Enterprise Security Architecture & Compliance

TrustLens implements zero-trust, defense-in-depth principles designed for regulated fintech and marketplace compliance environments.

---

## 1. Authentication Mechanisms
- **JWT (JSON Web Tokens)**: Signed using HMAC-SHA256 (`HS256`) with a cryptographically secure 256-bit secret key, explicit expiration timestamps, and subject identity validation.
- **API Keys**: High-entropy hexadecimal tokens generated with `secrets.token_hex(24)` prefixed with `tl_live_`. Supports both `X-API-Key` headers and secure signed query parameters for compliant file export streams.

---

## 2. Password Security & Complexity Policy
- Passwords are never stored in plain text.
- Hashing is implemented with **Bcrypt** utilizing per-user random cryptographic salts.
- **Enterprise Password Complexity Enforcement**:
  - Minimum 8 characters in length
  - At least one uppercase Latin character (`A-Z`)
  - At least one lowercase Latin character (`a-z`)
  - At least one numeric digit (`0-9`)
  - At least one special symbol (`!@#$%^&*()_+-=[]{};':"\\|,.<>/?`)

---

## 3. Brute-Force & Credential Stuffing Throttler
- `LoginThrottler` maintains high-resolution failure tracking across IP addresses and usernames.
- After 5 consecutive invalid credentials within a 15-minute window, the account/IP is locked with `HTTP 429 Too Many Requests`.
- Standard `Retry-After` headers communicate lockout duration to legitimate clients.
- Successful authentications automatically reset the failure counter.

---

## 4. Role-Based Access Control (RBAC) & Privilege Escalation Defense
Four distinct permission tiers are strictly enforced via FastAPI dependencies:
- `admin`: Full system configuration, model continuous retraining (`POST /reports/retrain`), user management, and API key provisioning.
- `investigator`: Triage queues, alert resolutions (`PATCH /alerts/{id}/resolve`), manual disposition actions (`APPROVE`, `REJECT`, `ESCALATE`), and CSV audit exports (`GET /reports/export-csv`).
- `analyst`: Read-only access to risk reports, analytics dashboards, and merchant summaries.
- `client`: External marketplace API consumers authorized to invoke `/analyze` and `/analyze/batch`.

**Privilege Escalation Defense**: Self-registration endpoints (`POST /auth/register`) strictly prohibit assigning `admin` or `investigator` roles without existing administrator authorization.

---

## 5. OWASP Security Response Headers
Every HTTP response is automatically hardened with industry-standard OWASP security headers:
- `X-Content-Type-Options: nosniff`: Eliminates MIME type confusion attacks.
- `X-Frame-Options: DENY`: Defends against clickjacking in external iframes.
- `X-XSS-Protection: 1; mode=block`: Activates browser reflected cross-site scripting filters.
- `Strict-Transport-Security: max-age=31536000; includeSubDomains`: Mandates HTTPS transport.
- `Referrer-Policy: strict-origin-when-cross-origin`: Shields internal routes from external referral leaks.
- `Permissions-Policy`: Restricts browser hardware access (`camera=(), microphone=(), geolocation=()`).
- `Content-Security-Policy (CSP)`: Enforces strict resource origin whitelisting (`default-src 'self'`).

---

## 6. Input Sanitization & Threat Signature Auditing
- **Automated Text Sanitizer (`app/security/sanitizer.py`)**:
  - Strips malicious active script/HTML tags (`<script>`, `<iframe>`, `<object>`, `<embed>`, `<svg>`).
  - Disarms inline `javascript:` URIs and event handler attributes (`onerror=`, `onload=`).
  - Cleans null bytes (`\x00`) and non-printable control characters that could bypass parsers.
  - Preserves legitimate punctuation and vocabulary critical for fraud token classification.
- **Attack Signature Scanner**: Detects SQL injection keywords (`UNION SELECT`, `DROP TABLE`) and adversarial AI prompt injection attempts ("ignore previous instructions").
- **100% Parameterized ORM Queries**: All database queries execute via SQLAlchemy ORM without raw string concatenation.

---

## 7. File Upload Security & Magic Byte Inspection
- **Magic Byte Signatures**: Verifies genuine binary headers (`FF D8 FF` for JPEG, `89 50 4E 47` for PNG, `RIFF....WEBP` for WebP, and `GIF87a`/`GIF89a` for GIF) to block polyglot binaries or malicious shell scripts disguised as images.
- **Decompression Bomb Protection**: Caps maximum upload payload to $10\text{ MB}$ and bounds pixel dimensions (`MAX_IMAGE_PIXELS = 25_000_000`).

---

## 8. Rate Limiting Defense
- Implements an **in-memory sliding window counter** tracking requests per minute per IP address and API key.
- Default limit: `120 requests/minute`.
- Violations return `HTTP 429 Too Many Requests` with standard retry headers:
  - `Retry-After: 60`
  - `X-RateLimit-Limit: 120`
  - `X-RateLimit-Remaining: 0`

---

## 9. Immutable Compliance Audit Trail
- All security-relevant actions (investigator decisions, alert resolutions, model retraining, and listing registrations) are logged to the `audit_logs` table with timestamp, user ID, username, IP/resource, and action metadata.
