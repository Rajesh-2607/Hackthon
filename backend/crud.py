"""
CRUD operations for database models.
"""
from sqlalchemy.orm import Session
from models import AnalysisHistory, ScrapedProfile, User, TokenBlacklist, RefreshToken
from typing import List, Optional
from datetime import datetime
import json
import hashlib
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


def get_latest_analysis_by_username(db: Session, username: str) -> Optional[AnalysisHistory]:
    """
    Get the most recent analysis for a specific username.
    Used for caching - returns None if no previous analysis exists.
    """
    return db.query(AnalysisHistory).filter(
        AnalysisHistory.username == username
    ).order_by(AnalysisHistory.analyzed_at.desc()).first()


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


# ============== Token Blacklist CRUD ==============

def _hash_token(token: str) -> str:
    """Create a hash of a token for secure storage."""
    return hashlib.sha256(token.encode()).hexdigest()


def blacklist_token(
    db: Session,
    jti: str,
    token_type: str,
    expires_at: datetime,
    user_email: Optional[str] = None
) -> TokenBlacklist:
    """
    Add a token to the blacklist.
    Called on logout to invalidate tokens.
    """
    db_blacklist = TokenBlacklist(
        jti=jti,
        token_type=token_type,
        user_email=user_email,
        expires_at=expires_at
    )
    db.add(db_blacklist)
    db.commit()
    db.refresh(db_blacklist)
    return db_blacklist


def is_token_blacklisted(db: Session, jti: str) -> bool:
    """Check if a token's JTI is in the blacklist."""
    return db.query(TokenBlacklist).filter(TokenBlacklist.jti == jti).first() is not None


def cleanup_expired_blacklist(db: Session) -> int:
    """Remove expired tokens from blacklist to save space."""
    result = db.query(TokenBlacklist).filter(
        TokenBlacklist.expires_at < datetime.utcnow()
    ).delete()
    db.commit()
    return result


# ============== Refresh Token CRUD ==============

def store_refresh_token(
    db: Session,
    jti: str,
    user_email: str,
    token: str,
    expires_at: datetime
) -> RefreshToken:
    """
    Store a refresh token in the database.
    Token is hashed for security.
    """
    db_token = RefreshToken(
        jti=jti,
        user_email=user_email,
        token_hash=_hash_token(token),
        expires_at=expires_at
    )
    db.add(db_token)
    db.commit()
    db.refresh(db_token)
    return db_token


def get_refresh_token(db: Session, jti: str) -> Optional[RefreshToken]:
    """Get a refresh token by its JTI."""
    return db.query(RefreshToken).filter(RefreshToken.jti == jti).first()


def validate_refresh_token(db: Session, jti: str, token: str) -> bool:
    """
    Validate a refresh token exists and is not revoked.
    Also verifies the token hash matches.
    """
    db_token = get_refresh_token(db, jti)
    if not db_token:
        return False
    if db_token.is_revoked:
        return False
    if db_token.expires_at < datetime.utcnow():
        return False
    # Verify token hash
    if db_token.token_hash != _hash_token(token):
        return False
    return True


def revoke_refresh_token(db: Session, jti: str) -> bool:
    """Revoke a specific refresh token."""
    db_token = get_refresh_token(db, jti)
    if db_token:
        db_token.is_revoked = True
        db_token.revoked_at = datetime.utcnow()
        db.commit()
        return True
    return False


def revoke_all_user_tokens(db: Session, user_email: str) -> int:
    """Revoke all refresh tokens for a user (e.g., on password change)."""
    result = db.query(RefreshToken).filter(
        RefreshToken.user_email == user_email,
        RefreshToken.is_revoked == False
    ).update({
        "is_revoked": True,
        "revoked_at": datetime.utcnow()
    })
    db.commit()
    return result


def rotate_refresh_token(
    db: Session,
    old_jti: str,
    new_jti: str,
    user_email: str,
    new_token: str,
    expires_at: datetime
) -> Optional[RefreshToken]:
    """
    Rotate a refresh token: revoke old one, create new one.
    Used for refresh token rotation security.
    """
    # Revoke old token and mark replacement
    old_token = get_refresh_token(db, old_jti)
    if old_token:
        old_token.is_revoked = True
        old_token.revoked_at = datetime.utcnow()
        old_token.replaced_by = new_jti
    
    # Create new token
    new_token_record = store_refresh_token(
        db=db,
        jti=new_jti,
        user_email=user_email,
        token=new_token,
        expires_at=expires_at
    )
    
    return new_token_record


def cleanup_expired_refresh_tokens(db: Session) -> int:
    """Remove expired refresh tokens to save space."""
    result = db.query(RefreshToken).filter(
        RefreshToken.expires_at < datetime.utcnow()
    ).delete()
    db.commit()
    return result
