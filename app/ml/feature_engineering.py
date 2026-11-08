"""
Feature Engineering Module for Machine Learning Fraud Classifier
"""
import re
import numpy as np
import pandas as pd
from typing import Dict, Any, List, Union
from app.detectors.keyword_detector import KeywordDetector

keyword_detector = KeywordDetector()


FEATURE_COLUMNS = [
    "discount_pct",
    "price_ratio",
    "log_price",
    "keyword_score",
    "seller_rating",
    "account_age_days",
    "complaints_count",
    "title_length",
    "desc_length",
    "title_caps_ratio",
    "exclamation_count",
    "has_duplicate_image"
]


def extract_features_from_dict(row: Dict[str, Any]) -> Dict[str, float]:
    """Extracts numeric feature vector from a single raw listing record."""
    price = float(row.get("price", 10.0))
    market_price = float(row.get("market_price", price) or price)
    title = str(row.get("title", ""))
    description = str(row.get("description", ""))

    # Keyword score
    kw_res = keyword_detector.analyze(title=title, description=description)
    kw_score = kw_res["normalized_score"]

    # Price metrics
    if market_price > 0:
        discount_pct = max(-200.0, min(100.0, ((market_price - price) / market_price) * 100.0))
        price_ratio = price / market_price
    else:
        discount_pct = 0.0
        price_ratio = 1.0

    # Seller metrics
    seller_rating = float(row.get("seller_rating", 4.5) if row.get("seller_rating") is not None else 4.5)
    account_age_days = float(row.get("account_age_days", 90) if row.get("account_age_days") is not None else 90)
    complaints_count = float(row.get("complaints_count", 0) if row.get("complaints_count") is not None else 0)

    # Text structure
    title_alpha = [c for c in title if c.isalpha()]
    caps_ratio = (sum(1 for c in title_alpha if c.isupper()) / len(title_alpha)) if title_alpha else 0.0
    excl_count = float(title.count("!") + description.count("!"))

    has_dup = float(row.get("image_duplicate", 0) or row.get("has_duplicate_image", 0))

    return {
        "discount_pct": float(discount_pct),
        "price_ratio": float(price_ratio),
        "log_price": float(np.log1p(max(0.1, price))),
        "keyword_score": float(kw_score),
        "seller_rating": float(seller_rating),
        "account_age_days": float(account_age_days),
        "complaints_count": float(complaints_count),
        "title_length": float(len(title)),
        "desc_length": float(len(description)),
        "title_caps_ratio": float(caps_ratio),
        "exclamation_count": float(excl_count),
        "has_duplicate_image": float(has_dup)
    }


def extract_features_df(df: pd.DataFrame) -> pd.DataFrame:
    """Transforms a raw DataFrame of listings into the model feature space."""
    records = []
    for _, row in df.iterrows():
        records.append(extract_features_from_dict(row.to_dict()))
    return pd.DataFrame(records, columns=FEATURE_COLUMNS)
