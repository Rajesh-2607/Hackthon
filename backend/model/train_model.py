"""
XGBoost Model Training Pipeline for Fake Account Detection
"""
import os
import sys
import pandas as pd
import numpy as np
import pickle
from xgboost import XGBClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score,
    f1_score, roc_auc_score, classification_report, confusion_matrix
)

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(os.path.dirname(BASE_DIR), "data")
MODEL_DIR = os.path.dirname(os.path.abspath(__file__))

TRAIN_PATH = os.path.join(DATA_DIR, "train.csv")
TEST_PATH = os.path.join(DATA_DIR, "test.csv")
MODEL_PATH = os.path.join(MODEL_DIR, "xgboost_model.pkl")
SCALER_PATH = os.path.join(MODEL_DIR, "scaler.pkl")

# Feature column mapping (dataset cols -> clean names)
FEATURE_COLS = [
    "profile pic", "nums/length username", "fullname words",
    "nums/length fullname", "name==username", "description length",
    "external URL", "private", "#posts", "#followers", "#follows"
]
TARGET_COL = "fake"


def load_data():
    """Load and validate train/test datasets."""
    train_df = pd.read_csv(TRAIN_PATH)
    test_df = pd.read_csv(TEST_PATH)

    print(f"[INFO] Train shape: {train_df.shape}")
    print(f"[INFO] Test shape:  {test_df.shape}")
    print(f"[INFO] Train label distribution:\n{train_df[TARGET_COL].value_counts()}")
    print(f"[INFO] Missing values (train):\n{train_df.isnull().sum().sum()}")

    return train_df, test_df


def engineer_features(df):
    """Create additional features for better detection."""
    df = df.copy()

    # Follower-following ratio
    df["follower_following_ratio"] = df["#followers"] / (df["#follows"] + 1)

    # Posts per follower
    df["posts_per_follower"] = df["#posts"] / (df["#followers"] + 1)

    # Has description
    df["has_description"] = (df["description length"] > 0).astype(int)

    # High following (bots tend to follow many)
    df["high_following"] = (df["#follows"] > 1000).astype(int)

    # Username suspiciousness score (high digit ratio)
    df["suspicious_username"] = (df["nums/length username"] > 0.3).astype(int)

    # Engagement proxy: followers relative to posts
    df["engagement_proxy"] = df["#followers"] / (df["#posts"] + 1)

    return df


def train_model():
    """Full training pipeline."""
    print("=" * 60)
    print("  FAKE ACCOUNT DETECTION - MODEL TRAINING")
    print("=" * 60)

    # 1. Load data
    train_df, test_df = load_data()

    # 2. Feature engineering
    train_df = engineer_features(train_df)
    test_df = engineer_features(test_df)

    all_features = FEATURE_COLS + [
        "follower_following_ratio", "posts_per_follower",
        "has_description", "high_following",
        "suspicious_username", "engagement_proxy"
    ]

    X_train = train_df[all_features]
    y_train = train_df[TARGET_COL]
    X_test = test_df[all_features]
    y_test = test_df[TARGET_COL]

    # 3. Scale features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    # 4. Train XGBoost
    print("\n[TRAINING] XGBoost Classifier...")
    model = XGBClassifier(
        n_estimators=200,
        max_depth=6,
        learning_rate=0.1,
        subsample=0.8,
        colsample_bytree=0.8,
        reg_alpha=0.1,
        reg_lambda=1.0,
        random_state=42,
        eval_metric="logloss",
        use_label_encoder=False
    )
    model.fit(X_train_scaled, y_train)

    # 5. Evaluate
    y_pred = model.predict(X_test_scaled)
    y_proba = model.predict_proba(X_test_scaled)[:, 1]

    accuracy = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred)
    recall = recall_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred)
    roc_auc = roc_auc_score(y_test, y_proba)

    print("\n" + "=" * 60)
    print("  EVALUATION RESULTS")
    print("=" * 60)
    print(f"  Accuracy:  {accuracy:.4f}")
    print(f"  Precision: {precision:.4f}")
    print(f"  Recall:    {recall:.4f}")
    print(f"  F1 Score:  {f1:.4f}")
    print(f"  ROC-AUC:   {roc_auc:.4f}")
    print("=" * 60)
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred, target_names=["Real", "Fake"]))
    print("Confusion Matrix:")
    print(confusion_matrix(y_test, y_pred))

    # 6. Feature importance
    importance = model.feature_importances_
    feat_imp = sorted(zip(all_features, importance), key=lambda x: x[1], reverse=True)
    print("\nTop Feature Importances:")
    for feat, imp in feat_imp:
        print(f"  {feat:30s} {imp:.4f}")

    # 7. Save model & scaler
    os.makedirs(MODEL_DIR, exist_ok=True)
    with open(MODEL_PATH, "wb") as f:
        pickle.dump(model, f)
    with open(SCALER_PATH, "wb") as f:
        pickle.dump(scaler, f)

    print(f"\n[SAVED] Model  -> {MODEL_PATH}")
    print(f"[SAVED] Scaler -> {SCALER_PATH}")
    print("[DONE] Training complete!\n")

    return model, scaler


if __name__ == "__main__":
    train_model()
