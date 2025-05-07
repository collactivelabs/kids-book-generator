"""
API routes for the Kids Book Generator.

This module defines the FastAPI routers for all endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, status

# Initialize routers
book_router = APIRouter()
generation_router = APIRouter()
template_router = APIRouter()
auth_router = APIRouter()

# Import routers
from api.routers.canva import router as canva_router
from api.routers.users import router as users_router
from api.routers.books import router as books_router
from api.routers.batch import router as batch_router

# Book endpoints
@book_router.get("/books")
async def get_books():
    """Get all books."""
    return {"message": "List of books will be returned here"}

@book_router.get("/books/{book_id}")
async def get_book(book_id: str):
    """Get a specific book by ID."""
    return {"message": f"Book with ID {book_id} will be returned here"}

@book_router.post("/books")
async def create_book():
    """Create a new book."""
    return {"message": "New book creation endpoint"}

# Generation endpoints
@generation_router.post("/generate/story")
async def generate_story():
    """Generate a new story."""
    return {"message": "Story generation endpoint"}

@generation_router.post("/generate/image")
async def generate_image():
    """Generate a new image."""
    return {"message": "Image generation endpoint"}

@generation_router.post("/generate/book")
async def generate_book():
    """Generate a complete book."""
    return {"message": "Book generation endpoint"}

# Template endpoints
@template_router.get("/templates")
async def get_templates():
    """Get all templates."""
    return {"message": "List of templates will be returned here"}

@template_router.get("/templates/{template_id}")
async def get_template(template_id: str):
    """Get a specific template by ID."""
    return {"message": f"Template with ID {template_id} will be returned here"}

# Authentication endpoints
from fastapi import Depends
from fastapi.security import OAuth2PasswordRequestForm
from api.auth import (
    handle_token_generation,
    handle_canva_authorize,
    handle_canva_callback,
    handle_openai_key_validation
)

@auth_router.post("/auth/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """Login endpoint to obtain JWT token."""
    return await handle_token_generation(form_data)

@auth_router.get("/auth/canva/authorize")
async def canva_authorize():
    """Redirect to Canva OAuth authorization."""
    return await handle_canva_authorize()

@auth_router.get("/auth/canva/callback")
async def canva_callback(code: str, state: str = None):
    """Callback endpoint for Canva OAuth."""
    return await handle_canva_callback(code, state)
    
@auth_router.post("/auth/openai/validate")
async def validate_openai_key(api_key: str):
    """Validate an OpenAI API key."""
    return await handle_openai_key_validation(api_key)

# Note: We're exporting the Canva router directly rather than adding endpoints
# to the existing auth_router, as it's a comprehensive module with many endpoints
