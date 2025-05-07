"""
Configuration settings for the Kids Book Generator application.

This module handles configuration management, environment variables,
and provides a central place for all application settings.
"""
import os
from typing import Dict, List, Optional, Any
# In Pydantic 2.x, BaseSettings has moved to pydantic-settings
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator, Field

class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    """
    # API Settings
    APP_NAME: str = "Kids Book Generator"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = Field(default=False)
    
    # Server Settings
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # Database Settings
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/kids_book_generator"
    
    # Redis Settings
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # OpenAI API Settings
    OPENAI_API_KEY: str = Field(default="")
    
    # Canva API Settings
    CANVA_CLIENT_ID: str = Field(default="")
    CANVA_CLIENT_SECRET: str = Field(default="")
    CANVA_REDIRECT_URI: str = Field(default="http://localhost:8000/api/v1/auth/canva/callback")
    
    # Book Generation Settings
    STORY_BOOK_MIN_PAGES: int = 24
    STORY_BOOK_MAX_PAGES: int = 100
    COLORING_BOOK_MIN_PAGES: int = 24
    COLORING_BOOK_MAX_PAGES: int = 150
    
    # Image Generation Settings
    IMAGE_QUALITY: int = 300  # DPI
    DEFAULT_IMAGE_WIDTH: int = 2550  # 8.5 inches * 300 DPI
    DEFAULT_IMAGE_HEIGHT: int = 3300  # 11 inches * 300 DPI
    
    # Security Settings
    SECRET_KEY: str = Field(default="")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS Settings
    CORS_ORIGINS: List[str] = ["*"]
    
    # File Storage Settings
    STORAGE_DIR: str = "output"
    
    # Optional Canva API key (may be in .env file)
    CANVA_API_KEY: Optional[str] = None
    
    # Optional environment setting
    ENV: Optional[str] = "development"
    
    @field_validator("SECRET_KEY")
    @classmethod
    def validate_secret_key(cls, v: str) -> str:
        """Ensure SECRET_KEY is set for production."""
        if not v and os.getenv("DEBUG", "").lower() != "true":
            raise ValueError("SECRET_KEY is required in production")
        return v
    
    @field_validator("OPENAI_API_KEY")
    @classmethod
    def validate_openai_api_key(cls, v: str) -> str:
        """Ensure OPENAI_API_KEY is set."""
        if not v:
            raise ValueError("OPENAI_API_KEY is required")
        return v
    
    # Use new SettingsConfigDict instead of nested Config class
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"  # Allow extra fields in the settings
    )


# Create global settings object
settings = Settings()

# Export settings as dictionary for easier access in other modules
settings_dict: Dict[str, Any] = settings.dict()
