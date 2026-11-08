# TrustLens – AI Risk Intelligence API for Marketplaces & Fintech

<p align="center">
  <strong>Explainable, multi-dimensional AI fraud and risk scoring platform for e-commerce marketplaces and fintech payment ecosystems.</strong>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.11%20%7C%203.14-blue.svg" alt="Python Version" />
  <img src="https://img.shields.io/badge/FastAPI-0.115+-009688.svg" alt="FastAPI" />
  <img src="https://img.shields.io/badge/Scikit--Learn-1.9+-F7931E.svg" alt="Scikit-Learn" />
  <img src="https://img.shields.io/badge/React-19-61DAFB.svg" alt="React" />
  <img src="https://img.shields.io/badge/TypeScript-Vite-3178C6.svg" alt="TypeScript" />
  <img src="https://img.shields.io/badge/Tests-60%20Passed%20(100%25)-brightgreen.svg" alt="Pytest" />
  <a href="https://github.com/maheswari-pinneti/TrustLens-AI-Risk-Intelligence-API-for-Marketplaces-Fintech/actions/workflows/ci.yml"><img src="https://github.com/maheswari-pinneti/TrustLens-AI-Risk-Intelligence-API-for-Marketplaces-Fintech/actions/workflows/ci.yml/badge.svg" alt="TrustLens CI" /></a>
  <img src="https://img.shields.io/badge/Python%20SDK-Included-purple.svg" alt="Python SDK" />
  <img src="https://img.shields.io/badge/License-MIT-green.svg" alt="License" />
</p>

---

## 📌 Problem Statement

Online marketplaces and reseller platforms face systemic fraud challenges:
- **Counterfeit & Replica Listings**: Fake luxury goods, clone electronics, and knockoffs damages brand integrity and triggers buyer chargebacks.
- **Extreme Price Manipulation**: Stolen goods or bait listings advertised at 80%+ below retail to lure unsuspecting buyers.
- **Image Duplication**: Burner accounts recycling stock photos or images stolen from legitimate sellers.
- **Off-Platform Payment Scams**: Fraudulent sellers siphoning buyers to unmonitored channels (Telegram, WhatsApp, wire transfer).
- **Burner Merchant Accounts**: Low-reputation accounts created specifically for short hit-and-run fraud cycles.

**Manual review does not scale.** **TrustLens** provides an automated, explainable REST API and compliance dashboard that evaluates product listings, assigns a **calibrated risk score (0–100)**, and provides auditable evidence for every triggered flag.

---

## 💡 Solution Overview

TrustLens pairs **deterministic rule-based guardrails** with a **machine learning classification model** (Random Forest) to ensure both instant policy enforcement and non-linear pattern detection.

```
+----------------------------------------------------------------------------------+
|                            TrustLens Risk Platform                               |
+----------------------------------------------------------------------------------+
                                     |
               +---------------------+---------------------+
               |                                           |
     [ Marketplace Events ]                      [ Forensic Dashboard ]
      (REST API / Webhooks)                       (React 19 / Vite UI)
               |                                           |
               +---------------------+---------------------+
                                     |
                                     v
                       +---------------------------+
                       | FastAPI Gateway (Port 8000|
                       | - Rate Limiter (120 req/m)|
                       | - JWT & API Key Auth      |
                       +---------------------------+
                                     |
       +-----------------------------+-----------------------------+
       |                                                           |
       v                                                           v
+-------------------------------+                          +-------------------------------+
|    Deterministic Detectors    |                          |      Machine Learning         |
| 1. Keyword Detector           |                          | 1. Feature Engineering Vector |
| 2. Price Anomaly Analyzer     |                          | 2. StandardScaler Pipeline    |
| 3. Image Perceptual Hasher    |                          | 3. Random Forest Classifier   |
| 4. Seller Reputation Analyzer |                          | 4. Probability Calibration    |
| 5. Behavior & Urgency Scanner |                          +-------------------------------+
+-------------------------------+                                          |
       |                                                                   |
       +-----------------------------+-------------------------------------+
                                     |
                                     v
                       +---------------------------+
                       | Composite Risk Engine     |
                       | - Score: 0 to 100         |
                       | - Risk Tier: Low/Med/High |
                       | - Forensic Evidence & Flag|
                       +---------------------------+
```

