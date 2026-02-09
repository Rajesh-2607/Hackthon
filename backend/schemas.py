"""
Pydantic schemas for API request/response validation.
Updated to match training data (11 features, NO verification).
"""

from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime


# ============== User Authentication Schemas ==============

class UserRegister(BaseModel):
    """Request schema for user registration."""
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., min_length=6, description="Password (min 6 characters)")
    full_name: Optional[str] = Field(None, description="User's full name")
    phone: Optional[str] = Field(None, description="Phone number")


class UserLogin(BaseModel):
    """Request schema for user login."""
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., description="User password")


class UserResponse(BaseModel):
    """Response schema for user data (excludes password)."""
    id: int
    email: str
    full_name: Optional[str] = None
    phone: Optional[str] = None
    is_active: bool = True
    is_verified: bool = False
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    """Response schema for authentication token."""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


# ============== Account Features Schemas ==============


class AccountFeatures(BaseModel):
    """
    Input features for fake account prediction.
    Matches training data columns (11 features):
    'profile pic', 'nums/length username', 'fullname words',
    'nums/length fullname', 'name==username', 'description length',
    'external URL', 'private', '#posts', '#followers', '#follows'
    """
    profile_pic: int = Field(..., ge=0, le=1, description="Has profile picture (0 or 1)")
    nums_length_username: float = Field(..., ge=0, le=1, description="Ratio of digits in username")
    fullname_words: int = Field(..., ge=0, description="Number of words in full name")
    nums_length_fullname: float = Field(..., ge=0, le=1, description="Ratio of digits in full name")
    name_eq_username: int = Field(..., ge=0, le=1, description="Name equals username (0 or 1)")
    description_length: int = Field(..., ge=0, description="Bio/description character length")
    external_url: int = Field(..., ge=0, le=1, description="Has external URL (0 or 1)")
    private: int = Field(..., ge=0, le=1, description="Is private account (0 or 1)")
    posts: int = Field(..., ge=0, description="Number of posts")
    followers: int = Field(..., ge=0, description="Number of followers")
    following: int = Field(..., ge=0, description="Number of following")
    # Optional text fields for deeper analysis
    username: Optional[str] = Field(None, description="The actual username text for analysis")
    bio_text: Optional[str] = Field(None, description="The actual bio/description text for analysis")

class InstagramScrapeRequest(BaseModel):
    """Request for scraping Instagram profile."""
    input: str = Field(..., description="Instagram URL or username (e.g., '@username' or 'https://instagram.com/username')")

class PredictionResponse(BaseModel):
    """Response from prediction endpoint."""
    prediction: str
    risk_score: float
    confidence: str
    risk_factors: list[str]
    flagged_words: Optional[list[str]] = None
    gemini_analysis: Optional[str] = None

class GeminiAnalysisRequest(BaseModel):
    """Request for Gemini LLM analysis."""
    features: AccountFeatures
    risk_score: float
    prediction: str

class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    model_loaded: bool
    version: str
