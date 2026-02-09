"""
FastAPI Backend - Fake Account Detection API
"""
import os
import pickle
import numpy as np
from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from instagram_scraper import parse_instagram_input
from schemas import AccountFeatures, PredictionResponse, HealthResponse, InstagramScrapeRequest, UserRegister, UserLogin, TokenResponse, UserResponse
from utils import compute_engineered_features, identify_risk_factors, get_confidence_level, get_gemini_analysis, scan_for_suspicious_words
from database import get_db, init_db
from crud import create_analysis, get_all_analyses, get_recent_analyses, create_user, get_user_by_email, update_last_login
from models import AnalysisHistory, User
from auth import verify_password, create_access_token

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


@app.on_event("startup")
def startup_event():
    """Initialize database on startup."""
    init_db()
    print("[OK] Database ready.")


@app.get("/health", response_model=HealthResponse)
def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        is_model_loaded=model is not None,
        version="1.0.0"
    )


# ============== Authentication Endpoints ==============

@app.post("/register", response_model=TokenResponse)
def register(user_data: UserRegister, db: Session = Depends(get_db)):
    """
    Register a new user account.
    
    Returns JWT token on successful registration.
    """
    # Check if email already exists
    existing_user = get_user_by_email(db, user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )
    
    # Create new user
    new_user = create_user(
        db=db,
        email=user_data.email,
        password=user_data.password,
        full_name=user_data.full_name,
        phone=user_data.phone
    )
    
    # Generate token
    access_token = create_access_token(data={"sub": new_user.email})
    
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse(
            id=new_user.id,
            email=new_user.email,
            full_name=new_user.full_name,
            phone=new_user.phone,
            is_active=new_user.is_active,
            is_verified=new_user.is_verified,
            created_at=new_user.created_at
        )
    )


