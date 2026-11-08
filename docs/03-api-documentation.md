# 03 - API Documentation

The TrustLens API is fully OpenAPI 3.1 compliant with interactive documentation hosted locally at:
- **Swagger UI**: `http://127.0.0.1:8000/docs`
- **ReDoc**: `http://127.0.0.1:8000/redoc`
- **Raw OpenAPI JSON**: `http://127.0.0.1:8000/openapi.json`

---

## Authentication

All protected endpoints require either an **API Key** or a **JWT Bearer Token**:

### Header 1: API Key
```http
X-API-Key: tl_live_admin_secret_key_998877
```

### Header 2: Bearer Token
```http
Authorization: Bearer <jwt_access_token>
```

---

## Key Endpoints

### 1. Real-Time Risk Analysis
- **URL**: `POST /api/v1/analyze?persist=true`
- **Request Body**:
```json
{
  "title": "Nike Air Jordan 1 Retro High Cheap Replica",
  "description": "1:1 replica shoes first copy ua quality whatsapp me for orders fast shipping",
  "price": 45.0,
  "market_price": 210.0,
  "category": "Footwear & Apparel",
  "merchant_id": "merch_001",
  "seller_rating": 1.4,
  "seller_account_age_days": 3,
  "seller_complaints_count": 8
}
```

- **Response (200 OK)**:
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

### 2. Batch Analysis Endpoint
- **URL**: `POST /api/v1/analyze/batch`
- **Request Body**:
```json
{
  "listings": [
    { "title": "Authentic Item", "description": "Sealed retail", "price": 300, "market_price": 320 },
    { "title": "Replica Watch", "description": "Superclone cash only", "price": 100, "market_price": 5000 }
  ]
}
```

---

### 3. Listing Disposition (Compliance Review)
- **URL**: `PATCH /api/v1/listings/{listing_id}/decision`
- **Request Body**:
```json
{
  "status": "REJECTED",
  "review_notes": "Counterfeit branding and unauthorized off-platform payment detected."
}
```

---

### 4. Merchant Surveillance
- **URL**: `GET /api/v1/merchants`
- **URL**: `GET /api/v1/merchants/{merchant_id}`

---

### 5. Health Check
- **URL**: `GET /health`
- **Response**:
```json
{
  "status": "HEALTHY",
  "environment": "development",
  "version": "1.0.0",
  "database_connected": true,
  "ml_model_loaded": true,
  "timestamp": "2026-11-08T20:41:37.777234"
}
```
