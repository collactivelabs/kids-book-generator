"""
Canva integration API router for Kids Book Generator.

This module handles API endpoints for Canva Connect integration,
including authentication, template management, design export, and previews.
"""
import os
from typing import Dict, List, Optional, Any
from datetime import datetime
from urllib.parse import urlencode

from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks, Request
from fastapi.responses import JSONResponse, RedirectResponse, FileResponse
from pydantic import BaseModel, Field

from config import settings
from api.models import BookMetadata, BookType, TrimSize
from api.auth import get_current_user
from utils.logging import get_logger
from integrations.canva import (
    canva_client, CanvaDesign, CanvaDesignRequest, CanvaExportRequest, CanvaAsset
)
from integrations.canva_templates import (
    canva_template_manager, CanvaTemplate
)
from integrations.canva_export import (
    canva_export_manager, ExportStatus
)
from integrations.canva_preview import (
    canva_preview_manager, PreviewOptions, PreviewResult
)


logger = get_logger(__name__)
router = APIRouter(prefix="/canva", tags=["canva"])


# ---- Models for API requests and responses ----

class CanvaAuthResponse(BaseModel):
    """Response model for Canva authentication."""
    auth_url: str = Field(..., description="Canva authorization URL")
    state: str = Field(..., description="State parameter for CSRF protection")


class CanvaTokenRequest(BaseModel):
    """Request model for exchanging authorization code for token."""
    code: str = Field(..., description="Authorization code from Canva")
    state: Optional[str] = Field(None, description="State parameter from authorization")


class CanvaTokenResponse(BaseModel):
    """Response model for Canva access token."""
    access_token: str = Field(..., description="OAuth access token")
    refresh_token: str = Field(..., description="OAuth refresh token")
    expires_in: int = Field(..., description="Token expiration time in seconds")
    token_type: str = Field(..., description="Token type (usually 'Bearer')")
    scope: str = Field(..., description="Granted permission scopes")


class CanvaTemplateRequest(BaseModel):
    """Request model for creating a template."""
    name: str = Field(..., description="Template name")
    description: str = Field(..., description="Template description")
    book_type: BookType = Field(..., description="Book type")
    trim_size: TrimSize = Field(..., description="Trim size")
    age_groups: List[str] = Field(..., description="Compatible age groups")
    canva_id: Optional[str] = Field(None, description="Canva design ID")
    properties: Optional[Dict[str, Any]] = Field(None, description="Template properties")
    tags: Optional[List[str]] = Field(None, description="Template tags")


class CanvaTemplateUpdateRequest(BaseModel):
    """Request model for updating a template."""
    name: Optional[str] = Field(None, description="Template name")
    description: Optional[str] = Field(None, description="Template description")
    canva_id: Optional[str] = Field(None, description="Canva design ID")
    properties: Optional[Dict[str, Any]] = Field(None, description="Template properties")
    tags: Optional[List[str]] = Field(None, description="Template tags")


class CanvaExportRequest(BaseModel):
    """Request model for exporting a design."""
    design_id: str = Field(..., description="Canva design ID")
    export_type: str = Field("pdf", description="Export type (pdf, png, jpg)")
    pdf_options: Optional[Dict[str, Any]] = Field(None, description="PDF export options")


class CanvaPreviewRequest(BaseModel):
    """Request model for generating a preview."""
    design_id: str = Field(..., description="Canva design ID")
    width: Optional[int] = Field(None, description="Preview width in pixels")
    height: Optional[int] = Field(None, description="Preview height in pixels")
    format: str = Field("png", description="Image format (png, jpg, webp)")
    quality: int = Field(90, description="Image quality (1-100)")
    page_number: Optional[int] = Field(None, description="Page number to preview")
    include_bleed: bool = Field(False, description="Include bleed area in preview")
    include_spine: bool = Field(False, description="Include spine in cover preview")
    show_grid: bool = Field(False, description="Show grid overlay")


