"""
JWT Token utilities for UltraStake authentication.
Handles token creation, validation, and refresh logic.
"""

from datetime import datetime, timedelta
from typing import Optional, Dict
import jwt
import os
from functools import lru_cache

# Configuration
SECRET_KEY = os.getenv("SECRET_KEY", "CHANGE_ME_SUPER_SECRET")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))

class TokenError(Exception):
    """Custom exception for token-related errors"""
    pass

def create_access_token(user_id: str, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token.
    
    Args:
        user_id: The user's unique identifier
        expires_delta: Optional custom expiration time
        
    Returns:
        Encoded JWT token string
    """
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    payload = {
        "sub": user_id,
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "access"
    }
    
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def create_refresh_token(user_id: str) -> str:
    """
    Create a JWT refresh token.
    
    Args:
        user_id: The user's unique identifier
        
    Returns:
        Encoded JWT token string
    """
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    
    payload = {
        "sub": user_id,
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "refresh"
    }
    
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(token: str) -> Optional[Dict]:
    """
    Verify and decode a JWT token.
    
    Args:
        token: The JWT token string to verify
        
    Returns:
        Decoded payload dictionary if valid, None otherwise
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise TokenError("Token has expired")
    except jwt.InvalidTokenError:
        raise TokenError("Invalid token")
    except Exception as e:
        raise TokenError(f"Token verification failed: {str(e)}")

def verify_access_token(token: str) -> Optional[Dict]:
    """
    Verify an access token specifically.
    
    Args:
        token: The JWT token string to verify
        
    Returns:
        Decoded payload if valid access token
        
    Raises:
        TokenError: If token is invalid or not an access token
    """
    payload = verify_token(token)
    
    if payload.get("type") != "access":
        raise TokenError("Invalid token type. Expected 'access' token")
    
    return payload

def verify_refresh_token(token: str) -> Optional[Dict]:
    """
    Verify a refresh token specifically.
    
    Args:
        token: The JWT token string to verify
        
    Returns:
        Decoded payload if valid refresh token
        
    Raises:
        TokenError: If token is invalid or not a refresh token
    """
    payload = verify_token(token)
    
    if payload.get("type") != "refresh":
        raise TokenError("Invalid token type. Expected 'refresh' token")
    
    return payload

def refresh_access_token(refresh_token: str) -> str:
    """
    Generate a new access token from a valid refresh token.
    
    Args:
        refresh_token: Valid refresh token
        
    Returns:
        New access token
        
    Raises:
        TokenError: If refresh token is invalid
    """
    payload = verify_refresh_token(refresh_token)
    user_id = payload.get("sub")
    
    return create_access_token(user_id)

def get_user_id_from_token(token: str) -> str:
    """
    Extract user_id from a valid token.
    
    Args:
        token: JWT token string
        
    Returns:
        User ID
        
    Raises:
        TokenError: If token is invalid
    """
    payload = verify_token(token)
    return payload.get("sub")
