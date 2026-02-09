"""
SQLAlchemy ORM Models for storing Instagram analysis results.
"""
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text
from sqlalchemy.sql import func
from database import Base


class AnalysisHistory(Base):
    """
    Model to store Instagram profile analysis history.
    """
    __tablename__ = "analysis_history"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # Input data
    input_url = Column(String(500), nullable=False, index=True)
    username = Column(String(100), nullable=True, index=True)
    
    # Extracted features (11 features)
    profile_pic = Column(Integer, nullable=True)
    nums_length_username = Column(Float, nullable=True)
    fullname_words = Column(Integer, nullable=True)
    nums_length_fullname = Column(Float, nullable=True)
    name_eq_username = Column(Integer, nullable=True)
    description_length = Column(Integer, nullable=True)
    external_url = Column(Integer, nullable=True)
    private = Column(Integer, nullable=True)
    posts = Column(Integer, nullable=True)
    followers = Column(Integer, nullable=True)
    following = Column(Integer, nullable=True)
    
    # Prediction results
    prediction = Column(String(50), nullable=False)  # "Fake Account" or "Real Account"
    risk_score = Column(Float, nullable=False)
    confidence = Column(String(50), nullable=True)
    risk_factors = Column(Text, nullable=True)  # JSON string of risk factors
    gemini_analysis = Column(Text, nullable=True)
    
    # Metadata
    analyzed_at = Column(DateTime(timezone=True), server_default=func.now())
    ip_address = Column(String(50), nullable=True)
    
    def __repr__(self):
        return f"<AnalysisHistory(id={self.id}, username='{self.username}', prediction='{self.prediction}')>"


class ScrapedProfile(Base):
    """
    Model to store raw scraped Instagram profile data.
    """
    __tablename__ = "scraped_profiles"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # Profile info
    username = Column(String(100), nullable=False, unique=True, index=True)
    full_name = Column(String(200), nullable=True)
    biography = Column(Text, nullable=True)
    external_url = Column(String(500), nullable=True)
    profile_pic_url = Column(String(1000), nullable=True)
    
    # Stats
    followers_count = Column(Integer, default=0)
    following_count = Column(Integer, default=0)
    posts_count = Column(Integer, default=0)
    
    # Flags
    is_private = Column(Boolean, default=False)
    is_verified = Column(Boolean, default=False)
    
    # Timestamps
    scraped_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<ScrapedProfile(username='{self.username}', followers={self.followers_count})>"


class User(Base):
    """
    User model for authentication.
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # Authentication fields
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    
    # Profile info
    full_name = Column(String(200), nullable=True)
    phone = Column(String(20), nullable=True)
    
    # Account status
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_login = Column(DateTime(timezone=True), nullable=True)
    
    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}')>"

