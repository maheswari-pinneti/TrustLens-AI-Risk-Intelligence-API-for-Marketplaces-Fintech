"""
Feedback Loop & Active Learning Retraining Service
Collects human investigator decisions (APPROVED vs REJECTED)
to create verified ground-truth datasets for continuous model improvement.
"""
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, List
import pandas as pd
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.config import get_settings
from app.database.models import Listing
from app.ml.train import train_and_evaluate_model


class FeedbackService:

    def __init__(self, db: Session):
        self.db = db
        self.settings = get_settings()

    def get_feedback_statistics(self) -> Dict[str, Any]:
        """Returns statistics on human-reviewed listings available for active learning."""
        approved_count = self.db.query(func.count(Listing.id)).filter(
            Listing.status == "APPROVED"
        ).scalar() or 0

        rejected_count = self.db.query(func.count(Listing.id)).filter(
            Listing.status == "REJECTED"
        ).scalar() or 0

        pending_count = self.db.query(func.count(Listing.id)).filter(
            Listing.status == "PENDING_REVIEW"
        ).scalar() or 0

        total_labeled = approved_count + rejected_count

        return {
            "total_human_reviewed": total_labeled,
            "approved_as_genuine": approved_count,
            "rejected_as_fraud": rejected_count,
            "pending_investigation": pending_count,
            "label_ratio_genuine_pct": round((approved_count / total_labeled * 100), 1) if total_labeled > 0 else 0.0,
            "label_ratio_fraud_pct": round((rejected_count / total_labeled * 100), 1) if total_labeled > 0 else 0.0,
            "eligible_for_retraining": total_labeled >= 10
        }

    def export_feedback_dataset(self) -> Path:
        """
        Extracts reviewed listings and merges them with sample data to create an augmented dataset.
        """
        reviewed = self.db.query(Listing).filter(
            Listing.status.in_(["APPROVED", "REJECTED"])
        ).all()

        records = []
        for item in reviewed:
            is_fraud_label = 1 if item.status == "REJECTED" else 0
            records.append({
                "listing_id": item.listing_id,
                "merchant_id": item.merchant_id,
                "title": item.title,
                "description": item.description,
                "category": item.category,
                "price": item.price,
                "market_price": item.market_price or item.price,
                "seller_rating": (item.evidence or {}).get("seller", {}).get("rating", 4.0) or 4.0,
                "account_age_days": (item.evidence or {}).get("seller", {}).get("account_age_days", 90) or 90,
                "complaints_count": (item.evidence or {}).get("seller", {}).get("complaints_count", 0) or 0,
                "is_fraud": is_fraud_label
            })

        feedback_df = pd.DataFrame(records)
        
        # Merge with baseline dataset if exists
        baseline_file = self.settings.DATA_DIR / "sample_listings.csv"
        if baseline_file.exists():
            base_df = pd.read_csv(baseline_file)
            # Remove any overlapping IDs if feedback records exist
            if not feedback_df.empty and "listing_id" in feedback_df.columns:
                base_df = base_df[~base_df["listing_id"].isin(feedback_df["listing_id"])]
                combined_df = pd.concat([base_df, feedback_df], ignore_index=True)
            else:
                combined_df = base_df
        else:
            combined_df = feedback_df

        augmented_path = self.settings.DATA_DIR / "augmented_training_dataset.csv"
        combined_df.to_csv(augmented_path, index=False)
        return augmented_path

    def trigger_retraining(self) -> Dict[str, Any]:
        """
        Exports the latest investigator decisions and retrains the ML classification pipeline.
        """
        augmented_dataset = self.export_feedback_dataset()
        results = train_and_evaluate_model(
            data_path=augmented_dataset,
            save_dir=self.settings.ML_MODELS_DIR
        )

        return {
            "status": "SUCCESS",
            "retrained_at": datetime.now(timezone.utc).isoformat(),
            "augmented_dataset": str(augmented_dataset.name),
            "model_metadata": results
        }
