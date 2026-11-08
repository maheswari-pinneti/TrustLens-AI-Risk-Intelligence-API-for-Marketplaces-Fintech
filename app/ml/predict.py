"""
Machine Learning Model Inference Service
"""
import json
from pathlib import Path
from typing import Dict, Any, Optional, List
import joblib
import pandas as pd
from app.config import get_settings
from app.ml.feature_engineering import extract_features_from_dict, FEATURE_COLUMNS


class MLFraudPredictor:
    """
    Production-ready inference wrapper for the trained fraud classification model.
    """

    def __init__(self, model_path: Optional[Path] = None):
        settings = get_settings()
        self.model_path = model_path or (settings.ML_MODELS_DIR / "fraud_model.joblib")
        self.metadata_path = settings.ML_MODELS_DIR / "model_metadata.json"
        self.pipeline = None
        self.metadata = {}
        self._load_model()

    def _load_model(self) -> bool:
        if self.model_path.exists():
            try:
                self.pipeline = joblib.load(self.model_path)
                if self.metadata_path.exists():
                    with open(self.metadata_path, "r", encoding="utf-8") as f:
                        self.metadata = json.load(f)
                return True
            except Exception as e:
                print(f"Warning: Failed to load ML model from {self.model_path}: {e}")
                self.pipeline = None
                return False
        return False

    @property
    def is_loaded(self) -> bool:
        return self.pipeline is not None

    def predict_single(self, listing_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Runs ML inference on a single listing.
        Returns:
            {
                "fraud_probability": float (0.0 to 1.0),
                "prediction": "Fraudulent" | "Genuine",
                "risk_contribution": float (0 to 100),
                "model_version": str
            }
        """
        if not self.is_loaded:
            # Fallback when model is not available
            return {
                "fraud_probability": None,
                "prediction": None,
                "risk_contribution": None,
                "model_version": None,
                "status": "MODEL_UNAVAILABLE"
            }

        features = extract_features_from_dict(listing_data)
        feature_df = pd.DataFrame([features], columns=FEATURE_COLUMNS)

        try:
            probabilities = self.pipeline.predict_proba(feature_df)[0]
            fraud_prob = float(probabilities[1])
            is_fraud = int(fraud_prob >= 0.5)

            return {
                "fraud_probability": round(fraud_prob, 4),
                "prediction": "Fraudulent" if is_fraud == 1 else "Genuine",
                "confidence": round(max(probabilities), 4),
                "model_version": self.metadata.get("version", "1.0.0"),
                "status": "SUCCESS"
            }
        except Exception as e:
            return {
                "fraud_probability": None,
                "prediction": None,
                "error": str(e),
                "status": "INFERENCE_ERROR"
            }

    def predict_batch(self, listings_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        return [self.predict_single(item) for item in listings_data]

    def get_model_info(self) -> Dict[str, Any]:
        return {
            "loaded": self.is_loaded,
            "model_path": str(self.model_path),
            "metadata": self.metadata
        }
