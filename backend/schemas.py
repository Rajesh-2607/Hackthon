"""
Pydantic schemas for API request/response validation.
"""
from pydantic import BaseModel, Field
from typing import Optional


class AccountFeatures(BaseModel):
    """Input features for fake account prediction."""
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


class PredictionResponse(BaseModel):
    """Response from prediction endpoint."""
    prediction: str
    risk_score: float
    confidence: str
    risk_factors: list[str]
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
