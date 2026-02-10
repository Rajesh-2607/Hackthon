"""
Authentication utilities - password hashing and JWT token management.
Includes: Token blacklisting, refresh tokens, short expiration times.
"""
from datetime import datetime, timedelta
from typing import Optional, Tuple
import uuid
from passlib.context import CryptContext
from jose import JWTError, jwt

# Security configuration
SECRET_KEY = "your-secret-key-change-in-production-use-env-variable"  # Change this!
REFRESH_SECRET_KEY = "refresh-secret-key-different-from-access"  # Change this!
ALGORITHM = "HS256"

# Token expiration times
ACCESS_TOKEN_EXPIRE_MINUTES = 15  # Short-lived: 15 minutes
REFRESH_TOKEN_EXPIRE_DAYS = 7     # Longer-lived: 7 days

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a short-lived JWT access token.
    
    Args:
        data: Dictionary containing claims (e.g., {"sub": user_email})
        expires_delta: Optional custom expiration time
    
    Returns:
        Encoded JWT token string
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({
        "exp": expire,
        "type": "access",
        "jti": str(uuid.uuid4())  # Unique token ID for blacklisting
    })
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: dict) -> str:
    """
    Create a long-lived refresh token.
    
    Args:
        data: Dictionary containing claims (e.g., {"sub": user_email})
    
    Returns:
        Encoded JWT refresh token string
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    
    to_encode.update({
        "exp": expire,
        "type": "refresh",
        "jti": str(uuid.uuid4())  # Unique token ID for blacklisting
    })
    encoded_jwt = jwt.encode(to_encode, REFRESH_SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def create_token_pair(email: str) -> Tuple[str, str]:
    """
    Create both access and refresh tokens for a user.
    
    Args:
        email: User's email address
    
    Returns:
        Tuple of (access_token, refresh_token)
    """
    data = {"sub": email}
    access_token = create_access_token(data)
    refresh_token = create_refresh_token(data)
    return access_token, refresh_token


def decode_access_token(token: str) -> Optional[dict]:
    """
    Decode and verify an access token.
    
    Args:
        token: JWT access token string
    
    Returns:
        Decoded token payload or None if invalid
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("type") != "access":
            return None
        return payload
    except JWTError:
        return None


def decode_refresh_token(token: str) -> Optional[dict]:
    """
    Decode and verify a refresh token.
    
    Args:
        token: JWT refresh token string
    
    Returns:
        Decoded token payload or None if invalid
    """
    try:
        payload = jwt.decode(token, REFRESH_SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("type") != "refresh":
            return None
        return payload
    except JWTError:
        return None


# Legacy function for backwards compatibility
def decode_token(token: str) -> Optional[dict]:
    """Decode and verify a JWT token (access token)."""
    return decode_access_token(token)


def get_email_from_token(token: str) -> Optional[str]:
    """Extract email from a JWT access token."""
    payload = decode_access_token(token)
    if payload:
        return payload.get("sub")
    return None


def get_token_jti(token: str, token_type: str = "access") -> Optional[str]:
    """
    Get the unique token ID (jti) from a token.
    Used for blacklisting.
    
    Args:
        token: JWT token string
        token_type: "access" or "refresh"
    
    Returns:
        Token's jti or None if invalid
    """
    if token_type == "access":
        payload = decode_access_token(token)
    else:
        payload = decode_refresh_token(token)
    
    if payload:
        return payload.get("jti")
    return None