# ---- Authentication endpoints ----

@router.get("/auth", response_model=CanvaAuthResponse)
async def get_canva_auth_url():
    """
    Get Canva authorization URL.
    
    Returns:
        Authorization URL and state parameter
    """
    state = os.urandom(16).hex()
    auth_url = canva_client.get_authorization_url(state=state)
    
    return {
        "auth_url": auth_url,
        "state": state
    }


@router.post("/token", response_model=CanvaTokenResponse)
async def exchange_token(request: CanvaTokenRequest):
    """
    Exchange authorization code for access token.
    
    Args:
        request: Token request with authorization code
        
    Returns:
        Access token response
    """
    try:
        token_response = await canva_client.exchange_code_for_token(request.code)
        
        return {
            "access_token": token_response["access_token"],
            "refresh_token": token_response["refresh_token"],
            "expires_in": token_response["expires_in"],
            "token_type": token_response["token_type"],
            "scope": token_response["scope"]
        }
    
    except Exception as e:
        logger.error(f"Failed to exchange token: {str(e)}")
        raise HTTPException(
            status_code=400,
            detail=f"Failed to exchange token: {str(e)}"
        )


@router.post("/refresh", response_model=CanvaTokenResponse)
async def refresh_token(refresh_token: str):
    """
    Refresh access token.
    
    Args:
        refresh_token: OAuth refresh token
        
    Returns:
        New access token response
    """
    try:
        token_response = await canva_client.refresh_access_token(refresh_token)
        
        return {
            "access_token": token_response["access_token"],
            "refresh_token": token_response["refresh_token"],
            "expires_in": token_response["expires_in"],
            "token_type": token_response["token_type"],
            "scope": token_response["scope"]
        }
    
    except Exception as e:
        logger.error(f"Failed to refresh token: {str(e)}")
        raise HTTPException(
            status_code=400,
            detail=f"Failed to refresh token: {str(e)}"
        )


# ---- Template management endpoints ----

@router.get("/templates", response_model=List[CanvaTemplate])
async def get_templates(
    book_type: Optional[BookType] = None,
    trim_size: Optional[TrimSize] = None,
    age_group: Optional[str] = None,
    tags: Optional[List[str]] = Query(None)
):
    """
    Get templates matching the specified criteria.
    
    Args:
        book_type: Book type filter
        trim_size: Trim size filter
        age_group: Age group filter
        tags: Tags filter
        
    Returns:
        List of matching templates
    """
    return canva_template_manager.get_templates(
        book_type=book_type,
        trim_size=trim_size,
        age_group=age_group,
        tags=tags
    )


@router.get("/templates/{template_id}", response_model=CanvaTemplate)
async def get_template(template_id: str):
    """
    Get a template by ID.
    
    Args:
        template_id: Template ID
        
    Returns:
        Template details
    """
    template = canva_template_manager.get_template(template_id)
    if not template:
        raise HTTPException(
            status_code=404,
            detail=f"Template {template_id} not found"
        )
    
    return template


@router.post("/templates", response_model=CanvaTemplate)
async def create_template(request: CanvaTemplateRequest):
    """
    Create a new template.
    
    Args:
        request: Template creation request
        
    Returns:
        Created template
    """
    return canva_template_manager.create_template(
        name=request.name,
        description=request.description,
        book_type=request.book_type,
        trim_size=request.trim_size,
        age_groups=request.age_groups,
        canva_id=request.canva_id,
        properties=request.properties,
        tags=request.tags
    )


@router.put("/templates/{template_id}", response_model=CanvaTemplate)
async def update_template(template_id: str, request: CanvaTemplateUpdateRequest):
    """
    Update an existing template.
    
    Args:
        template_id: Template ID
        request: Template update request
        
    Returns:
        Updated template
    """
    template = canva_template_manager.update_template(
        template_id=template_id,
        name=request.name,
        description=request.description,
        canva_id=request.canva_id,
        properties=request.properties,
        tags=request.tags
    )
    
    if not template:
        raise HTTPException(
            status_code=404,
            detail=f"Template {template_id} not found"
        )
    
    return template


