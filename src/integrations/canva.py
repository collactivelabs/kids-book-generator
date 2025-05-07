"""
Canva Connect API integration for Kids Book Generator.

This module handles integration with the Canva Connect API for
design creation, automation, and export functionality.

Documentation: https://www.canva.com/developers/docs/
"""
import os
import json
import logging
import time
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
import base64
import hashlib
import hmac
import uuid
from urllib.parse import urlencode, quote

import requests
from fastapi import HTTPException, Depends
import aiohttp
from pydantic import BaseModel, Field

from config import settings
from utils.logging import get_logger
from api.models import BookMetadata, BookType


logger = get_logger(__name__)


class CanvaDesign(BaseModel):
    """Model for Canva design information."""
    design_id: str = Field(..., description="Canva design ID")
    brand_id: Optional[str] = Field(None, description="Canva brand ID")
    title: str = Field(..., description="Design title")
    thumbnail_url: Optional[str] = Field(None, description="Thumbnail URL")
    created_at: datetime = Field(..., description="Creation timestamp")
    modified_at: datetime = Field(..., description="Last modification timestamp")
    width: int = Field(..., description="Design width in pixels")
    height: int = Field(..., description="Design height in pixels")
    status: str = Field("active", description="Design status")
    template_type: Optional[str] = Field(None, description="Type of template (story, coloring)")
    age_group: Optional[str] = Field(None, description="Target age group")


class CanvaDesignRequest(BaseModel):
    """Model for design creation request."""
    title: str = Field(..., description="Design title")
    template_id: Optional[str] = Field(None, description="Template ID to use")
    brand_id: Optional[str] = Field(None, description="Brand ID for design")
    folder_id: Optional[str] = Field(None, description="Folder ID for design")
    width: Optional[int] = Field(None, description="Design width in pixels")
    height: Optional[int] = Field(None, description="Design height in pixels")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


class CanvaExportRequest(BaseModel):
    """Model for design export request."""
    design_id: str = Field(..., description="Canva design ID")
    export_type: str = Field("pdf", description="Export type (pdf, png, jpg)")
    pdf_options: Optional[Dict[str, Any]] = Field(None, description="PDF export options")
    image_options: Optional[Dict[str, Any]] = Field(None, description="Image export options")


class CanvaAsset(BaseModel):
    """Model for Canva asset information."""
    asset_id: str = Field(..., description="Asset ID")
    asset_type: str = Field(..., description="Asset type (image, graphic)")
    title: str = Field(..., description="Asset title")
    url: Optional[str] = Field(None, description="Asset URL")
    thumbnail_url: Optional[str] = Field(None, description="Thumbnail URL")
    created_at: datetime = Field(..., description="Creation timestamp")
    width: Optional[int] = Field(None, description="Asset width in pixels")
    height: Optional[int] = Field(None, description="Asset height in pixels")
    status: str = Field("active", description="Asset status")


