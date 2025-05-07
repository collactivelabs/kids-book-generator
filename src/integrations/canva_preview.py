"""
Canva design preview system for Kids Book Generator.

This module handles real-time preview generation for Canva designs,
including thumbnail generation, PDF previews, and interactive previews.
"""
import os
import asyncio
import logging
import base64
import tempfile
from typing import Dict, List, Optional, Any, Union, BinaryIO
from pathlib import Path
from datetime import datetime
import io
import re
import uuid

import aiohttp
from fastapi import HTTPException, Depends
from pydantic import BaseModel, Field
import fitz  # PyMuPDF
from PIL import Image

from config import settings
from utils.logging import get_logger
from api.models import BookMetadata
from integrations.canva import canva_client
from integrations.canva_export import canva_export_manager


logger = get_logger(__name__)


class PreviewOptions(BaseModel):
    """Model for preview options."""
    width: Optional[int] = Field(None, description="Preview width in pixels")
    height: Optional[int] = Field(None, description="Preview height in pixels")
    format: str = Field("png", description="Image format (png, jpg, webp)")
    quality: int = Field(90, description="Image quality (1-100)")
    page_number: Optional[int] = Field(None, description="Page number to preview (for PDF)")
    include_bleed: bool = Field(False, description="Include bleed area in preview")
    include_spine: bool = Field(False, description="Include spine in cover preview")
    show_grid: bool = Field(False, description="Show grid overlay")


