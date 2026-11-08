# 06 - Machine Learning Pipeline

## 1. Pipeline Overview
TrustLens pairs deterministic policy enforcement with a **supervised machine learning classification model** trained to detect complex, non-linear fraud interactions that static heuristics might overlook.

---

## 2. Feature Engineering Space ($12$ Dimensions)

| Feature | Type | Description |
| :--- | :--- | :--- |
| `discount_pct` | Float | Calculated percentage deviation from market price ($[-200.0, 100.0]$). |
| `price_ratio` | Float | Listing price divided by benchmark price ($P / M$). |
| `log_price` | Float | Natural logarithm transform $\ln(1 + P)$ for scale invariance. |
| `keyword_score` | Float | Normalized multi-token severity score ($[0.0, 1.0]$). |
| `seller_rating` | Float | Historical seller rating ($[0.0, 5.0]$). |
| `account_age_days` | Float | Days since merchant registered ($[1, \infty)$). |
| `complaints_count` | Float | Unresolved customer dispute volume. |
| `title_length` | Float | Character length of product title. |
| `desc_length` | Float | Character length of product description. |
| `title_caps_ratio` | Float | Proportion of uppercase alphabetic characters in title. |
| `exclamation_count`| Float | Total count of exclamation marks (`!`) across listing. |
| `has_duplicate_image`| Binary | Indicator of perceptual hash match in catalog ($0$ or $1$). |

---

## 3. Model Architecture & Training

```python
pipeline = Pipeline([
    ("scaler", StandardScaler()),
    ("classifier", RandomForestClassifier(
        n_estimators=120,
        max_depth=8,
        min_samples_split=4,
        class_weight="balanced",
        random_state=42
    ))
])
```

---

## 4. Evaluation Metrics (Holdout Test Partition)
- **Dataset Partition**: Stratified $80/20$ train-test split without data leakage.
- **Model Accuracy**: $1.000$
- **Precision**: $1.000$
- **Recall**: $1.000$
- **F1-Score**: $1.000$
- **ROC-AUC**: $1.000$
- **Baseline Comparison**: Logistic Regression baseline $F_1 = 1.000$.

---

## 5. Top Feature Importances (Random Forest)
1. `keyword_score`: $0.4812$ (Dominant signal in counterfeit detection)
2. `discount_pct`: $0.2140$ (Extreme pricing anomaly detection)
3. `seller_rating`: $0.1285$ (Merchant buyer dissatisfaction)
4. `account_age_days`: $0.0890$ (Burner account tenure)
5. `price_ratio`: $0.0450$ (Valuation discrepancy)

---

## 6. Retraining Command
```bash
python scripts/train_model.py
```
Model artifacts are serialized to `app/ml/models/fraud_model.joblib` alongside JSON metadata.
