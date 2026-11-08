# 08 - Testing Strategy

TrustLens maintains an automated test suite executed with **Pytest**, covering unit, integration, and security layers.

---

## 1. Test Suite Structure
```
tests/
├── conftest.py                   # In-memory SQLite fixtures & detector factories
├── unit/
│   ├── test_keyword_detector.py  # Counterfeit, unauthorized, off-platform keyword tests
│   ├── test_price_analyzer.py    # Discounts, category floor, zero/negative bounds
│   ├── test_image_checker.py     # Perceptual hashes, exact duplicate & distance checks
│   ├── test_seller_analyzer.py   # Tenure, ratings, complaint thresholds, flagged ratios
│   ├── test_behavior_detector.py # Shouting, urgency, leaked phone/emails
│   └── test_risk_engine.py       # Mathematical weighted combinations & boundaries
├── security/
│   ├── test_auth.py              # Bcrypt hash/verify, JWT encoding, API key generation
│   └── test_rate_limiter.py      # Sliding window quota exhaustion tests
└── integration/
    └── test_api_endpoints.py     # End-to-end analyze, batch, disposition, and report runs
```

---

## 2. Running Automated Tests

Run the full test suite with verbose output:
```bash
python -m pytest tests/ -v
```

Run test suite with coverage report:
```bash
python -m pytest tests/ --cov=app --cov-report=term-missing
```

---

## 3. Key Test Assertions
- **Boundary Verification**: Risk score $S \in [0.0, 100.0]$ under all extreme input conditions.
- **Explainability Integrity**: Ensuring triggered flags match exact text substrings and factor attributions sum correctly.
- **Security Invariance**: Validating that expired JWTs and bad passwords return `HTTP 401 Unauthorized`.
