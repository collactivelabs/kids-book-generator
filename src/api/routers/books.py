"""
Book management API router for Kids Book Generator.

This module handles book creation, retrieval, updating, and deletion.
"""
import os
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Security, status, Query, File, UploadFile
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from api.auth import User, get_current_user
from api.models import (
    BookMetadata, BookType, TrimSize, AgeGroup, BookGenerationResponse
)
from utils.logging import get_logger


logger = get_logger(__name__)
router = APIRouter(prefix="/books", tags=["books"])


# ---- API Models ----

class BookCreateRequest(BaseModel):
    """Request model for book creation."""
    metadata: BookMetadata
    template_id: Optional[str] = None
    content: Optional[Dict[str, Any]] = None
    canva_design_id: Optional[str] = None


class BookUpdateRequest(BaseModel):
    """Request model for book update."""
    metadata: Optional[BookMetadata] = None
    template_id: Optional[str] = None
    content: Optional[Dict[str, Any]] = None
    canva_design_id: Optional[str] = None
    status: Optional[str] = None


class BookResponse(BaseModel):
    """Response model for book data."""
    id: str
    metadata: BookMetadata
    template_id: Optional[str] = None
    canva_design_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    owner: str
    status: str = "draft"
    preview_url: Optional[str] = None
    download_url: Optional[str] = None


# Mock book database - in a real application, this would be a database
fake_books_db: Dict[str, Dict[str, Any]] = {}


# ---- Book Management Endpoints ----

@router.post("", response_model=BookResponse, status_code=status.HTTP_201_CREATED)
async def create_book(
    book_create: BookCreateRequest,
    current_user: User = Security(
        get_current_user, scopes=["books:write"]
    )
):
    """Create a new book."""
    # Generate a unique ID for the book
    book_id = str(uuid4())
    
    # Create the book record
    now = datetime.utcnow()
    book = {
        "id": book_id,
        "metadata": book_create.metadata.dict(),
        "template_id": book_create.template_id,
        "content": book_create.content or {},
        "canva_design_id": book_create.canva_design_id,
        "created_at": now,
        "updated_at": now,
        "owner": current_user.username,
        "status": "draft",
        "preview_url": None,
        "download_url": None,
    }
    
    # Store in mock database
    fake_books_db[book_id] = book
    
    # Construct response
    return BookResponse(
        id=book_id,
        metadata=book_create.metadata,
        template_id=book_create.template_id,
        canva_design_id=book_create.canva_design_id,
        created_at=now,
        updated_at=now,
        owner=current_user.username,
        status="draft"
    )


@router.get("", response_model=List[BookResponse])
async def list_books(
    status: Optional[str] = None,
    book_type: Optional[BookType] = None,
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Security(
        get_current_user, scopes=["books:read"]
    )
):
    """List books with optional filtering."""
    # Filter books by owner
    user_books = [
        book for book in fake_books_db.values() 
        if book["owner"] == current_user.username
    ]
    
    # Apply status filter if provided
    if status:
        user_books = [book for book in user_books if book["status"] == status]
    
    # Apply book type filter if provided
    if book_type:
        user_books = [
            book for book in user_books 
            if BookType(book["metadata"]["book_type"]) == book_type
        ]
    
    # Apply pagination
    paginated_books = user_books[offset:offset + limit]
    
    # Convert to response model
    result = []
    for book in paginated_books:
        result.append(BookResponse(
            id=book["id"],
            metadata=BookMetadata(**book["metadata"]),
            template_id=book["template_id"],
            canva_design_id=book["canva_design_id"],
            created_at=book["created_at"],
            updated_at=book["updated_at"],
            owner=book["owner"],
            status=book["status"],
            preview_url=book["preview_url"],
            download_url=book["download_url"]
        ))
    
    return result


@router.get("/{book_id}", response_model=BookResponse)
async def get_book(
    book_id: str,
    current_user: User = Security(
        get_current_user, scopes=["books:read"]
    )
):
    """Get a specific book by ID."""
    # Check if book exists
    if book_id not in fake_books_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found"
        )
    
    book = fake_books_db[book_id]
    
    # Check if user is the owner
    if book["owner"] != current_user.username and "admin" not in current_user.scopes:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this book"
        )
    
    # Return book data
    return BookResponse(
        id=book["id"],
        metadata=BookMetadata(**book["metadata"]),
        template_id=book["template_id"],
        canva_design_id=book["canva_design_id"],
        created_at=book["created_at"],
        updated_at=book["updated_at"],
        owner=book["owner"],
        status=book["status"],
        preview_url=book["preview_url"],
        download_url=book["download_url"]
    )


@router.put("/{book_id}", response_model=BookResponse)
async def update_book(
    book_id: str,
    book_update: BookUpdateRequest,
    current_user: User = Security(
        get_current_user, scopes=["books:write"]
    )
):
    """Update a specific book."""
    # Check if book exists
    if book_id not in fake_books_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found"
        )
    
    book = fake_books_db[book_id]
    
    # Check if user is the owner
    if book["owner"] != current_user.username and "admin" not in current_user.scopes:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to modify this book"
        )
    
    # Update book fields
    if book_update.metadata:
        book["metadata"] = book_update.metadata.dict()
    
    if book_update.template_id is not None:
        book["template_id"] = book_update.template_id
    
    if book_update.content is not None:
        book["content"] = book_update.content
    
    if book_update.canva_design_id is not None:
        book["canva_design_id"] = book_update.canva_design_id
    
    if book_update.status is not None:
        book["status"] = book_update.status
    
    # Update the updated_at timestamp
    book["updated_at"] = datetime.utcnow()
    
    # Save updated book
    fake_books_db[book_id] = book
    
    # Return updated book data
    return BookResponse(
        id=book["id"],
        metadata=BookMetadata(**book["metadata"]),
        template_id=book["template_id"],
        canva_design_id=book["canva_design_id"],
        created_at=book["created_at"],
        updated_at=book["updated_at"],
        owner=book["owner"],
        status=book["status"],
        preview_url=book["preview_url"],
        download_url=book["download_url"]
    )