---

## ⚖️ Risk Scoring Model

The risk score $S \in [0, 100]$ is computed using configurable factor weights:

| Risk Dimension | Maximum Points | Description |
| :--- | :---: | :--- |
| **Price Anomaly** | **30 pts** | Mathematical deviation from market price benchmarks and category minimums. |
| **Fraud Keywords** | **25 pts** | Multi-token regex scanning for replica, counterfeit, stolen, and off-platform language. |
| **Image Similarity** | **20 pts** | 64-bit perceptual hashing (dHash/pHash) and bitwise Hamming distance cross-matching. |
| **Seller Reputation** | **15 pts** | Seller tenure, customer disputes, rating, and historical flagged listing ratio. |
| **Listing Behavior** | **10 pts** | Excessive uppercase shouting, urgency punctuation, leaked phone numbers, and burst velocity. |
| **Total Score** | **100 pts** | **Low (0–29)**: `AUTO_APPROVE` • **Medium (30–59)**: `MANUAL_REVIEW` • **High (60–100)**: `AUTO_REJECT` |

---

## 🛠️ Technology Stack

- **Backend**: Python 3.11 / 3.14, FastAPI, Pydantic v2, Uvicorn
- **Machine Learning**: Scikit-Learn (Random Forest & Logistic Regression), Pandas, NumPy
- **Image Processing**: Pillow, ImageHash (dHash, pHash, aHash)
- **Database**: SQLite (Development) / PostgreSQL (Production), SQLAlchemy 2.0 ORM
- **Security**: JWT (`pyjwt`), Bcrypt password hashing, sliding-window Rate Limiting, OWASP Security Headers (CSP, HSTS, X-Frame-Options), XSS/SQLi input sanitization, image magic byte validation, brute-force login throttling, and RBAC privilege escalation defense
- **Testing**: Pytest (60 comprehensive tests across unit, integration, and security suites, 100% pass rate), HTTPX
- **Frontend Dashboard**: React 19, TypeScript, Vite, Recharts, Lucide Icons
- **DevOps**: Docker, Docker Compose, NGINX

---

## 🚀 Quick Start

### 1. Clone & Set Up Virtual Environment

```bash
git clone https://github.com/maheswari-pinneti/TrustLens-AI-Risk-Intelligence-API-for-Marketplaces-Fintech.git
cd TrustLens-AI-Risk-Intelligence-API-for-Marketplaces-Fintech

python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

pip install -r requirements.txt
```

### 2. Seed Database & Train ML Model

```bash
# Seed realistic demo merchants and 150+ evaluated listings
python scripts/seed_db.py

# (Optional) Retrain machine learning classifier
python scripts/train_model.py
```

### 3. Start FastAPI Backend

```bash
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```
Open **Interactive Swagger UI**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

### 4. Start React Investigation Dashboard

```bash
cd frontend
npm install
npm run dev
```
Open dashboard: [http://localhost:5173](http://localhost:5173)

---

## 🐳 Docker Deployment

Run the complete multi-service stack with a single command:

```bash
docker-compose up --build -d
```
- **Backend API**: `http://localhost:8000`
- **Dashboard UI**: `http://localhost:3000`
- **Swagger Docs**: `http://localhost:8000/docs`

---

## 📡 API Example Usage

### Analyze Listing Request

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/analyze?persist=true" \
     -H "Content-Type: application/json" \
     -H "X-API-Key: tl_live_admin_secret_key_998877" \
     -d '{
       "title": "Nike Air Jordan 1 Retro High Cheap Replica",
       "description": "1:1 replica shoes first copy ua quality whatsapp me for orders must go today",
       "price": 45.0,
       "market_price": 210.0,
       "category": "Footwear & Apparel",
       "merchant_id": "merch_quick_deals",
       "seller_rating": 1.4,
       "seller_account_age_days": 3,
       "seller_complaints_count": 8
     }'
