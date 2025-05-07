"""
Authentication controllers for the Kids Book Generator.

This module handles authentication endpoints, including OAuth flows
and API key management.
"""
import os
import json
import logging
from typing import Dict, Optional, List, Union, Any
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Request, Security
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm, SecurityScopes
from pydantic import BaseModel, Field, ValidationError

from jose import JWTError, jwt

from src.config import settings
from src.utils.auth import create_access_token, verify_password, get_password_hash
from src.integrations.canva import canva_client
from src.utils.logging import get_logger

logger = get_logger(__name__)

# OAuth2 password bearer token setup
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/v1/auth/token",
    scopes={
        "users:read": "Read user information",
        "users:write": "Modify user information",
        "books:read": "Read book information",
        "books:write": "Create and modify books",
        "admin": "Admin access",
    }
)


class Token(BaseModel):
    """OAuth2 token response model."""
    access_token: str
    token_type: str = "bearer"
    expires_at: datetime
    scopes: List[str] = Field(default_factory=list)


class TokenData(BaseModel):
    """Data extracted from token."""
    username: Optional[str] = None
    scopes: List[str] = Field(default_factory=list)
    exp: Optional[datetime] = None


class User(BaseModel):
    """User model."""
    username: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    disabled: bool = False
    scopes: List[str] = Field(default_factory=list)


class UserInDB(User):
    """User model with password hash."""
    hashed_password: str


