"""
Authentication controllers for the Kids Book Generator.

This module handles authentication endpoints, including OAuth flows
and API key management.
"""
import os
import logging
from typing import Dict, Optional
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from src.config import settings
from src.utils.auth import create_access_token, get_current_user, CanvaAuth

logger = logging.getLogger(__name__)


async def handle_token_generation(form_data: OAuth2PasswordRequestForm = Depends()) -> Dict:
    """
    Handle user authentication and token generation.
    
    Args:
        form_data: OAuth2 password request form
        
    Returns:
        Dictionary with access token
        
    Raises:
        HTTPException: If authentication fails
    """
    # In a real application, you would validate username/password against a database
    # For this placeholder, we'll accept a simple admin/admin combination
    if form_data.username != "admin" or form_data.password != "admin":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token with 30 minute expiration
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": form_data.username},
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_at": (datetime.utcnow() + access_token_expires).isoformat()
    }


async def handle_canva_authorize() -> Dict:
    """
    Generate Canva OAuth authorization URL.
    
    Returns:
        Dictionary with authorization URL
    """
    try:
        oauth_url = CanvaAuth.get_oauth_url()
        return {"authorization_url": oauth_url}
    except ValueError as e:
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
        state: Optional state parameter
        
    Returns:
        Redirect response to frontend
    """
    try:
        # Exchange code for token
        token_info = await CanvaAuth.exchange_code_for_token(code)
        
        # In a real application, you would store this token in a database
        # For now, we'll just redirect to a success page
        frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
        redirect_url = f"{frontend_url}/auth/success?provider=canva"
        
        return RedirectResponse(url=redirect_url)
    except Exception as e:
        logger.error(f"Canva OAuth callback error: {str(e)}")
        frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
        redirect_url = f"{frontend_url}/auth/error?provider=canva&error={str(e)}"
        
        return RedirectResponse(url=redirect_url)


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
