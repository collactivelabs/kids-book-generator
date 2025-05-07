"""
Authentication utilities for the Kids Book Generator.

This module provides functions for handling API authentication,
token management, and external API credentials.
"""
import jwt
import logging
from datetime import datetime, timedelta
from typing import Dict, Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext

from config import settings


from utils.logging import get_logger

logger = get_logger(__name__)

# Setup password context for hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Setup OAuth2 scheme for token authentication with scopes
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/v1/auth/token",
    auto_error=True,
    scopes={
        "users:read": "Read user information",
        "users:write": "Modify user information",
        "books:read": "Read book information",
        "books:write": "Create and modify books",
        "admin": "Admin access",
    }
)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against a hash.
    
    Args:
        plain_password: Plain text password
        hashed_password: Hashed password
        
    Returns:
        True if the password matches the hash
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Hash a password using bcrypt.
    
    Args:
        password: Plain text password
        
    Returns:
        Hashed password
    """
    return pwd_context.hash(password)


def create_access_token(data: Dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token.
    
    Args:
        data: Data to encode in the token
        expires_delta: Optional expiration time
        
    Returns:
        Encoded JWT token
    """
    to_encode = data.copy()
    
    # Set expiration time
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    
    # Add expiration time to token data - ensure we use integer timestamp
    # This is critical as PyJWT expects exp to be an integer timestamp
    to_encode.update({"exp": int(expire.timestamp())})
    
    logger.debug(f"Creating token with data: {to_encode}")
    logger.debug(f"Using key: {settings.SECRET_KEY[:5]}... and algorithm: {settings.ALGORITHM}")
    
    # Encode token with JWT
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )
    
    logger.debug(f"Token created: {encoded_jwt[:10]}...")
    return encoded_jwt


async def get_current_user(token: str = Depends(oauth2_scheme)):
    """
    Verify and decode JWT token to get current user.
    
    Args:
        token: JWT token from Authorization header
        
    Returns:
        User data from token
        
    Raises:
        HTTPException: If token is invalid
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # For debugging, print the token information
        logger.debug(f"Decoding token with SECRET_KEY starting with {settings.SECRET_KEY[:5]}...")
        
        # Decode JWT token with explicit disabling of verification options
        # This is only for development/testing - should be properly configured in production
        payload = jwt.decode(
            token, 
            settings.SECRET_KEY, 
            algorithms=[settings.ALGORITHM],
            options={
                "verify_signature": True,  # Verify the signature
                "verify_exp": True,       # Verify expiration time
                "verify_nbf": False,      # Skip "not before" time verification
                "verify_iat": False,      # Skip "issued at" time verification
                "verify_aud": False,      # Skip audience verification
                "verify_iss": False,      # Skip issuer verification
                "require": ["exp"]      # Require expiration time
            }
        )
        return payload
    except jwt.PyJWTError as e:
        logger.error(f"JWT decode error: {str(e)}")
        raise credentials_exception


class OpenAIAuth:
    """Utility for managing OpenAI API authentication."""
    
    @staticmethod
    def get_api_key() -> str:
        """
        Get the OpenAI API key from settings.
        
        Returns:
            API key string
            
        Raises:
            ValueError: If API key is not set
        """
        api_key = settings.OPENAI_API_KEY
        if not api_key:
            raise ValueError("OpenAI API key is not set")
        return api_key


class CanvaAuth:
    """Utility for managing Canva API authentication."""
    
    @staticmethod
    def get_oauth_url() -> str:
        """
        Get the Canva OAuth authorization URL.
        
        Returns:
            Authorization URL string
        """
        client_id = settings.CANVA_CLIENT_ID
        redirect_uri = settings.CANVA_REDIRECT_URI
        
        if not client_id:
            raise ValueError("Canva client ID is not set")
        
        # Construct OAuth URL with required parameters
        oauth_url = (
            f"https://www.canva.com/oauth/authorize?"
            f"client_id={client_id}&"
            f"redirect_uri={redirect_uri}&"
            f"response_type=code&"
            f"scope=designs.read%20designs.write"
        )
        
        return oauth_url
    
    @staticmethod
    async def exchange_code_for_token(authorization_code: str) -> Dict:
        """
        Exchange authorization code for access token.
        
        Args:
            authorization_code: Authorization code from OAuth callback
            
        Returns:
            Dictionary with token information
            
        Raises:
            ValueError: If client credentials are not set
        """
        client_id = settings.CANVA_CLIENT_ID
        client_secret = settings.CANVA_CLIENT_SECRET
        redirect_uri = settings.CANVA_REDIRECT_URI
        
        if not client_id or not client_secret:
            raise ValueError("Canva client credentials are not set")
        
        # This is a placeholder - will be implemented with actual API calls
        # when we set up the HTTP client
        
        # Mock response for now
        mock_token_response = {
            "access_token": "mock_access_token",
            "token_type": "bearer",
            "expires_in": 3600,
            "refresh_token": "mock_refresh_token"
        }
        
        return mock_token_response