@router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(
    book_id: str,
    current_user: User = Security(
        get_current_user, scopes=["books:write"]
    )
):
    """Delete a specific book."""
    # Check if book exists
    if book_id not in fake_books_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found"
        )
    
    book = fake_books_db[book_id]
    
    # Check if user is the owner
    if book["owner"] != current_user.username and "admin" not in current_user.scopes:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this book"
        )
    
    # Delete the book
    del fake_books_db[book_id]
    
    return None


# ---- Book Generation Endpoints ----

@router.post("/{book_id}/generate", response_model=BookGenerationResponse)
async def generate_book(
    book_id: str,
    current_user: User = Security(
        get_current_user, scopes=["books:write"]
    )
):
    """Generate a book from its metadata and content."""
    # Check if book exists
    if book_id not in fake_books_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found"
        )
    
    book = fake_books_db[book_id]
    
    # Check if user is the owner
    if book["owner"] != current_user.username and "admin" not in current_user.scopes:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to generate this book"
        )
    
    # Check if we have all required fields
    if not book["content"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Book content is required for generation"
        )
    
    # Update book status to "generating"
    book["status"] = "generating"
    book["updated_at"] = datetime.utcnow()
    fake_books_db[book_id] = book
    
    # In a real application, we would start an async task for generation
    # and return its ID for status tracking
    
    # For this mock implementation, we'll simulate a completed generation
    generation_id = f"gen_{uuid4()}"
    
    # Return generation response
    return BookGenerationResponse(
        id=generation_id,
        status="pending",
        created_at=datetime.utcnow()
    )


@router.get("/{book_id}/generate/{generation_id}", response_model=BookGenerationResponse)
async def get_generation_status(
    book_id: str,
    generation_id: str,
    current_user: User = Security(
        get_current_user, scopes=["books:read"]
    )
):
    """Get the status of a book generation task."""
    # Check if book exists
    if book_id not in fake_books_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found"
        )
    
    book = fake_books_db[book_id]
    
    # Check if user is the owner
    if book["owner"] != current_user.username and "admin" not in current_user.scopes:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this book's generation"
        )
    
    # In a real application, we would check the status of the generation task
    # For this mock implementation, we'll simulate a random status
    
    # Simulate completed generation and update book status
    book["status"] = "completed"
    book["preview_url"] = f"/api/v1/books/{book_id}/preview"
    book["download_url"] = f"/api/v1/books/{book_id}/download"
    book["updated_at"] = datetime.utcnow()
    fake_books_db[book_id] = book
    
    return BookGenerationResponse(
        id=generation_id,
        status="completed",
        created_at=datetime.now() - timedelta(minutes=5),
        completed_at=datetime.now(),
        preview_url=book["preview_url"],
        download_url=book["download_url"]
    )


@router.get("/{book_id}/preview")
async def preview_book(
    book_id: str,
    current_user: User = Security(
        get_current_user, scopes=["books:read"]
    )
):
    """Get a preview of a book."""
    # Check if book exists
    if book_id not in fake_books_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found"
        )
    
    book = fake_books_db[book_id]
    
    # Check if user is the owner
    if book["owner"] != current_user.username and "admin" not in current_user.scopes:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to preview this book"
        )
    
    # Check if book has been generated
    if book["status"] not in ["completed", "published"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Book has not been generated yet"
        )
    
    # In a real application, we would return the book preview
    # For this mock implementation, we'll return a placeholder
    return {"message": "Book preview would be shown here"}


@router.get("/{book_id}/download")
async def download_book(
    book_id: str,
    current_user: User = Security(
        get_current_user, scopes=["books:read"]
    )
):
    """Download a book."""
    # Check if book exists
    if book_id not in fake_books_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found"
        )
    
    book = fake_books_db[book_id]
    
    # Check if user is the owner
    if book["owner"] != current_user.username and "admin" not in current_user.scopes:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to download this book"
        )
    
    # Check if book has been generated
    if book["status"] not in ["completed", "published"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Book has not been generated yet"
        )
    
    # In a real application, we would return the book file
    # For this mock implementation, we'll return a placeholder
    return {"message": "Book download would be provided here"}


@router.post("/{book_id}/publish")
async def publish_book(
    book_id: str,
    current_user: User = Security(
        get_current_user, scopes=["books:write"]
    )
):
    """Publish a book."""
    # Check if book exists
    if book_id not in fake_books_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found"
        )
    
    book = fake_books_db[book_id]
    
    # Check if user is the owner
    if book["owner"] != current_user.username and "admin" not in current_user.scopes:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to publish this book"
        )
    
    # Check if book has been generated
    if book["status"] not in ["completed"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Book must be in 'completed' state to publish"
        )
    
    # Update book status to "published"
    book["status"] = "published"
    book["updated_at"] = datetime.utcnow()
    fake_books_db[book_id] = book
    
    # Return updated book data
    return BookResponse(
        id=book["id"],
        metadata=BookMetadata(**book["metadata"]),
        template_id=book["template_id"],
        canva_design_id=book["canva_design_id"],
        created_at=book["created_at"],
        updated_at=book["updated_at"],
        owner=book["owner"],
        status=book["status"],
        preview_url=book["preview_url"],
        download_url=book["download_url"]
    )