class CanvaConnectClient:
    """
    Client for Canva Connect API integration.
    
    This client handles all interactions with the Canva Connect API,
    including authentication, design creation, and asset management.
    """
    
    def __init__(self):
        """Initialize the Canva Connect client."""
        self.client_id = settings.CANVA_CLIENT_ID
        self.client_secret = settings.CANVA_CLIENT_SECRET
        self.redirect_uri = settings.CANVA_REDIRECT_URI
        self.api_base_url = "https://api.canva.com/v1"
        self.design_base_url = "https://api.canva.com/v1/designs"
        self.brand_base_url = "https://api.canva.com/v1/brands"
        self.template_base_url = "https://api.canva.com/v1/templates"
        self.asset_base_url = "https://api.canva.com/v1/assets"
        
        # Rate limit handling
        self.rate_limit_remaining = 1000  # Default
        self.rate_limit_reset = datetime.now() + timedelta(hours=1)  # Default
        
        # Template mapping for different book types
        self.template_mapping = {
            "story": {
                "standard": "template_id_for_standard_story_book",
                "square": "template_id_for_square_story_book"
            },
            "coloring": {
                "standard": "template_id_for_standard_coloring_book",
                "square": "template_id_for_square_coloring_book"
            }
        }
    
    async def _make_request(
        self,
        method: str,
        endpoint: str,
        access_token: str,
        params: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        retry_count: int = 0
    ) -> Dict[str, Any]:
        """
        Make an authenticated request to the Canva API.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint path
            access_token: OAuth access token
            params: Query parameters
            json_data: JSON payload
            headers: Additional headers
            retry_count: Number of retries attempted
            
        Returns:
            API response as dictionary
        """
        # Check rate limiting
        if self.rate_limit_remaining <= 5 and datetime.now() < self.rate_limit_reset:
            wait_time = (self.rate_limit_reset - datetime.now()).total_seconds()
            logger.warning(f"Rate limit almost reached. Waiting {wait_time:.2f} seconds")
            time.sleep(min(wait_time, 60))  # Wait at most 60 seconds
        
        # Prepare request
        url = f"{self.api_base_url}{endpoint}"
        
        # Default headers
        default_headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        # Merge with custom headers
        if headers:
            default_headers.update(headers)
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.request(
                    method=method,
                    url=url,
                    params=params,
                    json=json_data,
                    headers=default_headers
                ) as response:
                    # Update rate limit info from headers
                    if "X-RateLimit-Remaining" in response.headers:
                        self.rate_limit_remaining = int(response.headers["X-RateLimit-Remaining"])
                    if "X-RateLimit-Reset" in response.headers:
                        reset_time = int(response.headers["X-RateLimit-Reset"])
                        self.rate_limit_reset = datetime.fromtimestamp(reset_time)
                    
                    # Handle response
                    if response.status == 429:  # Too Many Requests
                        if retry_count < 3:
                            wait_time = 2 ** retry_count  # Exponential backoff
                            logger.warning(f"Rate limited. Waiting {wait_time} seconds before retry")
                            time.sleep(wait_time)
                            return await self._make_request(
                                method, endpoint, access_token, params,
                                json_data, headers, retry_count + 1
                            )
                        else:
                            raise HTTPException(status_code=429, detail="Canva API rate limit exceeded")
                    
                    # Parse JSON response
                    response_json = await response.json()
                    
                    # Check for errors
                    if not response.ok:
                        error_message = response_json.get("error", {}).get("message", "Unknown error")
                        logger.error(f"Canva API error: {error_message}")
                        raise HTTPException(
                            status_code=response.status,
                            detail=f"Canva API error: {error_message}"
                        )
                    
                    return response_json
        
        except aiohttp.ClientError as e:
            logger.error(f"Canva API request failed: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Failed to connect to Canva API: {str(e)}")
    
    def get_authorization_url(self, state: Optional[str] = None) -> str:
        """
        Generate the Canva OAuth authorization URL.
        
        Args:
            state: Optional state for CSRF protection
            
        Returns:
            Authorization URL
        """
        if not state:
            state = base64.urlsafe_b64encode(os.urandom(32)).decode("utf-8")
        
        params = {
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "response_type": "code",
            "scope": "design.read design.write asset.read asset.write brand.read",
            "state": state
        }
        
        auth_url = f"https://www.canva.com/oauth/authorize?{urlencode(params)}"
        return auth_url
    
    async def exchange_code_for_token(self, code: str) -> Dict[str, Any]:
        """
        Exchange authorization code for access token.
        
        Args:
            code: Authorization code from redirect
            
        Returns:
            Token response including access_token and refresh_token
        """
        token_url = "https://api.canva.com/oauth/token"
        payload = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "code": code,
            "redirect_uri": self.redirect_uri,
            "grant_type": "authorization_code"
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(token_url, data=payload) as response:
                    response_json = await response.json()
                    
                    if response.status != 200:
                        error_message = response_json.get("error_description", "Unknown error")
                        logger.error(f"Failed to exchange code for token: {error_message}")
                        raise HTTPException(
                            status_code=response.status,
                            detail=f"Failed to authenticate with Canva: {error_message}"
                        )
                    
                    return response_json
        
        except aiohttp.ClientError as e:
            logger.error(f"Failed to exchange code for token: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Failed to authenticate with Canva: {str(e)}")
    
    async def refresh_access_token(self, refresh_token: str) -> Dict[str, Any]:
        """
        Refresh OAuth access token.
        
        Args:
            refresh_token: OAuth refresh token
            
        Returns:
            New token response
        """
        token_url = "https://api.canva.com/oauth/token"
        payload = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "refresh_token": refresh_token,
            "grant_type": "refresh_token"
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(token_url, data=payload) as response:
                    response_json = await response.json()
                    
                    if response.status != 200:
                        error_message = response_json.get("error_description", "Unknown error")
                        logger.error(f"Failed to refresh token: {error_message}")
                        raise HTTPException(
                            status_code=response.status,
                            detail=f"Failed to refresh Canva token: {error_message}"
                        )
                    
                    return response_json
        
        except aiohttp.ClientError as e:
            logger.error(f"Failed to refresh token: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Failed to refresh Canva token: {str(e)}")
    
    async def get_templates(
        self,
        access_token: str,
        category: Optional[str] = None,
        page_size: int = 20,
        cursor: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get available templates from Canva.
        
        Args:
            access_token: OAuth access token
            category: Optional category filter
            page_size: Number of results per page
            cursor: Pagination cursor
            
        Returns:
            List of templates
        """
        params = {"pageSize": page_size}
        if category:
            params["category"] = category
        if cursor:
            params["cursor"] = cursor
        
        return await self._make_request(
            "GET", "/templates", access_token, params=params
        )
    
    async def get_user_designs(
        self,
        access_token: str,
        page_size: int = 20,
        cursor: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get user's designs from Canva.
        
        Args:
            access_token: OAuth access token
            page_size: Number of results per page
            cursor: Pagination cursor
            
        Returns:
            List of designs
        """
        params = {"pageSize": page_size}
        if cursor:
            params["cursor"] = cursor
        
        return await self._make_request(
            "GET", "/designs", access_token, params=params
        )
    
    async def create_design(
        self,
        access_token: str,
        design_request: CanvaDesignRequest
    ) -> Dict[str, Any]:
        """
        Create a new design in Canva.
        
        Args:
            access_token: OAuth access token
            design_request: Design creation request
            
        Returns:
            Created design information
        """
        payload = {
            "title": design_request.title,
        }
        
        if design_request.template_id:
            payload["templateId"] = design_request.template_id
        
        if design_request.brand_id:
            payload["brandId"] = design_request.brand_id
        
        if design_request.folder_id:
            payload["folderId"] = design_request.folder_id
        
        if design_request.width and design_request.height:
            payload["dimensions"] = {
                "width": design_request.width,
                "height": design_request.height
            }
        
        if design_request.metadata:
            payload["metadata"] = design_request.metadata
        
        return await self._make_request(
            "POST", "/designs", access_token, json_data=payload
        )
    
    async def get_design(
        self,
        access_token: str,
        design_id: str
    ) -> Dict[str, Any]:
        """
        Get design information from Canva.
        
        Args:
            access_token: OAuth access token
            design_id: Canva design ID
            
        Returns:
            Design information
        """
        return await self._make_request(
            "GET", f"/designs/{design_id}", access_token
        )
    
    async def update_design(
        self,
        access_token: str,
        design_id: str,
        title: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Update an existing design in Canva.
        
        Args:
            access_token: OAuth access token
            design_id: Canva design ID
            title: New design title
            metadata: Updated metadata
            
        Returns:
            Updated design information
        """
        payload = {}
        if title:
            payload["title"] = title
        if metadata:
            payload["metadata"] = metadata
        
        return await self._make_request(
            "PATCH", f"/designs/{design_id}", access_token, json_data=payload
        )
    
    async def export_design(
        self,
        access_token: str,
        export_request: CanvaExportRequest
    ) -> Dict[str, Any]:
        """
        Export a design from Canva.
        
        Args:
            access_token: OAuth access token
            export_request: Export request details
            
        Returns:
            Export information including download URL
        """
        payload = {
            "exportType": export_request.export_type
        }
        
        if export_request.export_type == "pdf" and export_request.pdf_options:
            payload["pdfOptions"] = export_request.pdf_options
        
        elif export_request.export_type in ["png", "jpg"] and export_request.image_options:
            payload["imageOptions"] = export_request.image_options
        
        return await self._make_request(
            "POST", 
            f"/designs/{export_request.design_id}/exports", 
            access_token, 
            json_data=payload
        )
    
    async def get_export_status(
        self,
        access_token: str,
        design_id: str,
        export_id: str
    ) -> Dict[str, Any]:
        """
        Check the status of a design export.
        
        Args:
            access_token: OAuth access token
            design_id: Canva design ID
            export_id: Export ID
            
        Returns:
            Export status information
        """
        return await self._make_request(
            "GET", 
            f"/designs/{design_id}/exports/{export_id}", 
            access_token
        )
    
    async def upload_asset(
        self,
        access_token: str,
        file_path: str,
        title: str,
        asset_type: str = "image"
    ) -> Dict[str, Any]:
        """
        Upload an asset to Canva.
        
        Args:
            access_token: OAuth access token
            file_path: Path to the asset file
            title: Asset title
            asset_type: Asset type (image, graphic)
            
        Returns:
            Uploaded asset information
        """
        # Step 1: Request upload URL
        upload_request_payload = {
            "title": title,
            "type": asset_type
        }
        
        upload_url_response = await self._make_request(
            "POST", 
            "/assets/uploads", 
            access_token, 
            json_data=upload_request_payload
        )
        
        upload_url = upload_url_response.get("uploadUrl")
        asset_id = upload_url_response.get("assetId")
        
        if not upload_url or not asset_id:
            raise HTTPException(status_code=500, detail="Failed to get asset upload URL")
        
        # Step 2: Upload file to the provided URL
        try:
            with open(file_path, "rb") as file:
                file_content = file.read()
                
            async with aiohttp.ClientSession() as session:
                async with session.put(
                    upload_url,
                    data=file_content,
                    headers={"Content-Type": "application/octet-stream"}
                ) as response:
                    if not response.ok:
                        error_text = await response.text()
                        logger.error(f"Failed to upload asset: {error_text}")
                        raise HTTPException(
                            status_code=response.status,
                            detail=f"Failed to upload asset: {error_text}"
                        )
        
        except (IOError, aiohttp.ClientError) as e:
            logger.error(f"Failed to upload asset: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Failed to upload asset: {str(e)}")
        
        # Step 3: Complete the upload
        complete_upload_response = await self._make_request(
            "POST", 
            f"/assets/uploads/{asset_id}/complete", 
            access_token
        )
        
        return complete_upload_response
    
    async def get_asset(
        self,
        access_token: str,
        asset_id: str
    ) -> Dict[str, Any]:
        """
        Get asset information from Canva.
        
        Args:
            access_token: OAuth access token
            asset_id: Canva asset ID
            
        Returns:
            Asset information
        """
        return await self._make_request(
            "GET", f"/assets/{asset_id}", access_token
        )
    
    async def get_user_assets(
        self,
        access_token: str,
        asset_type: Optional[str] = None,
        page_size: int = 20,
        cursor: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get user's assets from Canva.
        
        Args:
            access_token: OAuth access token
            asset_type: Optional asset type filter
            page_size: Number of results per page
            cursor: Pagination cursor
            
        Returns:
            List of assets
        """
        params = {"pageSize": page_size}
        if asset_type:
            params["type"] = asset_type
        if cursor:
            params["cursor"] = cursor
        
        return await self._make_request(
            "GET", "/assets", access_token, params=params
        )
    
    async def get_brands(
        self,
        access_token: str,
        page_size: int = 20,
        cursor: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get user's brands from Canva.
        
        Args:
            access_token: OAuth access token
            page_size: Number of results per page
            cursor: Pagination cursor
            
        Returns:
            List of brands
        """
        params = {"pageSize": page_size}
        if cursor:
            params["cursor"] = cursor
        
        return await self._make_request(
            "GET", "/brands", access_token, params=params
        )
    
    async def get_brand(
        self,
        access_token: str,
        brand_id: str
    ) -> Dict[str, Any]:
        """
        Get brand information from Canva.
        
        Args:
            access_token: OAuth access token
            brand_id: Canva brand ID
            
        Returns:
            Brand information
        """
        return await self._make_request(
            "GET", f"/brands/{brand_id}", access_token
        )
    
    async def create_design_from_book_metadata(
        self,
        access_token: str,
        metadata: BookMetadata
    ) -> Dict[str, Any]:
        """
        Create a design based on book metadata.
        
        Args:
            access_token: OAuth access token
            metadata: Book metadata
            
        Returns:
            Created design information
        """
        # Determine template based on book type and trim size
        book_type = metadata.book_type.value  # 'story' or 'coloring'
        trim_size = metadata.trim_size.value  # e.g., '8.5x11' or '8.5x8.5'
        template_type = "standard"
        
        if "8.5x8.5" in trim_size:
            template_type = "square"
        
        template_id = self.template_mapping.get(book_type, {}).get(template_type)
        
        # Create design request
        design_request = CanvaDesignRequest(
            title=metadata.title,
            template_id=template_id,
            metadata={
                "book_type": metadata.book_type.value,
                "age_group": metadata.age_group.value,
                "author": metadata.author,
                "theme": metadata.theme,
                "educational_focus": metadata.educational_focus,
                "trim_size": metadata.trim_size.value,
                "page_count": metadata.page_count
            }
        )
        
        # Create the design
        return await self.create_design(access_token, design_request)


# Create singleton instance
canva_client = CanvaConnectClient()