@router.delete("/templates/{template_id}")
async def delete_template(template_id: str):
    """
    Delete a template.
    
    Args:
        template_id: Template ID
        
    Returns:
        Success message
    """
    success = canva_template_manager.delete_template(template_id)
    
    if not success:
        raise HTTPException(
            status_code=404,
            detail=f"Template {template_id} not found"
        )
    
    return {"message": f"Template {template_id} deleted"}


@router.get("/templates/default", response_model=CanvaTemplate)
async def get_default_template(book_type: BookType, trim_size: TrimSize):
    """
    Get the default template for a book type and trim size.
    
    Args:
        book_type: Book type
        trim_size: Trim size
        
    Returns:
        Default template
    """
    template = canva_template_manager.get_default_template(
        book_type=book_type,
        trim_size=trim_size
    )
    
    if not template:
        raise HTTPException(
            status_code=404,
            detail=f"No default template found for {book_type.value} {trim_size.value}"
        )
    
    return template


@router.post("/templates/import", response_model=CanvaTemplate)
async def import_template_from_canva(
    access_token: str,
    canva_design_id: str,
    request: CanvaTemplateRequest
):
    """
    Import a template from Canva.
    
    Args:
        access_token: Canva API access token
        canva_design_id: Canva design ID
        request: Template creation request
        
    Returns:
        Imported template
    """
    template = await canva_template_manager.import_template_from_canva(
        access_token=access_token,
        canva_design_id=canva_design_id,
        name=request.name,
        description=request.description,
        book_type=request.book_type,
        trim_size=request.trim_size,
        age_groups=request.age_groups,
        tags=request.tags
    )
    
    if not template:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to import template from Canva"
        )
    
    return template


# ---- Design management endpoints ----

@router.get("/designs", response_model=Dict[str, Any])
async def get_user_designs(
    access_token: str,
    page_size: int = 20,
    cursor: Optional[str] = None
):
    """
    Get user's designs from Canva.
    
    Args:
        access_token: Canva API access token
        page_size: Number of results per page
        cursor: Pagination cursor
        
    Returns:
        List of designs
    """
    return await canva_client.get_user_designs(
        access_token=access_token,
        page_size=page_size,
        cursor=cursor
    )


@router.get("/designs/{design_id}", response_model=Dict[str, Any])
async def get_design(access_token: str, design_id: str):
    """
    Get design information from Canva.
    
    Args:
        access_token: Canva API access token
        design_id: Canva design ID
        
    Returns:
        Design information
    """
    return await canva_client.get_design(
        access_token=access_token,
        design_id=design_id
    )


@router.post("/designs", response_model=Dict[str, Any])
async def create_design(access_token: str, request: CanvaDesignRequest):
    """
    Create a new design in Canva.
    
    Args:
        access_token: Canva API access token
        request: Design creation request
        
    Returns:
        Created design information
    """
    return await canva_client.create_design(
        access_token=access_token,
        design_request=request
    )


@router.post("/designs/from-metadata", response_model=Dict[str, Any])
async def create_design_from_metadata(access_token: str, metadata: BookMetadata):
    """
    Create a design based on book metadata.
    
    Args:
        access_token: Canva API access token
        metadata: Book metadata
        
    Returns:
        Created design information
    """
    return await canva_client.create_design_from_book_metadata(
        access_token=access_token,
        metadata=metadata
    )


@router.patch("/designs/{design_id}", response_model=Dict[str, Any])
async def update_design(
    access_token: str,
    design_id: str,
    title: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None
):
    """
    Update an existing design in Canva.
    
    Args:
        access_token: Canva API access token
        design_id: Canva design ID
        title: New design title
        metadata: Updated metadata
        
    Returns:
        Updated design information
    """
    return await canva_client.update_design(
        access_token=access_token,
        design_id=design_id,
        title=title,
        metadata=metadata
    )


