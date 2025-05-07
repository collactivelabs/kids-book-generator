"""
User management API router for Kids Book Generator.

This module handles user registration, profile management, and user-specific operations.
"""
import os
from typing import List, Optional
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Security, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, Field, EmailStr

from src.api.auth import (
    User, Token, handle_token_generation, get_current_user,
    handle_canva_authorize, handle_canva_callback, fake_users_db
)
from src.utils.logging import get_logger
from src.utils.auth import get_password_hash


logger = get_logger(__name__)
router = APIRouter(prefix="/users", tags=["users"])


# ---- API Models ----

class UserCreate(BaseModel):
    """Request model for user registration."""
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    full_name: Optional[str] = None
    password: str = Field(..., min_length=8)


class UserUpdate(BaseModel):
    """Request model for user profile update."""
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    password: Optional[str] = Field(None, min_length=8)


class UserResponse(BaseModel):
    """Response model for user data."""
    username: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    created_at: Optional[datetime] = None
    last_login: Optional[datetime] = None


# ---- Authentication Endpoints ----

@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """Login endpoint to get access token."""
    return await handle_token_generation(form_data)


@router.get("/me", response_model=UserResponse)
async def read_users_me(
    current_user: User = Security(
        get_current_user, scopes=["users:read"]
    )
):
    """Get current user profile."""
    return {
        "username": current_user.username,
        "email": current_user.email,
        "full_name": current_user.full_name,
        # In a real app, these would come from the database
        "created_at": datetime.utcnow(),
        "last_login": datetime.utcnow(),
    }


@router.put("/me", response_model=UserResponse)
async def update_user_me(
    user_update: UserUpdate,
    current_user: User = Security(
        get_current_user, scopes=["users:write"]
    )
):
    """Update current user profile."""
    # In a real app, this would update the database
    # For this demo, we'll just return the updated user
    
    # Mock updating the user in our fake database
    if current_user.username in fake_users_db:
        user_data = fake_users_db[current_user.username]
        
        if user_update.email:
            user_data["email"] = user_update.email
        
        if user_update.full_name:
            user_data["full_name"] = user_update.full_name
        
        if user_update.password:
            user_data["hashed_password"] = get_password_hash(user_update.password)
    
    return {
        "username": current_user.username,
        "email": user_update.email or current_user.email,
        "full_name": user_update.full_name or current_user.full_name,
        "created_at": datetime.utcnow(),
        "last_login": datetime.utcnow(),
    }


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(user_create: UserCreate):
    """Register a new user."""
    # Check if username already exists
    if user_create.username in fake_users_db:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    # In a real app, this would create a user in the database
    # For this demo, we'll add the user to our fake database
    fake_users_db[user_create.username] = {
        "username": user_create.username,
        "email": user_create.email,
        "full_name": user_create.full_name,
        "hashed_password": get_password_hash(user_create.password),
        "disabled": False,
        "scopes": ["books:read", "books:write"],  # Default scopes for new users
    }
    
    return {
        "username": user_create.username,
        "email": user_create.email,
        "full_name": user_create.full_name,
        "created_at": datetime.utcnow(),
        "last_login": None,
    }


# ---- External Auth Endpoints ----

@router.get("/auth/canva")
async def canva_auth(
    current_user: User = Security(
        get_current_user, scopes=["users:write"]
    )
):
    """Get Canva OAuth authorization URL."""
    return await handle_canva_authorize(username=current_user.username)


@router.get("/canva-callback")
async def canva_auth_callback(code: str, state: Optional[str] = None):
    """Handle Canva OAuth callback."""
    return await handle_canva_callback(code, state)


# ---- Admin Endpoints ----

@router.get(
    "", 
    response_model=List[UserResponse],
    dependencies=[Security(get_current_user, scopes=["admin"])]
)
async def list_users():
    """List all users (admin only)."""
    # In a real app, this would query the database
    users = []
    for username, user_data in fake_users_db.items():
        users.append({
            "username": username,
            "email": user_data.get("email"),
            "full_name": user_data.get("full_name"),
            "created_at": datetime.utcnow(),  # Placeholder
            "last_login": None,
        })
    return users


@router.get(
    "/{username}", 
    response_model=UserResponse,
    dependencies=[Security(get_current_user, scopes=["admin"])]
)
async def get_user_by_username(username: str):
    """Get user by username (admin only)."""
    # Check if user exists
    if username not in fake_users_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    user_data = fake_users_db[username]
    return {
        "username": username,
        "email": user_data.get("email"),
        "full_name": user_data.get("full_name"),
        "created_at": datetime.utcnow(),  # Placeholder
        "last_login": None,
    }


@router.delete(
    "/{username}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Security(get_current_user, scopes=["admin"])]
)
async def delete_user(username: str):
    """Delete user (admin only)."""
    # Check if user exists
    if username not in fake_users_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # In a real app, this would delete the user from the database
    # For this demo, we'll remove the user from our fake database
    del fake_users_db[username]
    return None