```

### API Response

```json
{
  "listing_id": "lst_98ce14694d",
  "title": "Nike Air Jordan 1 Retro High Cheap Replica",
  "risk_score": 67.42,
  "risk_level": "High",
  "recommendation": "AUTO_REJECT",
  "ml_prediction": "Fraudulent",
  "ml_fraud_probability": 0.9421,
  "flags": [
    "Fraud keyword detected: 'replica' (severity: 1.0, in title and description)",
    "Fraud keyword detected: '1:1 replica' (severity: 1.0, in description)",
    "Fraud keyword detected: 'ua quality' (severity: 1.0, in description)",
    "Fraud keyword detected: 'whatsapp me' (severity: 1.0, in description)",
    "Severe price anomaly: 78.6% discount indicates likely counterfeit or bait listing",
    "Critically low seller rating: 1.4/5.0 (high buyer dissatisfaction)",
    "Very new seller account: registered only 3 day(s) ago (high burner account risk)",
    "Severe complaint history: 8 reported customer disputes"
  ],
  "score_breakdown": {
    "price_anomaly_score": 26.57,
    "fraud_keywords_score": 25.0,
    "image_similarity_score": 0.0,
    "seller_reputation_score": 15.0,
    "listing_behavior_score": 0.85,
    "total_score": 67.42
  },
  "evidence": {
    "summary_explanation": "High fraud probability (67.4/100) driven by critical alerts in: Price Anomaly, Fraud Keywords, Seller Reputation. Contains 8 high-confidence risk indicators requiring immediate rejection or escalation."
  },
  "timestamp": "2026-11-08T20:42:22.123456"
}
```

---

## 🐍 Python SDK Integration

TrustLens includes an integrated Python client SDK for marketplaces and payment platforms:

```python
from sdk.trustlens_client import TrustLensClient

# Initialize client
client = TrustLensClient(
    base_url="http://127.0.0.1:8000",
    api_key="tl_live_admin_secret_key_998877"
)

# Scan a product listing
result = client.analyze(
    title="Nike Air Jordan 1 Retro High Cheap Replica",
    description="1:1 replica shoes first copy ua quality whatsapp me",
    price=45.0,
    market_price=210.0,
    seller_rating=1.5
)

print(f"Risk Score: {result.risk_score}/100")
print(f"Risk Level: {result.risk_level}")
print(f"Recommendation: {result.recommendation}")
print(f"Detected Flags: {result.flags}")

if result.is_high_risk:
    print("Action: Automatically rejecting listing and notifying compliance team.")
```

---

## 🔄 Continuous Feedback Loop & Active Learning
When compliance investigators manually inspect and disposition listings (`APPROVE` or `REJECT`) in the triage queue, TrustLens persists their decisions to an augmented ground-truth dataset. This feedback can be used to retrain the Random Forest model and prevent model drift:

```bash
# Trigger feedback model retraining via API
curl -X POST "http://127.0.0.1:8000/api/v1/reports/retrain" \
     -H "X-API-Key: tl_live_admin_secret_key_998877"
```

---

## 🧪 Automated Testing

Execute the test suite with Pytest:

```bash
python -m pytest tests/ -v
```

Output:
```
============================= 60 passed in 14.16s =============================
```

---

## 📁 Architectural Documentation

Detailed deep-dive architectural specifications are located in [`docs/`](docs):
- [01 - Project Overview](docs/01-project-overview.md)
- [02 - System Architecture](docs/02-system-architecture.md)
- [03 - API Documentation & Specifications](docs/03-api-documentation.md)
- [04 - Mathematical Risk Scoring Engine](docs/04-risk-scoring-engine.md)
- [05 - Database Design & ER Diagram](docs/05-database-design.md)
- [06 - Machine Learning & Evaluation](docs/06-machine-learning.md)
- [07 - Security Architecture & RBAC](docs/07-security.md)
- [08 - Automated Testing Strategy](docs/08-testing-strategy.md)
- [09 - Deployment & Docker Guide](docs/09-deployment.md)
- [10 - Future Roadmap & Evolution](docs/10-future-roadmap.md)

---

## 👤 Author

**Maheswari Pinneti**  
*AI & Backend Engineer*  
GitHub: [https://github.com/maheswari-pinneti](https://github.com/maheswari-pinneti)

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