# ---- Export endpoints ----

@router.post("/exports", response_model=str)
async def export_design(access_token: str, request: CanvaExportRequest):
    """
    Start exporting a design from Canva.
    
    Args:
        access_token: Canva API access token
        request: Export request
        
    Returns:
        Export ID for tracking status
    """
    return await canva_export_manager.export_design(
        access_token=access_token,
        design_id=request.design_id,
        export_type=request.export_type,
        pdf_options=request.pdf_options
    )


@router.get("/exports/{export_id}", response_model=ExportStatus)
async def get_export_status(export_id: str):
    """
    Get the status of an export.
    
    Args:
        export_id: Export ID
        
    Returns:
        Export status
    """
    status = await canva_export_manager.get_export_status(export_id)
    
    if not status:
        raise HTTPException(
            status_code=404,
            detail=f"Export {export_id} not found"
        )
    
    return status


@router.get("/exports/{export_id}/download")
async def download_export(export_id: str):
    """
    Download an exported file.
    
    Args:
        export_id: Export ID
        
    Returns:
        Exported file
    """
    status = await canva_export_manager.get_export_status(export_id)
    
    if not status:
        raise HTTPException(
            status_code=404,
            detail=f"Export {export_id} not found"
        )
    
    if status.status != "completed":
        raise HTTPException(
            status_code=400,
            detail=f"Export {export_id} is not complete: {status.status}"
        )
    
    if not status.local_path:
        raise HTTPException(
            status_code=500,
            detail=f"Export {export_id} has no local file"
        )
    
    return FileResponse(
        path=status.local_path,
        filename=f"export_{export_id}.{status.export_type}",
        media_type=f"application/{status.export_type}"
    )


@router.post("/exports/{export_id}/extract-images", response_model=List[str])
async def extract_images_from_export(
    export_id: str,
    name_prefix: str = "image",
    min_size: int = 100
):
    """
    Extract images from a PDF export.
    
    Args:
        export_id: Export ID
        name_prefix: Prefix for image filenames
        min_size: Minimum image size in pixels
        
    Returns:
        List of paths to extracted images
    """
    status = await canva_export_manager.get_export_status(export_id)
    
    if not status:
        raise HTTPException(
            status_code=404,
            detail=f"Export {export_id} not found"
        )
    
    if status.status != "completed":
        raise HTTPException(
            status_code=400,
            detail=f"Export {export_id} is not complete: {status.status}"
        )
    
    if not status.local_path:
        raise HTTPException(
            status_code=500,
            detail=f"Export {export_id} has no local file"
        )
    
    if status.export_type != "pdf":
        raise HTTPException(
            status_code=400,
            detail=f"Export {export_id} is not a PDF: {status.export_type}"
        )
    
    return await canva_export_manager.extract_images_from_pdf(
        pdf_path=status.local_path,
        name_prefix=name_prefix,
        min_size=min_size
    )


@router.post("/exports/{export_id}/convert-to-kdp", response_model=str)
async def convert_export_to_kdp(
    export_id: str,
    metadata: Optional[BookMetadata] = None
):
    """
    Convert a PDF export to KDP-compatible format.
    
    Args:
        export_id: Export ID
        metadata: Book metadata for sizing
        
    Returns:
        Path to converted PDF
    """
    status = await canva_export_manager.get_export_status(export_id)
    
    if not status:
        raise HTTPException(
            status_code=404,
            detail=f"Export {export_id} not found"
        )
    
    if status.status != "completed":
        raise HTTPException(
            status_code=400,
            detail=f"Export {export_id} is not complete: {status.status}"
        )
    
    if not status.local_path:
        raise HTTPException(
            status_code=500,
            detail=f"Export {export_id} has no local file"
        )
    
    if status.export_type != "pdf":
        raise HTTPException(
            status_code=400,
            detail=f"Export {export_id} is not a PDF: {status.export_type}"
        )
    
    return await canva_export_manager.convert_pdf_to_kdp_format(
        pdf_path=status.local_path,
        metadata=metadata
    )


