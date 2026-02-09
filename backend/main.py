"""
FastAPI Backend - Fake Account Detection API
"""
import os
import pickle
import numpy as np
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from schemas import AccountFeatures, PredictionResponse, HealthResponse
from utils import compute_engineered_features, identify_risk_factors, get_confidence_level, get_gemini_analysis

# Paths
MODEL_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "model")
MODEL_PATH = os.path.join(MODEL_DIR, "xgboost_model.pkl")
SCALER_PATH = os.path.join(MODEL_DIR, "scaler.pkl")

# Load model & scaler
model = None
scaler = None

def load_artifacts():
    global model, scaler
    try:
        with open(MODEL_PATH, "rb") as f:
            model = pickle.load(f)
        with open(SCALER_PATH, "rb") as f:
            scaler = pickle.load(f)
        print("[OK] Model and scaler loaded successfully.")
    except FileNotFoundError:
        print("[WARN] Model files not found. Run 'python model/train_model.py' first.")

load_artifacts()

# FastAPI app
app = FastAPI(
    title="Fake Account Detection API",
    description="Hybrid AI system using XGBoost + Gemini 2.5 for detecting fake social media accounts",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", response_model=HealthResponse)
def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        model_loaded=model is not None,
        version="1.0.0"
    )


@app.post("/predict", response_model=PredictionResponse)
def predict(account: AccountFeatures):
    """
    Predict if a social media account is fake.
    Returns risk score, prediction, confidence, risk factors, and Gemini analysis.
    """
    if model is None or scaler is None:
        raise HTTPException(status_code=503, detail="Model not loaded. Train the model first.")

    # Convert input to dict
    raw_features = {
        "profile_pic": account.profile_pic,
        "nums_length_username": account.nums_length_username,
        "fullname_words": account.fullname_words,
        "nums_length_fullname": account.nums_length_fullname,
        "name_eq_username": account.name_eq_username,
        "description_length": account.description_length,
        "external_url": account.external_url,
        "private": account.private,
        "posts": account.posts,
        "followers": account.followers,
        "following": account.following,
    }

    # Compute features & predict
    feature_vector = compute_engineered_features(raw_features)
    scaled_features = scaler.transform(feature_vector)

    risk_score = float(model.predict_proba(scaled_features)[0][1])
    prediction = "Fake Account" if risk_score >= 0.5 else "Real Account"
    confidence = get_confidence_level(risk_score)
    risk_factors = identify_risk_factors(raw_features, risk_score)

    # Gemini LLM analysis
    gemini_analysis = get_gemini_analysis(raw_features, risk_score, prediction)

    return PredictionResponse(
        prediction=prediction,
        risk_score=round(risk_score, 4),
        confidence=confidence,
        risk_factors=risk_factors,
        gemini_analysis=gemini_analysis
    )


@app.post("/predict/quick", response_model=PredictionResponse)
def predict_quick(account: AccountFeatures):
    """
    Quick prediction without Gemini analysis (faster response).
    """
    if model is None or scaler is None:
        raise HTTPException(status_code=503, detail="Model not loaded. Train the model first.")

    raw_features = {
        "profile_pic": account.profile_pic,
        "nums_length_username": account.nums_length_username,
        "fullname_words": account.fullname_words,
        "nums_length_fullname": account.nums_length_fullname,
        "name_eq_username": account.name_eq_username,
        "description_length": account.description_length,
        "external_url": account.external_url,
        "private": account.private,
        "posts": account.posts,
        "followers": account.followers,
        "following": account.following,
    }

    feature_vector = compute_engineered_features(raw_features)
    scaled_features = scaler.transform(feature_vector)

    risk_score = float(model.predict_proba(scaled_features)[0][1])
    prediction = "Fake Account" if risk_score >= 0.5 else "Real Account"
    confidence = get_confidence_level(risk_score)
    risk_factors = identify_risk_factors(raw_features, risk_score)

    return PredictionResponse(
        prediction=prediction,
        risk_score=round(risk_score, 4),
        confidence=confidence,
        risk_factors=risk_factors,
        gemini_analysis=None
    )
