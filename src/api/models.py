"""
API data models for the Kids Book Generator.

This module defines Pydantic models used for request/response validation,
serialization, and documentation.
"""
from enum import Enum
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field


class BookType(str, Enum):
    """Type of book to generate."""
    STORY = "story"
    COLORING = "coloring"


class TrimSize(str, Enum):
    """Standard KDP trim sizes."""
    STANDARD = "8.5x11"
    SQUARE = "8.5x8.5"


class AgeGroup(str, Enum):
    """Target age groups for books."""
    TODDLER = "0-3"
    PRESCHOOL = "3-5"
    EARLY_READER = "5-7"
    MIDDLE_GRADE = "7-12"


class Character(BaseModel):
    """Character model for book generation."""
    name: str
    description: str
    visual_description: str
    role: str = Field(default="supporting")


class ChapterBase(BaseModel):
    """Base model for a book chapter."""
    title: str
    content: str
    illustration_prompt: Optional[str] = None


class BookMetadata(BaseModel):
    """Metadata for book generation."""
    title: str
    author: str = Field(default="AI Book Generator")
    age_group: AgeGroup
    book_type: BookType
    theme: str
    educational_focus: Optional[str] = None
    trim_size: TrimSize = TrimSize.STANDARD
    page_count: int = Field(default=24, ge=24, le=100)


class StoryGenerationRequest(BaseModel):
    """Request model for story generation."""
    metadata: BookMetadata
    characters: List[Character] = Field(default_factory=list)
    additional_prompts: Optional[str] = None


class ImageGenerationRequest(BaseModel):
    """Request model for image generation."""
    prompt: str
    style: Optional[str] = None
    width: int = Field(default=2550)  # 8.5 inches * 300 DPI
    height: int = Field(default=3300)  # 11 inches * 300 DPI


class BookGenerationResponse(BaseModel):
    """Response model for book generation tasks."""
    id: str
    status: str = "pending"
    created_at: datetime = Field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    download_url: Optional[str] = None
    preview_url: Optional[str] = None


class AuthToken(BaseModel):
    """Authentication token response."""
    access_token: str
    token_type: str = "bearer"
    expires_at: datetime