# ---- Preview endpoints ----

@router.post("/previews", response_model=PreviewResult)
async def generate_design_preview(
    access_token: str,
    request: CanvaPreviewRequest
):
    """
    Generate a preview for a Canva design.
    
    Args:
        access_token: Canva API access token
        request: Preview request
        
    Returns:
        Preview result
    """
    options = PreviewOptions(
        width=request.width,
        height=request.height,
        format=request.format,
        quality=request.quality,
        page_number=request.page_number,
        include_bleed=request.include_bleed,
        include_spine=request.include_spine,
        show_grid=request.show_grid
    )
    
    return await canva_preview_manager.generate_design_preview(
        access_token=access_token,
        design_id=request.design_id,
        options=options
    )


@router.get("/previews/{preview_id}", response_model=PreviewResult)
async def get_preview(preview_id: str):
    """
    Get a previously generated preview.
    
    Args:
        preview_id: Preview ID
        
    Returns:
        Preview result
    """
    preview = await canva_preview_manager.get_preview(preview_id)
    
    if not preview:
        raise HTTPException(
            status_code=404,
            detail=f"Preview {preview_id} not found"
        )
    
    return preview


@router.post("/exports/{export_id}/preview", response_model=PreviewResult)
async def generate_interactive_preview(export_id: str):
    """
    Generate an interactive preview for an export.
    
    Args:
        export_id: Export ID
        
    Returns:
        Preview result with HTML data
    """
    status = await canva_export_manager.get_export_status(export_id)
    
    if not status:
        raise HTTPException(
            status_code=404,
            detail=f"Export {export_id} not found"
        )
    
    if status.status != "completed":
        raise HTTPException(
            status_code=400,
            detail=f"Export {export_id} is not complete: {status.status}"
        )
    
    if not status.local_path:
        raise HTTPException(
            status_code=500,
            detail=f"Export {export_id} has no local file"
        )
    
    if status.export_type != "pdf":
        raise HTTPException(
            status_code=400,
            detail=f"Export {export_id} is not a PDF: {status.export_type}"
        )
    
    return await canva_preview_manager.generate_interactive_preview(
        pdf_path=status.local_path,
        metadata=status.metadata
    )


# ---- Asset management endpoints ----

@router.get("/assets", response_model=Dict[str, Any])
async def get_user_assets(
    access_token: str,
    asset_type: Optional[str] = None,
    page_size: int = 20,
    cursor: Optional[str] = None
):
    """
    Get user's assets from Canva.
    
    Args:
        access_token: Canva API access token
        asset_type: Optional asset type filter
        page_size: Number of results per page
        cursor: Pagination cursor
        
    Returns:
        List of assets
    """
    return await canva_client.get_user_assets(
        access_token=access_token,
        asset_type=asset_type,
        page_size=page_size,
        cursor=cursor
    )


@router.get("/assets/{asset_id}", response_model=Dict[str, Any])
async def get_asset(access_token: str, asset_id: str):
    """
    Get asset information from Canva.
    
    Args:
        access_token: Canva API access token
        asset_id: Canva asset ID
        
    Returns:
        Asset information
    """
    return await canva_client.get_asset(
        access_token=access_token,
        asset_id=asset_id
    )


@router.post("/assets/upload", response_model=Dict[str, Any])
async def upload_asset(
    access_token: str,
    file_path: str,
    title: str,
    asset_type: str = "image"
):
    """
    Upload an asset to Canva.
    
    Args:
        access_token: Canva API access token
        file_path: Path to the asset file
        title: Asset title
        asset_type: Asset type (image, graphic)
        
    Returns:
        Uploaded asset information
    """
    return await canva_client.upload_asset(
        access_token=access_token,
        file_path=file_path,
        title=title,
        asset_type=asset_type
    )