@app.post("/login", response_model=TokenResponse)
def login(credentials: UserLogin, db: Session = Depends(get_db)):
    """
    Login with email and password.
    
    Returns JWT token on successful authentication.
    """
    # Find user by email
    user = get_user_by_email(db, credentials.email)
    
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )
    
    # Verify password
    if not verify_password(credentials.password, user.password_hash):
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )
    
    # Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=403,
            detail="Account is disabled"
        )
    
    # Update last login
    update_last_login(db, user)
    
    # Generate token
    access_token = create_access_token(data={"sub": user.email})
    
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse(
            id=user.id,
            email=user.email,
            full_name=user.full_name,
            phone=user.phone,
            is_active=user.is_active,
            is_verified=user.is_verified,
            created_at=user.created_at
        )
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

    # Scan text content for suspicious words
    flagged_words = scan_for_suspicious_words(
        username=account.username,
        bio_text=account.bio_text
    )

    # Add flagged words to risk factors
    if flagged_words:
        for word in flagged_words:
            risk_factors.append(f"Suspicious text: \"{word}\"")

    # Gemini LLM analysis
    gemini_analysis = get_gemini_analysis(
        raw_features, risk_score, prediction,
        username=account.username,
        bio_text=account.bio_text,
        flagged_words=flagged_words
    )

    return PredictionResponse(
        prediction=prediction,
        risk_score=round(risk_score, 4),
        confidence=confidence,
        risk_factors=risk_factors,
        flagged_words=flagged_words if flagged_words else None,
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

    # Scan text content for suspicious words
    flagged_words = scan_for_suspicious_words(
        username=account.username,
        bio_text=account.bio_text
    )

    if flagged_words:
        for word in flagged_words:
            risk_factors.append(f"Suspicious text: \"{word}\"")

    return PredictionResponse(
        prediction=prediction,
        risk_score=round(risk_score, 4),
        confidence=confidence,
        risk_factors=risk_factors,
        flagged_words=flagged_words if flagged_words else None,
        gemini_analysis=None
    )


@app.post("/analyze", response_model=PredictionResponse)
def analyze_instagram(request: InstagramScrapeRequest, req: Request, db: Session = Depends(get_db)):
    """
    Analyze an Instagram profile by URL or username.
    Scrapes the profile, extracts features, and runs prediction.
    Results are saved to the database.
    
    Accepts:
    - Instagram URL: https://instagram.com/username
    - Username: @username or just username
    """
    if model is None or scaler is None:
        raise HTTPException(status_code=503, detail="Model not loaded. Train the model first.")
    
    try:
        # Scrape and extract features from Instagram profile
        scraped_data = parse_instagram_input(request.input)
        
        # Remove metadata for prediction (keep for reference)
        metadata = scraped_data.pop("_metadata", {})
        
        # Build raw_features dict
        raw_features = {
            "profile_pic": scraped_data["profile_pic"],
            "nums_length_username": scraped_data["nums_length_username"],
            "fullname_words": scraped_data["fullname_words"],
            "nums_length_fullname": scraped_data["nums_length_fullname"],
            "name_eq_username": scraped_data["name_eq_username"],
            "description_length": scraped_data["description_length"],
            "external_url": scraped_data["external_url"],
            "private": scraped_data["private"],
            "posts": scraped_data["posts"],
            "followers": scraped_data["followers"],
            "following": scraped_data["following"],
        }
        
        # Compute features & predict
        feature_vector = compute_engineered_features(raw_features)
        scaled_features = scaler.transform(feature_vector)
        
        risk_score = float(model.predict_proba(scaled_features)[0][1])
        prediction = "Fake Account" if risk_score >= 0.5 else "Real Account"
        confidence = get_confidence_level(risk_score)
        risk_factors = identify_risk_factors(raw_features, risk_score)
        
        # Gemini LLM analysis (include bio for better context)
        bio = metadata.get("biography", "")
        gemini_analysis = get_gemini_analysis(raw_features, risk_score, prediction, bio=bio)
        
        # Save to database
        try:
            client_ip = req.client.host if req.client else None
            create_analysis(
                db=db,
                input_url=request.input,
                username=metadata.get("username", ""),
                features=raw_features,
                prediction=prediction,
                risk_score=round(risk_score, 4),
                confidence=confidence,
                risk_factors=risk_factors,
                gemini_analysis=gemini_analysis,
                ip_address=client_ip
            )
            print(f"[OK] Analysis saved to database for: {metadata.get('username', 'unknown')}")
        except Exception as db_error:
            print(f"[WARN] Failed to save to database: {db_error}")
        
        return PredictionResponse(
            prediction=prediction,
            risk_score=round(risk_score, 4),
            confidence=confidence,
            risk_factors=risk_factors,
            gemini_analysis=gemini_analysis
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to analyze profile: {str(e)}")


@app.get("/history")
def get_history(skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    """
    Get analysis history from the database.
    
    Query params:
    - skip: Number of records to skip (default: 0)
    - limit: Max number of records to return (default: 50, max: 100)
    """
    if limit > 100:
        limit = 100
    
    analyses = get_all_analyses(db, skip=skip, limit=limit)
    
    return {
        "total": len(analyses),
        "skip": skip,
        "limit": limit,
        "results": [
            {
                "id": a.id,
                "input_url": a.input_url,
                "username": a.username,
                "prediction": a.prediction,
                "risk_score": a.risk_score,
                "confidence": a.confidence,
                "risk_factors": a.risk_factors,
                "analyzed_at": a.analyzed_at.isoformat() if a.analyzed_at else None,
                "features": {
                    "profile_pic": a.profile_pic,
                    "followers": a.followers,
                    "following": a.following,
                    "posts": a.posts,
                    "private": a.private
                }
            }
            for a in analyses
        ]
    }


@app.get("/recent-analyze")
def recent_analyze(limit: int = 10, db: Session = Depends(get_db)):
    """
    Get recent analyses with username, risk level, and timeline.
    
    Returns a simplified view of recent analyses for dashboard display.
    
    Query params:
    - limit: Number of recent analyses to return (default: 10, max: 50)
    """
    if limit > 50:
        limit = 50
    
    analyses = get_recent_analyses(db, limit=limit)
    
    def get_risk_level(risk_score: float) -> str:
        """Categorize risk score into High/Medium/Low."""
        if risk_score >= 0.7:
            return "High"
        elif risk_score >= 0.4:
            return "Medium"
        else:
            return "Low"
    
    def get_time_ago(analyzed_at) -> str:
        """Convert timestamp to human-readable time ago."""
        if not analyzed_at:
            return "Unknown"
        
        from datetime import datetime, timezone
        now = datetime.now(timezone.utc)
        
        # Handle timezone-naive datetime
        if analyzed_at.tzinfo is None:
            from datetime import timezone
            analyzed_at = analyzed_at.replace(tzinfo=timezone.utc)
        
        diff = now - analyzed_at
        seconds = diff.total_seconds()
        
        if seconds < 60:
            return "Just now"
        elif seconds < 3600:
            minutes = int(seconds // 60)
            return f"{minutes} min ago"
        elif seconds < 86400:
            hours = int(seconds // 3600)
            return f"{hours} hour{'s' if hours > 1 else ''} ago"
        else:
            days = int(seconds // 86400)
            return f"{days} day{'s' if days > 1 else ''} ago"
    
    return {
        "count": len(analyses),
        "analyses": [
            {
                "id": a.id,
                "username": a.username or "Unknown",
                "risk_score": round(a.risk_score, 2) if a.risk_score else 0,
                "risk_level": get_risk_level(a.risk_score) if a.risk_score else "Unknown",
                "prediction": a.prediction,
                "time_ago": get_time_ago(a.analyzed_at),
                "analyzed_at": a.analyzed_at.isoformat() if a.analyzed_at else None
            }
            for a in analyses
        ]
    }


