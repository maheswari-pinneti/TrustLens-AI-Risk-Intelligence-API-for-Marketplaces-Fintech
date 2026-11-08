"""
Model Retraining CLI Script
"""
import sys
from pathlib import Path

# Add project root to path
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from app.ml.train import train_and_evaluate_model


if __name__ == "__main__":
    print("Initiating TrustLens Machine Learning Pipeline...")
    results = train_and_evaluate_model()
    print("Training Pipeline Complete!")
    print(f"Metrics: {results['evaluation_metrics']}")
