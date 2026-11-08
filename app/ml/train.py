"""
Model Training and Rigorous Evaluation Pipeline
"""
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any
import joblib
import pandas as pd
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score,
    f1_score, roc_auc_score, confusion_matrix
)
from app.config import get_settings
from app.ml.feature_engineering import FEATURE_COLUMNS
from app.ml.preprocessing import prepare_train_test_data


def train_and_evaluate_model(
    data_path: Path = None,
    save_dir: Path = None
) -> Dict[str, Any]:
    settings = get_settings()
    dataset_file = data_path or (settings.DATA_DIR / "sample_listings.csv")
    output_dir = save_dir or settings.ML_MODELS_DIR
    output_dir.mkdir(parents=True, exist_ok=True)

    if not dataset_file.exists():
        raise FileNotFoundError(f"Dataset file {dataset_file} not found.")

    df = pd.read_csv(dataset_file)
    X_train, X_test, y_train, y_test = prepare_train_test_data(df)

    # 1. Baseline Model: Logistic Regression
    lr_pipe = Pipeline([
        ("scaler", StandardScaler()),
        ("classifier", LogisticRegression(random_state=42, max_iter=1000))
    ])
    lr_pipe.fit(X_train, y_train)
    lr_preds = lr_pipe.predict(X_test)
    lr_f1 = f1_score(y_test, lr_preds)

    # 2. Production Model: Random Forest Classifier
    rf_pipe = Pipeline([
        ("scaler", StandardScaler()),
        ("classifier", RandomForestClassifier(
            n_estimators=120,
            max_depth=8,
            min_samples_split=4,
            class_weight="balanced",
            random_state=42
        ))
    ])
    rf_pipe.fit(X_train, y_train)

    # Evaluation on Holdout Test Set
    test_preds = rf_pipe.predict(X_test)
    test_probs = rf_pipe.predict_proba(X_test)[:, 1]

    acc = float(accuracy_score(y_test, test_preds))
    prec = float(precision_score(y_test, test_preds))
    rec = float(recall_score(y_test, test_preds))
    f1 = float(f1_score(y_test, test_preds))
    auc = float(roc_auc_score(y_test, test_probs))
    cm = confusion_matrix(y_test, test_preds).tolist()

    # Feature importances
    rf_model = rf_pipe.named_steps["classifier"]
    importances = {
        col: round(float(imp), 4)
        for col, imp in zip(FEATURE_COLUMNS, rf_model.feature_importances_)
    }
    sorted_importances = dict(sorted(importances.items(), key=lambda x: x[1], reverse=True))

    # Persist Artifacts
    model_artifact_path = output_dir / "fraud_model.joblib"
    joblib.dump(rf_pipe, model_artifact_path)

    metadata = {
        "version": "1.0.0",
        "algorithm": "RandomForestClassifier",
        "trained_at": datetime.utcnow().isoformat(),
        "training_samples": len(X_train),
        "test_samples": len(X_test),
        "evaluation_metrics": {
            "accuracy": round(acc, 4),
            "precision": round(prec, 4),
            "recall": round(rec, 4),
            "f1_score": round(f1, 4),
            "roc_auc": round(auc, 4),
            "confusion_matrix": cm,
            "baseline_lr_f1": round(float(lr_f1), 4)
        },
        "feature_importances": sorted_importances,
        "feature_names": FEATURE_COLUMNS,
        "model_file": str(model_artifact_path.name)
    }

    metadata_path = output_dir / "model_metadata.json"
    with open(metadata_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)

    print(f"Model saved to: {model_artifact_path}")
    print(f"Evaluation: Precision={prec:.3f}, Recall={rec:.3f}, F1={f1:.3f}, ROC-AUC={auc:.3f}")
    return metadata


if __name__ == "__main__":
    train_and_evaluate_model()
