"""
Main application entry point for the Kids Book Generator.

This module initializes the FastAPI application and sets up all routes,
middleware, and dependencies.
"""
import os
from pathlib import Path
from typing import List, Dict, Any, Optional

# Import development settings before other modules
import dev_settings

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="Kids Book Generator",
    description="An AI-powered generator for children's books and coloring books",
    version="0.1.0",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint to verify API is running."""
    return {"status": "healthy", "version": app.version}

# Mount static files directory if it exists
static_dir = Path(__file__).parent.parent / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

# Include API routers
from api.routes import (
    book_router, generation_router, template_router, auth_router, 
    canva_router, users_router, books_router, batch_router
)

# Legacy routers (simple placeholders)
app.include_router(book_router, prefix="/api/v1/legacy", tags=["legacy"])
app.include_router(generation_router, prefix="/api/v1/legacy", tags=["legacy"])
app.include_router(template_router, prefix="/api/v1/legacy", tags=["legacy"])
app.include_router(auth_router, prefix="/api/v1", tags=["auth"])

# New fully implemented routers
app.include_router(canva_router, prefix="/api/v1", tags=["canva"])
app.include_router(users_router, prefix="/api/v1", tags=["users"])
app.include_router(books_router, prefix="/api/v1", tags=["books"])
app.include_router(batch_router, prefix="/api/v1", tags=["batch"])

# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Custom HTTP exception handler."""
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail, "status_code": exc.status_code},
    )

if __name__ == "__main__":
    """
    For development only. In production, use:
    uvicorn src.main:app --host 0.0.0.0 --port 8000
    """
    import uvicorn
    uvicorn.run("src.main:app", host="0.0.0.0", port=8000, reload=True)
