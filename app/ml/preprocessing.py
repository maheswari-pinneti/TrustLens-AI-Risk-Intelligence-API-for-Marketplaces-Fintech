"""
Data Preprocessing & Splitting Pipeline
"""
from typing import Tuple
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from app.ml.feature_engineering import extract_features_df, FEATURE_COLUMNS


def prepare_train_test_data(
    df: pd.DataFrame,
    target_col: str = "is_fraud",
    test_size: float = 0.2,
    random_state: int = 42
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]:
    """
    Extracts features and splits into stratified train and test partitions to prevent leakage.
    """
    X = extract_features_df(df)
    y = df[target_col].astype(int)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y,
        test_size=test_size,
        random_state=random_state,
        stratify=y
    )

    return X_train, X_test, y_train, y_test
