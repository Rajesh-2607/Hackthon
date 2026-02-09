"""
CRUD operations for database models.
"""
from sqlalchemy.orm import Session
from models import AnalysisHistory, ScrapedProfile, User
from typing import List, Optional
from datetime import datetime
import json
from auth import hash_password


# ============== User CRUD ==============

def create_user(
    db: Session,
    email: str,
    password: str,
    full_name: Optional[str] = None,
    phone: Optional[str] = None
) -> User:
    """
    Create a new user with hashed password.
    """
    db_user = User(
        email=email,
        password_hash=hash_password(password),
        full_name=full_name,
        phone=phone
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """Get a user by email address."""
    return db.query(User).filter(User.email == email).first()


def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    """Get a user by ID."""
    return db.query(User).filter(User.id == user_id).first()


def update_last_login(db: Session, user: User) -> User:
    """Update user's last login timestamp."""
    user.last_login = datetime.utcnow()
    db.commit()
    db.refresh(user)
    return user


# ============== AnalysisHistory CRUD ==============

def create_analysis(
    db: Session,
    input_url: str,
    username: str,
    features: dict,
    prediction: str,
    risk_score: float,
    confidence: str,
    risk_factors: List[str],
    gemini_analysis: Optional[str] = None,
    ip_address: Optional[str] = None
) -> AnalysisHistory:
    """
    Save a new analysis result to the database.
    """
    db_analysis = AnalysisHistory(
        input_url=input_url,
        username=username,
        profile_pic=features.get("profile_pic"),
        nums_length_username=features.get("nums_length_username"),
        fullname_words=features.get("fullname_words"),
        nums_length_fullname=features.get("nums_length_fullname"),
        name_eq_username=features.get("name_eq_username"),
        description_length=features.get("description_length"),
        external_url=features.get("external_url"),
        private=features.get("private"),
        posts=features.get("posts"),
        followers=features.get("followers"),
        following=features.get("following"),
        prediction=prediction,
        risk_score=risk_score,
        confidence=confidence,
        risk_factors=json.dumps(risk_factors),
        gemini_analysis=gemini_analysis,
        ip_address=ip_address
    )
    
    db.add(db_analysis)
    db.commit()
    db.refresh(db_analysis)
    return db_analysis


def get_analysis_by_id(db: Session, analysis_id: int) -> Optional[AnalysisHistory]:
    """Get a single analysis by ID."""
    return db.query(AnalysisHistory).filter(AnalysisHistory.id == analysis_id).first()


def get_analyses_by_username(db: Session, username: str) -> List[AnalysisHistory]:
    """Get all analyses for a specific username."""
    return db.query(AnalysisHistory).filter(AnalysisHistory.username == username).all()


def get_all_analyses(db: Session, skip: int = 0, limit: int = 100) -> List[AnalysisHistory]:
    """Get all analyses with pagination."""
    return db.query(AnalysisHistory).order_by(AnalysisHistory.analyzed_at.desc()).offset(skip).limit(limit).all()


def get_recent_analyses(db: Session, limit: int = 10) -> List[AnalysisHistory]:
    """Get the most recent analyses."""
    return db.query(AnalysisHistory).order_by(AnalysisHistory.analyzed_at.desc()).limit(limit).all()


def delete_analysis(db: Session, analysis_id: int) -> bool:
    """Delete an analysis by ID."""
    analysis = get_analysis_by_id(db, analysis_id)
    if analysis:
        db.delete(analysis)
        db.commit()
        return True
    return False


# ============== ScrapedProfile CRUD ==============

def create_or_update_profile(
    db: Session,
    username: str,
    full_name: str = None,
    biography: str = None,
    external_url: str = None,
    profile_pic_url: str = None,
    followers_count: int = 0,
    following_count: int = 0,
    posts_count: int = 0,
    is_private: bool = False,
    is_verified: bool = False
) -> ScrapedProfile:
    """
    Create a new profile or update existing one.
    """
    existing = db.query(ScrapedProfile).filter(ScrapedProfile.username == username).first()
    
    if existing:
        # Update existing
        existing.full_name = full_name
        existing.biography = biography
        existing.external_url = external_url
        existing.profile_pic_url = profile_pic_url
        existing.followers_count = followers_count
        existing.following_count = following_count
        existing.posts_count = posts_count
        existing.is_private = is_private
        existing.is_verified = is_verified
        db.commit()
        db.refresh(existing)
        return existing
    else:
        # Create new
        db_profile = ScrapedProfile(
            username=username,
            full_name=full_name,
            biography=biography,
            external_url=external_url,
            profile_pic_url=profile_pic_url,
            followers_count=followers_count,
            following_count=following_count,
            posts_count=posts_count,
            is_private=is_private,
            is_verified=is_verified
        )
        db.add(db_profile)
        db.commit()
        db.refresh(db_profile)
        return db_profile


def get_profile_by_username(db: Session, username: str) -> Optional[ScrapedProfile]:
    """Get a profile by username."""
    return db.query(ScrapedProfile).filter(ScrapedProfile.username == username).first()


def get_all_profiles(db: Session, skip: int = 0, limit: int = 100) -> List[ScrapedProfile]:
    """Get all profiles with pagination."""
    return db.query(ScrapedProfile).offset(skip).limit(limit).all()
