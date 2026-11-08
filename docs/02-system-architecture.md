# 02 - System Architecture

## 1. High-Level Architecture Diagram

```
+-----------------------------------------------------------------------------------+
|                            TrustLens Risk Platform                                |
+-----------------------------------------------------------------------------------+
                                      |
                +---------------------+---------------------+
                |                                           |
      [ External Marketplaces ]                   [ React / Vite UI ]
      (REST API / Webhooks)                       (Forensic Dashboard)
                |                                           |
                +---------------------+---------------------+
                                      |
                                      v
                        +---------------------------+
                        |  Reverse Proxy / NGINX    |
                        +---------------------------+
                                      |
                                      v
                        +---------------------------+
                        |  FastAPI Gateway (Port 8000)
                        |  - Rate Limiter (120 req/m)|
                        |  - JWT & API Key Auth     |
                        |  - Pydantic v2 Validation |
                        +---------------------------+
                                      |
        +-----------------------------+-----------------------------+
        |                                                           |
        v                                                           v
+-------------------------------+                           +-------------------------------+
|    Deterministic Detectors    |                           |      Machine Learning         |
| 1. Keyword Detector           |                           | 1. Feature Engineering Vector |
| 2. Price Anomaly Analyzer     |                           | 2. StandardScaler Pipeline    |
| 3. Image Perceptual Hasher    |                           | 3. Random Forest Classifier   |
| 4. Seller Reputation Analyzer |                           | 4. Probability Calibration    |
| 5. Behavior & Urgency Scanner |                           +-------------------------------+
+-------------------------------+                                           |
        |                                                                   |
        +-----------------------------+-------------------------------------+
                                      |
                                      v
                        +---------------------------+
                        | Risk Engine Orchestrator  |
                        | - Weighted Score (0-100)  |
                        | - Risk Level (Low/Med/Hi) |
                        | - Plain-English Evidence  |
                        +---------------------------+
                                      |
        +-----------------------------+-----------------------------+
        |                                                           |
        v                                                           v
+-------------------------------+                           +-------------------------------+
|     SQLite / PostgreSQL       |                           |      Audit & Alerts Bus       |
| - Listings & Audit Trail      |                           | - Critical Threshold Alerts   |
| - Merchants & Reputation      |                           | - Event Notification Logs     |
| - Image Fingerprints          |                           +-------------------------------+
+-------------------------------+
```

---

## 2. Component Directory Architecture

```
app/
├── api/
│   ├── routes/              # FastAPI APIRouters (analyze, listings, merchants, reports, auth, health)
│   └── schemas/             # Pydantic v2 validation contracts (request, response, auth)
├── core/
│   ├── risk_engine.py       # Central orchestrator integrating all detectors & scoring
│   ├── scoring.py           # Mathematical weight combination and normalization
│   ├── explainability.py    # Evidence ranking and human explanation generator
│   └── thresholds.py        # Configurable risk factor point weights
├── detectors/
│   ├── keyword_detector.py  # Counterfeit, unauthorized, off-platform keyword scanner
│   ├── price_analyzer.py    # Market benchmark comparison & category floor validator
│   ├── image_checker.py     # Perceptual hashing (dHash/pHash) & duplicate finder
│   ├── seller_analyzer.py   # Seller tenure, rating, complaint & flag ratio analyzer
│   └── behavior_detector.py # Shouting, urgency punctuation, leaked contact regex
├── ml/
│   ├── preprocessing.py     # Stratified split & pipeline preprocessing
│   ├── feature_engineering.py # Numeric vector extraction from text & price signals
│   ├── train.py             # Reproducible training & evaluation pipeline
│   ├── predict.py           # Thread-safe ML inference service
│   └── models/              # Persisted joblib model artifacts & metadata
├── database/
│   ├── connection.py        # SQLAlchemy engine and session factory
│   ├── models.py            # ORM entities (User, Merchant, Listing, ImageFingerprint, AuditLog)
│   └── repositories/        # Clean CRUD repository pattern
├── security/
│   ├── authentication.py    # Bcrypt hashing, JWT bearer tokens, API key validation
│   ├── authorization.py     # Role-based access control (Admin, Investigator, Analyst)
│   └── rate_limiter.py      # In-memory sliding window rate limiter
└── services/
    ├── analysis_service.py  # End-to-end execution and DB persistence orchestration
    ├── merchant_service.py  # Dynamic merchant risk recalculation
    ├── alert_service.py     # High-risk alert emission
    └── report_service.py    # Analytics aggregations & CSV exports
```