class CanvaCredentials(BaseModel):
    """Canva OAuth credentials."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_at: datetime


# Mock user database - in a real application, this would be a database
fake_users_db = {
    "admin": {
        "username": "admin",
        "email": "admin@example.com",
        "full_name": "Admin User",
        "hashed_password": get_password_hash("admin"),
        "disabled": False,
        "scopes": ["users:read", "users:write", "books:read", "books:write", "admin"],
    },
    "user": {
        "username": "user",
        "email": "user@example.com",
        "full_name": "Regular User",
        "hashed_password": get_password_hash("user"),
        "disabled": False,
        "scopes": ["books:read", "books:write"],
    },
}


def get_user(db, username: str) -> Optional[UserInDB]:
    """Get user from database."""
    if username in db:
        user_dict = db[username]
        return UserInDB(**user_dict)
    return None


async def authenticate_user(db, username: str, password: str) -> Optional[UserInDB]:
    """Authenticate user."""
    user = get_user(db, username)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


async def handle_token_generation(form_data: OAuth2PasswordRequestForm = Depends()) -> Token:
    """
    Handle user authentication and token generation.
    
    Args:
        form_data: OAuth2 password request form
        
    Returns:
        Token model with access token
        
    Raises:
        HTTPException: If authentication fails
    """
    user = await authenticate_user(fake_users_db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if user.disabled:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user",
        )
    
    # Determine scopes from requested and available scopes
    scopes = []
    for scope in form_data.scopes:
        if scope in user.scopes:
            scopes.append(scope)
    
    # If no scopes were requested or matched, use all available scopes
    if not scopes:
        scopes = user.scopes
    
    # Create access token with 30 minute expiration
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    expires_at = datetime.utcnow() + access_token_expires
    
    access_token = create_access_token(
        data={
            "sub": user.username,
            "scopes": scopes,
            "exp": expires_at.timestamp()
        }
    )
    
    return Token(
        access_token=access_token,
        token_type="bearer",
        expires_at=expires_at,
        scopes=scopes
    )


async def handle_canva_authorize(username: str = None) -> Dict:
    """
    Generate Canva OAuth authorization URL.
    
    Args:
        username: Optional username to associate with the Canva authorization
        
    Returns:
        Dictionary with authorization URL and state
    """
    try:
        # Generate state parameter with username if provided
        state_data = {"timestamp": datetime.utcnow().timestamp()}
        if username:
            state_data["username"] = username
        
        state = jwt.encode(state_data, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        auth_url = canva_client.get_authorization_url(state=state)
        
        return {"authorization_url": auth_url, "state": state}
    except Exception as e:
        logger.error(f"Canva OAuth error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Canva OAuth error: {str(e)}"
        )


async def handle_canva_callback(code: str, state: Optional[str] = None) -> RedirectResponse:
    """
    Handle Canva OAuth callback.
    
    Args:
        code: Authorization code from Canva
        state: State parameter from authorization
        
    Returns:
        Redirect response to frontend
    """
    try:
        # Validate state parameter
        username = None
        if state:
            try:
                state_data = jwt.decode(state, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
                username = state_data.get("username")
            except JWTError:
                logger.warning("Invalid state parameter in Canva callback")
        
        # Exchange code for token
        token_response = await canva_client.exchange_code_for_token(code)
        
        # Create Canva credentials
        expires_at = datetime.utcnow() + timedelta(seconds=token_response["expires_in"])
        canva_credentials = CanvaCredentials(
            access_token=token_response["access_token"],
            refresh_token=token_response["refresh_token"],
            token_type=token_response["token_type"],
            expires_at=expires_at
        )
        
        # In a real application, you would store these credentials in a database
        # associated with the user identified by the 'username' variable
        
        # Redirect to frontend with success
        frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
        redirect_url = f"{frontend_url}/auth/success?provider=canva"
        if username:
            redirect_url += f"&username={username}"
        
        return RedirectResponse(url=redirect_url)
        
    except Exception as e:
        logger.error(f"Canva OAuth callback error: {str(e)}")
        frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
        redirect_url = f"{frontend_url}/auth/error?provider=canva&error={str(e)}"
        
        return RedirectResponse(url=redirect_url)


async def get_current_user(
    security_scopes: SecurityScopes,
    token: str = Depends(oauth2_scheme)
) -> User:
    """
    Get the current user from the JWT token.
    
    Args:
        security_scopes: Security scopes required for the endpoint
        token: JWT token from Authorization header
        
    Returns:
        User object
        
    Raises:
        HTTPException: If the token is invalid or the user doesn't have required scopes
    """
    if security_scopes.scopes:
        authenticate_value = f"Bearer scope=\"{''.join(security_scopes.scopes)}\""
    else:
        authenticate_value = "Bearer"
        
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": authenticate_value},
    )
    
    try:
        # Decode JWT token
        payload = jwt.decode(
            token, 
            settings.SECRET_KEY, 
            algorithms=[settings.ALGORITHM]
        )
        
        # Extract user information
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
            
        # Extract token scopes
        token_scopes = payload.get("scopes", [])
        
        # Create token data
        token_data = TokenData(
            username=username,
            scopes=token_scopes,
            exp=datetime.fromtimestamp(payload.get("exp", 0))
        )
    except JWTError:
        raise credentials_exception
    
    # Check token expiration
    if token_data.exp and token_data.exp < datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired",
            headers={"WWW-Authenticate": authenticate_value},
        )
    
    # Get user from database
    user = get_user(fake_users_db, token_data.username)
    if user is None:
        raise credentials_exception
    
    # Check if user is disabled
    if user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    
    # Check for required scopes
    for scope in security_scopes.scopes:
        if scope not in token_data.scopes:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Not enough permissions. Required: {security_scopes.scopes}",
                headers={"WWW-Authenticate": authenticate_value},
            )
    
    # Return User object (not UserInDB to avoid returning the password hash)
    return User(
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        disabled=user.disabled,
        scopes=user.scopes
    )


async def handle_openai_key_validation(api_key: str) -> Dict:
    """
    Validate OpenAI API key.
    
    Args:
        api_key: OpenAI API key to validate
        
    Returns:
        Dictionary with validation result
    """
    # In a real application, you would validate the API key against the OpenAI API
    # For this placeholder, we'll just check that it's not empty
    if not api_key or len(api_key) < 10:
        return {"valid": False, "message": "Invalid API key format"}
    
    # Placeholder for actual validation
    # Will be implemented with real OpenAI API calls
    return {
        "valid": True,
        "message": "API key validated successfully",
        "key_info": {
            "type": "sk-..." if api_key.startswith("sk-") else "Unknown",
            "last_4": api_key[-4:] if len(api_key) >= 4 else "",
        }
    }
