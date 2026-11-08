# TrustLens v1.0.0 Release Notes & Pull Request Specification

## 🚀 Overview

**TrustLens** is an enterprise-grade AI Risk Intelligence API and compliance investigation platform designed for high-volume e-commerce marketplaces and fintech payment platforms. It pairs deterministic policy-enforcing rule detectors with a machine learning classification pipeline to detect counterfeit goods, price manipulation, recycled imagery, burner seller syndicates, and off-platform transaction fraud.

---

## 📦 What's Included in This Release

### 1. Hybrid Risk Scoring Engine
- **Price Anomaly Analyzer (30 pts)**: Detects benchmark deviations and category price floor breaches.
- **Fraud Keyword Detector (25 pts)**: Multi-token regex scanning for counterfeit, replica, stolen goods, and off-platform payment siphoning.
- **Image Perceptual Hasher (20 pts)**: 64-bit dHash/pHash perceptual hashing with bitwise Hamming distance cross-matching.
- **Seller Reputation Analyzer (15 pts)**: Evaluates burner tenure ($<3$ days), complaint frequencies, and historical flagged listing ratios.
- **Behavior & Urgency Scanner (10 pts)**: Flags uppercase shouting ratios ($>65\%$), urgency punctuation, and leaked contact numbers/emails.
- **Calibrated Tiers**: Low (`0–29`, `AUTO_APPROVE`), Medium (`30–59`, `MANUAL_REVIEW`), High (`60–100`, `AUTO_REJECT`).

### 2. Machine Learning & Continuous Active Learning Loop
- **Model Pipeline**: Random Forest Classifier (`trustlens_rf_v1.pkl`) trained with cross-validated `StandardScaler` feature scaling.
- **Continuous Retraining**: Compliance investigator decisions (`APPROVE` or `REJECT`) automatically augment training datasets to prevent model drift via `POST /api/v1/reports/retrain`.
- **Inference Service**: Thread-safe inference with calibrated fraud probabilities and rule-vs-ML consensus reporting.

### 3. Enterprise Security & OWASP Hardening
- **Security Headers**: Strict Content-Security-Policy (CSP), HSTS, `X-Frame-Options: DENY`, `X-Content-Type-Options: nosniff`, and Permissions-Policy.
- **Multi-Vector Sanitization**: Neutralizes `<script>` tags, event handlers, and scans for SQL injection keywords and adversarial LLM prompt injections.
- **Authentication & RBAC**: Dual JWT bearer token and API key (`X-API-Key`) authentication with 4 hierarchical roles (`admin`, `investigator`, `analyst`, `client`).
- **Brute-Force Protection**: `LoginThrottler` enforces a 15-minute account lockout after 5 consecutive failed attempts.
- **Privilege Escalation Defense**: Explicit server-side validation preventing self-assignment of elevated roles during registration.
- **Binary Image Verification**: File header magic byte inspection (`\xFF\xD8\xFF`, `\x89PNG`, `RIFF...WEBP`, `GIF89a`) with 10MB/25Mpx bomb protection.
- **Webhook Integrity**: HMAC-SHA256 signature calculation and constant-time signature verification for platform event webhooks.

### 4. Forensic Investigation Dashboard (Frontend)
- **Stack**: React 19 + TypeScript + Vite + Tailwind CSS + Recharts + Lucide Icons.
- **Pages**: Executive Risk Overview, Live Interactive Listing Analyzer, Compliance Triage Queue, Deep Listing Investigation Modal, Merchant Profiles, Risk Reports & Audit Logs, System Settings.

### 5. Automated Testing & CI/CD
- **Test Suite**: 60 unit, security, and integration tests with 100% pass rate.
- **CI/CD Pipeline**: GitHub Actions workflow testing backend on Python 3.11 with SQLite in-memory isolation and building the Vite frontend production distribution.

---

## 🔍 Verification Commands

```bash
# Run backend tests
python -m pytest

# Run CLI scan
python app/cli.py scan --title "Nike Shoes Cheap Replica" --desc "1:1 replica shoes whatsapp me" --price 45 --market-price 210

# Run Frontend from root
npm run dev

# Run FastAPI backend
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```
