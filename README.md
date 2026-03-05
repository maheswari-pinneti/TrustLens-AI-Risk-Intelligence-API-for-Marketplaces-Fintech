# TrustLens-AI-Risk-Intelligence-API-for-Marketplaces-Fintech

# TrustLens – AI Risk Intelligence API

TrustLens is an AI-powered Risk Scoring API that detects suspicious product listings and merchant fraud patterns in e-commerce and fintech platforms.

This project analyzes product listings and generates a **risk score with explanation** to help marketplaces detect fraud early.

---

# Problem

Online marketplaces often face problems like:

- Counterfeit product listings
- Unrealistic price manipulation
- Duplicate product images
- Fraud keywords in descriptions
- Suspicious sellers

Manual moderation is slow and expensive.

---

# Solution

TrustLens provides a **REST API** that analyzes product listing data and calculates a risk score.

The system evaluates:

- Price anomaly detection
- Fraud keyword detection
- Duplicate image detection
- Seller risk indicators

The API returns:

- Risk Score (0–100)
- Risk Level (Low / Medium / High)
- Explanation of risk factors

---

# Example API Response

```json
{
  "risk_score": 78,
  "risk_level": "High",
  "flags": [
    "Price anomaly detected",
    "Fraud keyword detected: replica",
    "Low seller rating"
  ]
}
````

---

# Tech Stack

Backend

* Python
* FastAPI

Libraries

* Uvicorn
* Pillow
* ImageHash
* Pandas
* Scikit-learn

---

# Project Structure

```
trustlens-ai-risk-intelligence-api

app
│
├── main.py
├── risk_engine.py
├── keyword_detector.py
├── price_analyzer.py
└── image_checker.py

data
└── fraud_keywords.txt

requirements.txt
README.md
```

---

# Installation

Clone the repository

```
git clone https://github.com/yourusername/trustlens-ai-risk-intelligence-api.git
```

Go to the folder

```
cd trustlens-ai-risk-intelligence-api
```

Create virtual environment

```
python -m venv venv
```

Activate environment

Windows

```
venv\Scripts\activate
```

Install dependencies

```
pip install -r requirements.txt
```

---

# Run the API

Start FastAPI server

```
uvicorn app.main:app --reload
```

Open API documentation

```
http://127.0.0.1:8000/docs
```

FastAPI automatically generates **interactive Swagger API documentation**.

---

# Example Request

Endpoint

```
POST /analyze
```

Request Body

```json
{
"title": "Nike Shoes",
"description": "cheap replica nike shoes",
"price": 500,
"market_price": 5000,
"seller_rating": 1
}
```

---

# Use Cases

TrustLens can be used by:

* E-commerce marketplaces
* Fintech payment platforms
* Online reseller platforms
* Startup marketplaces

---

# Future Improvements

* Machine learning fraud detection model
* Advanced NLP analysis
* Seller reputation scoring
* Image similarity detection using deep learning
* Fraud monitoring dashboard

---

# Author

Maheswari Pinneti

GitHub
[https://github.com/maheswari-pinneti](https://github.com/maheswari-pinneti)

LinkedIn
[https://www.linkedin.com/in/maheswari-pinneti/](https://www.linkedin.com/in/maheswari-pinneti/)

---

# License

MIT License

```

---

# Step 4 — Scroll Down

Click the green button:

```

Commit new file

```

Your README will appear on your repo homepage.

---

# Step 5 — Check Your Repository

Now when someone opens your repo they will see:

```

Project title
Project description
Tech stack
Installation
Usage
API example

```
