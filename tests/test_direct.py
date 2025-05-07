"""
Direct testing script for the books router.

This script creates a minimal FastAPI application to test the books router
without the complexity of the full application.
"""
import sys
import os
import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

# Add the src directory to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Import the books router
from src.api.routers.books import router as books_router

# Create a minimal FastAPI application
app = FastAPI(
    title="Books API Test",
    description="Minimal FastAPI application to test the books router",
    version="1.0.0",
)

# Add the books router
app.include_router(books_router, prefix="/api/v1/books", tags=["books"])

# Add a middleware to log requests and responses
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all requests and responses."""
    print(f"Request: {request.method} {request.url}")
    print(f"Headers: {request.headers}")
    
    # Process the request
    response = await call_next(request)
    
    # Print status code
    print(f"Response status: {response.status_code}")
    
    return response

# Add a simple root endpoint
@app.get("/")
async def root():
    """Root endpoint for testing."""
    return {"message": "Books API Test"}

# Add an exception handler
@app.exception_handler(Exception)
async def exception_handler(request: Request, exc: Exception):
    """Handle all exceptions."""
    print(f"Exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": str(exc)},
    )

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
