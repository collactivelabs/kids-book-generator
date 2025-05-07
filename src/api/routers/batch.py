"""
Batch processing API router for Kids Book Generator.

This module handles batch operations for book generation, including
job queue management, parallel processing, and status tracking.
"""
import os
import asyncio
from typing import List, Dict, Optional, Any
from datetime import datetime
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Security, status, BackgroundTasks
from pydantic import BaseModel, Field, validator

from src.api.auth import User, get_current_user
from src.api.models import BookMetadata, BookType, AgeGroup, TrimSize
from src.utils.logging import get_logger


logger = get_logger(__name__)
router = APIRouter(prefix="/batch", tags=["batch"])


# ---- API Models ----

class BatchJobStatus(str):
    """Batch job status enumeration."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class BatchBookRequest(BaseModel):
    """Request model for a single book in a batch."""
    metadata: BookMetadata
    template_id: Optional[str] = None
    content: Optional[Dict[str, Any]] = None
    canva_design_id: Optional[str] = None


class BatchJobRequest(BaseModel):
    """Request model for a batch processing job."""
    name: str = Field(..., description="Batch job name")
    description: Optional[str] = None
    books: List[BatchBookRequest]
    
    @validator("books")
    def validate_books(cls, books):
        """Validate that the batch contains at least one book."""
        if not books:
            raise ValueError("Batch must contain at least one book")
        if len(books) > 50:
            raise ValueError("Batch can contain at most 50 books")
        return books


class BatchBookResult(BaseModel):
    """Result model for a single book in a batch."""
    id: Optional[str] = None
    metadata: BookMetadata
    status: str = "pending"
    error: Optional[str] = None
    preview_url: Optional[str] = None
    download_url: Optional[str] = None


class BatchJobResponse(BaseModel):
    """Response model for a batch processing job."""
    id: str
    name: str
    description: Optional[str] = None
    status: str
    owner: str
    created_at: datetime
    updated_at: datetime
    total_books: int
    completed_books: int
    failed_books: int
    results: Optional[List[BatchBookResult]] = None


# Mock batch job database
fake_batch_jobs: Dict[str, Dict[str, Any]] = {}


# ---- Batch Processing Endpoints ----

@router.post("", response_model=BatchJobResponse, status_code=status.HTTP_201_CREATED)
async def create_batch_job(
    batch_job: BatchJobRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Security(
        get_current_user, scopes=["books:write"]
    )
):
    """Create a new batch processing job."""
    # Generate a unique ID for the batch job
    job_id = str(uuid4())
    
    # Initialize book results
    book_results = []
    for book_request in batch_job.books:
        book_results.append(BatchBookResult(
            metadata=book_request.metadata,
            status="pending"
        ))
    
    # Create batch job record
    now = datetime.utcnow()
    job = {
        "id": job_id,
        "name": batch_job.name,
        "description": batch_job.description,
        "status": BatchJobStatus.PENDING,
        "owner": current_user.username,
        "created_at": now,
        "updated_at": now,
        "total_books": len(batch_job.books),
        "completed_books": 0,
        "failed_books": 0,
        "books": [book.dict() for book in batch_job.books],
        "results": [result.dict() for result in book_results]
    }
    
    # Store in mock database
    fake_batch_jobs[job_id] = job
    
    # Start background processing
    background_tasks.add_task(process_batch_job, job_id)
    
    # Return response
    return BatchJobResponse(
        id=job_id,
        name=batch_job.name,
        description=batch_job.description,
        status=BatchJobStatus.PENDING,
        owner=current_user.username,
        created_at=now,
        updated_at=now,
        total_books=len(batch_job.books),
        completed_books=0,
        failed_books=0,
        results=book_results
    )


@router.get("", response_model=List[BatchJobResponse])
async def list_batch_jobs(
    status: Optional[str] = None,
    current_user: User = Security(
        get_current_user, scopes=["books:read"]
    )
):
    """List batch jobs."""
    # Filter jobs by owner
    user_jobs = [
        job for job in fake_batch_jobs.values() 
        if job["owner"] == current_user.username
    ]
    
    # Apply status filter if provided
    if status:
        user_jobs = [job for job in user_jobs if job["status"] == status]
    
    # Convert to response model
    result = []
    for job in user_jobs:
        # Convert book results
        book_results = []
        if job.get("results"):
            for result_dict in job["results"]:
                book_results.append(BatchBookResult(**result_dict))
        
        result.append(BatchJobResponse(
            id=job["id"],
            name=job["name"],
            description=job["description"],
            status=job["status"],
            owner=job["owner"],
            created_at=job["created_at"],
            updated_at=job["updated_at"],
            total_books=job["total_books"],
            completed_books=job["completed_books"],
            failed_books=job["failed_books"],
            results=book_results
        ))
    
    return result


@router.get("/{job_id}", response_model=BatchJobResponse)
async def get_batch_job(
    job_id: str,
    current_user: User = Security(
        get_current_user, scopes=["books:read"]
    )
):
    """Get a specific batch job by ID."""
    # Check if job exists
    if job_id not in fake_batch_jobs:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Batch job not found"
        )
    
    job = fake_batch_jobs[job_id]
    
    # Check if user is the owner
    if job["owner"] != current_user.username and "admin" not in current_user.scopes:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this batch job"
        )
    
    # Convert book results
    book_results = []
    if job.get("results"):
        for result_dict in job["results"]:
            book_results.append(BatchBookResult(**result_dict))
    
    # Return job data
    return BatchJobResponse(
        id=job["id"],
        name=job["name"],
        description=job["description"],
        status=job["status"],
        owner=job["owner"],
        created_at=job["created_at"],
        updated_at=job["updated_at"],
        total_books=job["total_books"],
        completed_books=job["completed_books"],
        failed_books=job["failed_books"],
        results=book_results
    )


@router.post("/{job_id}/cancel", response_model=BatchJobResponse)
async def cancel_batch_job(
    job_id: str,
    current_user: User = Security(
        get_current_user, scopes=["books:write"]
    )
):
    """Cancel a batch job."""
    # Check if job exists
    if job_id not in fake_batch_jobs:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Batch job not found"
        )
    
    job = fake_batch_jobs[job_id]
    
    # Check if user is the owner
    if job["owner"] != current_user.username and "admin" not in current_user.scopes:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to cancel this batch job"
        )
    
    # Check if job can be cancelled
    if job["status"] not in [BatchJobStatus.PENDING, BatchJobStatus.PROCESSING]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot cancel batch job in {job['status']} status"
        )
    
    # Update job status
    job["status"] = BatchJobStatus.CANCELLED
    job["updated_at"] = datetime.utcnow()
    fake_batch_jobs[job_id] = job
    
    # Convert book results
    book_results = []
    if job.get("results"):
        for result_dict in job["results"]:
            book_results.append(BatchBookResult(**result_dict))
    
    # Return updated job data
    return BatchJobResponse(
        id=job["id"],
        name=job["name"],
        description=job["description"],
        status=job["status"],
        owner=job["owner"],
        created_at=job["created_at"],
        updated_at=job["updated_at"],
        total_books=job["total_books"],
        completed_books=job["completed_books"],
        failed_books=job["failed_books"],
        results=book_results
    )


# ---- Batch Processing Functions ----

async def process_batch_job(job_id: str):
    """
    Process a batch job in the background.
    
    Args:
        job_id: Batch job ID
    """
    # Check if job exists
    if job_id not in fake_batch_jobs:
        logger.error(f"Batch job {job_id} not found")
        return
    
    job = fake_batch_jobs[job_id]
    
    # Update job status to processing
    job["status"] = BatchJobStatus.PROCESSING
    job["updated_at"] = datetime.utcnow()
    fake_batch_jobs[job_id] = job
    
    # Process books in parallel
    try:
        # In a real application, we would use a task queue like Celery
        # For this mock implementation, we'll use asyncio
        
        # Simulate processing each book
        for i, book_request in enumerate(job["books"]):
            # Skip if job has been cancelled
            if fake_batch_jobs[job_id]["status"] == BatchJobStatus.CANCELLED:
                break
            
            # Simulate async processing
            await asyncio.sleep(2)  # Simulate processing time
            
            # Generate a unique ID for the book
            book_id = str(uuid4())
            
            # Update book result with success
            job["results"][i]["id"] = book_id
            job["results"][i]["status"] = "completed"
            job["results"][i]["preview_url"] = f"/api/v1/books/{book_id}/preview"
            job["results"][i]["download_url"] = f"/api/v1/books/{book_id}/download"
            
            # Update job counters
            job["completed_books"] += 1
            
            # Update job
            job["updated_at"] = datetime.utcnow()
            fake_batch_jobs[job_id] = job
        
        # Update job status to completed if not cancelled
        if job["status"] != BatchJobStatus.CANCELLED:
            job["status"] = BatchJobStatus.COMPLETED
            job["updated_at"] = datetime.utcnow()
            fake_batch_jobs[job_id] = job
    
    except Exception as e:
        logger.error(f"Error processing batch job {job_id}: {str(e)}")
        
        # Update job status to failed
        job["status"] = BatchJobStatus.FAILED
        job["updated_at"] = datetime.utcnow()
        fake_batch_jobs[job_id] = job