class PreviewResult(BaseModel):
    """Model for preview result."""
    preview_id: str = Field(..., description="Unique preview ID")
    preview_url: Optional[str] = Field(None, description="Preview URL")
    preview_data: Optional[str] = Field(None, description="Base64-encoded preview data")
    preview_type: str = Field(..., description="Preview type (image, pdf, html)")
    width: Optional[int] = Field(None, description="Preview width in pixels")
    height: Optional[int] = Field(None, description="Preview height in pixels")
    page_count: Optional[int] = Field(None, description="Number of pages (for PDF)")
    created_at: datetime = Field(default_factory=datetime.now, description="Creation timestamp")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class CanvaPreviewManager:
    """
    Manager for Canva design previews.
    
    This class handles:
    - Generating thumbnails from designs
    - Creating interactive previews
    - Converting between preview formats
    """
    
    def __init__(self, preview_dir: Optional[str] = None):
        """
        Initialize the preview manager.
        
        Args:
            preview_dir: Directory to store preview files
        """
        # Set up directory
        self.preview_dir = Path(preview_dir) if preview_dir else Path(settings.STORAGE_DIR) / "canva_previews"
        os.makedirs(self.preview_dir, exist_ok=True)
        
        # Preview cache
        self.previews: Dict[str, Dict[str, Any]] = {}
    
    async def generate_design_preview(
        self,
        access_token: str,
        design_id: str,
        options: Optional[PreviewOptions] = None
    ) -> PreviewResult:
        """
        Generate a preview for a Canva design.
        
        Args:
            access_token: Canva API access token
            design_id: Canva design ID
            options: Preview options
            
        Returns:
            Preview result
        """
        # Use default options if not provided
        if not options:
            options = PreviewOptions()
        
        # Generate preview ID
        preview_id = f"preview_{uuid.uuid4().hex}"
        
        try:
            # Request thumbnail or export depending on needs
            if options.page_number is None or options.page_number == 1:
                # Get design info, which includes thumbnail
                design_info = await canva_client.get_design(
                    access_token=access_token,
                    design_id=design_id
                )
                
                # Get thumbnail URL
                thumbnail_url = design_info.get("thumbnail", {}).get("url")
                if not thumbnail_url:
                    logger.warning(f"No thumbnail URL for design {design_id}, using export instead")
                    return await self._generate_preview_from_export(
                        access_token=access_token,
                        design_id=design_id,
                        preview_id=preview_id,
                        options=options
                    )
                
                # Download and process thumbnail
                preview_data = await self._process_thumbnail(
                    thumbnail_url=thumbnail_url,
                    preview_id=preview_id,
                    options=options
                )
                
                result = PreviewResult(
                    preview_id=preview_id,
                    preview_data=preview_data,
                    preview_type="image",
                    width=options.width,
                    height=options.height,
                    created_at=datetime.now(),
                    metadata={
                        "design_id": design_id,
                        "source": "thumbnail"
                    }
                )
                
                # Cache result
                self.previews[preview_id] = result.dict()
                
                return result
            
            else:
                # For specific pages, we need to export the design
                return await self._generate_preview_from_export(
                    access_token=access_token,
                    design_id=design_id,
                    preview_id=preview_id,
                    options=options
                )
        
        except Exception as e:
            logger.error(f"Failed to generate preview for design {design_id}: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to generate preview: {str(e)}"
            )
    
    async def _process_thumbnail(
        self,
        thumbnail_url: str,
        preview_id: str,
        options: PreviewOptions
    ) -> str:
        """
        Process a thumbnail image.
        
        Args:
            thumbnail_url: Thumbnail URL
            preview_id: Preview ID
            options: Preview options
            
        Returns:
            Base64-encoded image data
        """
        try:
            # Download thumbnail
            async with aiohttp.ClientSession() as session:
                async with session.get(thumbnail_url) as response:
                    if not response.ok:
                        error_text = await response.text()
                        logger.error(f"Failed to download thumbnail: {error_text}")
                        raise ValueError(f"Failed to download thumbnail: {response.status}")
                    
                    # Get image data
                    image_data = await response.read()
            
            # Process image with PIL
            with Image.open(io.BytesIO(image_data)) as img:
                # Original dimensions
                original_width, original_height = img.size
                
                # Resize if dimensions provided
                if options.width and options.height:
                    img = img.resize((options.width, options.height), Image.LANCZOS)
                elif options.width:
                    ratio = options.width / original_width
                    height = int(original_height * ratio)
                    img = img.resize((options.width, height), Image.LANCZOS)
                elif options.height:
                    ratio = options.height / original_height
                    width = int(original_width * ratio)
                    img = img.resize((width, options.height), Image.LANCZOS)
                
                # Show grid if requested
                if options.show_grid:
                    img = self._add_grid_overlay(img)
                
                # Save to buffer
                buffer = io.BytesIO()
                format_str = options.format.upper()
                if format_str == "JPG":
                    format_str = "JPEG"
                
                img.save(
                    buffer,
                    format=format_str,
                    quality=options.quality
                )
                
                # Encode as base64
                encoded = base64.b64encode(buffer.getvalue()).decode("utf-8")
                return f"data:image/{options.format.lower()};base64,{encoded}"
        
        except Exception as e:
            logger.error(f"Failed to process thumbnail: {str(e)}")
            raise
    
    async def _generate_preview_from_export(
        self,
        access_token: str,
        design_id: str,
        preview_id: str,
        options: PreviewOptions
    ) -> PreviewResult:
        """
        Generate a preview from a design export.
        
        Args:
            access_token: Canva API access token
            design_id: Canva design ID
            preview_id: Preview ID
            options: Preview options
            
        Returns:
            Preview result
        """
        # Start export
        export_id = await canva_export_manager.export_design(
            access_token=access_token,
            design_id=design_id,
            export_type="pdf"
        )
        
        # Wait for export to complete
        max_attempts = 30
        delay = 2
        
        for attempt in range(max_attempts):
            export_status = await canva_export_manager.get_export_status(export_id)
            
            if export_status.status == "completed":
                # Export completed
                pdf_path = export_status.local_path
                break
            
            elif export_status.status == "failed":
                # Export failed
                raise ValueError(f"Design export failed: {export_status.error}")
            
            # Wait before checking again
            await asyncio.sleep(delay)
        
        else:
            # Export timed out
            raise TimeoutError(f"Export timed out after {max_attempts * delay} seconds")
        
        # Generate preview from PDF
        return await self._generate_preview_from_pdf(
            pdf_path=pdf_path,
            preview_id=preview_id,
            options=options,
            metadata={
                "design_id": design_id,
                "export_id": export_id,
                "source": "export"
            }
        )
    
    async def _generate_preview_from_pdf(
        self,
        pdf_path: str,
        preview_id: str,
        options: PreviewOptions,
        metadata: Optional[Dict[str, Any]] = None
    ) -> PreviewResult:
        """
        Generate a preview from a PDF file.
        
        Args:
            pdf_path: Path to PDF file
            preview_id: Preview ID
            options: Preview options
            metadata: Additional metadata
            
        Returns:
            Preview result
        """
        # Open PDF
        pdf = fitz.open(pdf_path)
        
        # Get page count
        page_count = len(pdf)
        
        # Determine page to preview
        page_num = options.page_number - 1 if options.page_number else 0
        if page_num < 0 or page_num >= page_count:
            # Default to first page if out of range
            page_num = 0
        
        # Get page
        page = pdf[page_num]
        
        # Get dimensions
        width, height = page.rect.width, page.rect.height
        
        # Render page to pixmap
        zoom = 2  # Higher quality
        mat = fitz.Matrix(zoom, zoom)
        pix = page.get_pixmap(matrix=mat)
        
        # Convert to PIL Image
        img_data = pix.samples
        img = Image.frombytes("RGB", [pix.width, pix.height], img_data)
        
        # Resize if dimensions provided
        if options.width and options.height:
            img = img.resize((options.width, options.height), Image.LANCZOS)
        elif options.width:
            ratio = options.width / img.width
            height = int(img.height * ratio)
            img = img.resize((options.width, height), Image.LANCZOS)
        elif options.height:
            ratio = options.height / img.height
            width = int(img.width * ratio)
            img = img.resize((width, options.height), Image.LANCZOS)
        
        # Show grid if requested
        if options.show_grid:
            img = self._add_grid_overlay(img)
        
        # Save to buffer
        buffer = io.BytesIO()
        format_str = options.format.upper()
        if format_str == "JPG":
            format_str = "JPEG"
        
        img.save(
            buffer,
            format=format_str,
            quality=options.quality
        )
        
        # Encode as base64
        encoded = base64.b64encode(buffer.getvalue()).decode("utf-8")
        preview_data = f"data:image/{options.format.lower()};base64,{encoded}"
        
        # Create result
        result = PreviewResult(
            preview_id=preview_id,
            preview_data=preview_data,
            preview_type="image",
            width=img.width,
            height=img.height,
            page_count=page_count,
            created_at=datetime.now(),
            metadata=metadata or {}
        )
        
        # Cache result
        self.previews[preview_id] = result.dict()
        
        return result
    
    def _add_grid_overlay(self, img: Image.Image) -> Image.Image:
        """
        Add a grid overlay to an image.
        
        Args:
            img: PIL Image
            
        Returns:
            Image with grid overlay
        """
        # Create a copy of the image
        img_with_grid = img.copy()
        
        # Get dimensions
        width, height = img_with_grid.size
        
        # Create a new image for the grid
        grid_img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        
        # Draw the grid
        from PIL import ImageDraw
        draw = ImageDraw.Draw(grid_img)
        
        # Grid size (inches on the final print)
        grid_size = 72  # 1 inch at 72 DPI
        
        # Draw vertical lines
        for x in range(0, width, grid_size):
            draw.line([(x, 0), (x, height)], fill=(255, 0, 0, 128), width=1)
        
        # Draw horizontal lines
        for y in range(0, height, grid_size):
            draw.line([(0, y), (width, y)], fill=(255, 0, 0, 128), width=1)
        
        # Overlay the grid on the original image
        img_with_grid = Image.alpha_composite(
            img_with_grid.convert("RGBA"),
            grid_img
        )
        
        return img_with_grid.convert("RGB")
    
    async def generate_interactive_preview(
        self,
        pdf_path: str,
        preview_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> PreviewResult:
        """
        Generate an interactive HTML preview for a PDF.
        
        Args:
            pdf_path: Path to PDF file
            preview_id: Optional preview ID
            metadata: Additional metadata
            
        Returns:
            Preview result with HTML data
        """
        if not preview_id:
            preview_id = f"preview_{uuid.uuid4().hex}"
        
        # Create output directory
        output_dir = self.preview_dir / preview_id
        os.makedirs(output_dir, exist_ok=True)
        
        # Create HTML preview
        html_path = output_dir / "preview.html"
        pdf_filename = os.path.basename(pdf_path)
        
        # Copy PDF to preview directory
        preview_pdf_path = output_dir / pdf_filename
        with open(pdf_path, "rb") as src_file, open(preview_pdf_path, "wb") as dst_file:
            dst_file.write(src_file.read())
        
        # Create HTML content
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>PDF Preview</title>
            <style>
                body {{
                    margin: 0;
                    padding: 0;
                    display: flex;
                    flex-direction: column;
                    height: 100vh;
                    font-family: Arial, sans-serif;
                }}
                .toolbar {{
                    background-color: #f0f0f0;
                    padding: 10px;
                    display: flex;
                    gap: 10px;
                    align-items: center;
                    border-bottom: 1px solid #ddd;
                }}
                .viewer {{
                    flex-grow: 1;
                    border: none;
                    width: 100%;
                    height: 100%;
                }}
                button {{
                    padding: 8px 12px;
                    border-radius: 4px;
                    border: 1px solid #ddd;
                    background-color: white;
                    cursor: pointer;
                }}
                button:hover {{
                    background-color: #f9f9f9;
                }}
                .page-info {{
                    margin-left: auto;
                }}
            </style>
        </head>
        <body>
            <div class="toolbar">
                <button id="prev">Previous</button>
                <button id="next">Next</button>
                <div class="page-info">
                    Page <span id="page-num"></span> of <span id="page-count"></span>
                </div>
            </div>
            <iframe class="viewer" src="{pdf_filename}"></iframe>
            
            <script>
                // Basic viewer controls
                const iframe = document.querySelector('.viewer');
                const prevButton = document.getElementById('prev');
                const nextButton = document.getElementById('next');
                const pageNum = document.getElementById('page-num');
                const pageCount = document.getElementById('page-count');
                
                let currentPage = 1;
                let totalPages = 0;
                
                // Load PDF.js viewer (simplified approach)
                iframe.onload = function() {{
                    // This is a simple approach; a real implementation 
                    // would use PDF.js for a better viewer experience
                    pageNum.textContent = currentPage;
                    // Estimate page count (this is not accurate)
                    totalPages = 1;
                    pageCount.textContent = totalPages;
                }};
                
                prevButton.addEventListener('click', () => {{
                    if (currentPage > 1) {{
                        currentPage--;
                        pageNum.textContent = currentPage;
                        // In a real implementation, would change the PDF page
                    }}
                }});
                
                nextButton.addEventListener('click', () => {{
                    if (currentPage < totalPages) {{
                        currentPage++;
                        pageNum.textContent = currentPage;
                        // In a real implementation, would change the PDF page
                    }}
                }});
            </script>
        </body>
        </html>
        """
        
        # Write HTML file
        with open(html_path, "w") as f:
            f.write(html_content)
        
        # Create result
        result = PreviewResult(
            preview_id=preview_id,
            preview_url=f"/previews/{preview_id}/preview.html",
            preview_type="html",
            created_at=datetime.now(),
            metadata=metadata or {}
        )
        
        # Cache result
        self.previews[preview_id] = result.dict()
        
        return result
    
    async def get_preview(self, preview_id: str) -> Optional[PreviewResult]:
        """
        Get a previously generated preview.
        
        Args:
            preview_id: Preview ID
            
        Returns:
            Preview result, or None if not found
        """
        preview_data = self.previews.get(preview_id)
        if not preview_data:
            return None
        
        return PreviewResult(**preview_data)


# Create singleton instance
canva_preview_manager = CanvaPreviewManager()
