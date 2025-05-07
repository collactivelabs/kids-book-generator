"""
Canva design export system for Kids Book Generator.

This module handles exporting designs from Canva to the local system,
including PDF export, image extraction, and format conversions.
"""
import os
import time
import asyncio
import json
import logging
from typing import Dict, List, Optional, Any, Union, Tuple
from pathlib import Path
from datetime import datetime, timedelta
import tempfile
import uuid
import shutil

import aiohttp
from fastapi import HTTPException, Depends
from pydantic import BaseModel, Field
import fitz  # PyMuPDF
from PIL import Image, ImageOps

from src.config import settings
from src.utils.logging import get_logger
from src.api.models import BookMetadata, BookType
from src.integrations.canva import canva_client, CanvaExportRequest


logger = get_logger(__name__)


class ExportStatus(BaseModel):
    """Model for export status tracking."""
    export_id: str = Field(..., description="Unique export ID")
    design_id: str = Field(..., description="Canva design ID")
    status: str = Field("pending", description="Export status")
    started_at: datetime = Field(default_factory=datetime.now, description="Start timestamp")
    completed_at: Optional[datetime] = Field(None, description="Completion timestamp")
    download_url: Optional[str] = Field(None, description="Download URL")
    local_path: Optional[str] = Field(None, description="Local file path")
    export_type: str = Field("pdf", description="Export type")
    error: Optional[str] = Field(None, description="Error message if failed")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class CanvaExportManager:
    """
    Manager for exporting Canva designs.
    
    This class handles:
    - Exporting designs from Canva as PDFs
    - Extracting images from PDFs
    - Converting designs to KDP-compatible formats
    - Tracking export status
    """
    
    def __init__(self, export_dir: Optional[str] = None):
        """
        Initialize the export manager.
        
        Args:
            export_dir: Directory to store exported files
        """
        # Set up directory
        self.export_dir = Path(export_dir) if export_dir else Path(settings.STORAGE_DIR) / "canva_exports"
        os.makedirs(self.export_dir, exist_ok=True)
        
        # Export status tracking
        self.exports: Dict[str, ExportStatus] = {}
        
        # Background tasks
        self.tasks = {}
    
    async def export_design(
        self,
        access_token: str,
        design_id: str,
        export_type: str = "pdf",
        pdf_options: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Start exporting a design from Canva.
        
        Args:
            access_token: Canva API access token
            design_id: Canva design ID
            export_type: Export type (pdf, png, jpg)
            pdf_options: PDF export options
            metadata: Additional metadata
            
        Returns:
            Export ID for tracking status
        """
        # Generate export ID
        export_id = f"export_{uuid.uuid4().hex}"
        
        # Create export status
        status = ExportStatus(
            export_id=export_id,
            design_id=design_id,
            status="pending",
            export_type=export_type,
            metadata=metadata or {}
        )
        self.exports[export_id] = status
        
        # Start background task
        task = asyncio.create_task(
            self._process_export(
                export_id=export_id,
                access_token=access_token,
                design_id=design_id,
                export_type=export_type,
                pdf_options=pdf_options
            )
        )
        self.tasks[export_id] = task
        
        return export_id
    
    async def _process_export(
        self,
        export_id: str,
        access_token: str,
        design_id: str,
        export_type: str,
        pdf_options: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Process a design export in the background.
        
        Args:
            export_id: Export ID
            access_token: Canva API access token
            design_id: Canva design ID
            export_type: Export type (pdf, png, jpg)
            pdf_options: PDF export options
        """
        status = self.exports[export_id]
        
        try:
            # Update status
            status.status = "processing"
            
            # Create export request
            export_request = CanvaExportRequest(
                design_id=design_id,
                export_type=export_type,
                pdf_options=pdf_options
            )
            
            # Start export
            export_response = await canva_client.export_design(
                access_token=access_token,
                export_request=export_request
            )
            
            # Get export ID from Canva
            canva_export_id = export_response.get("exportId")
            if not canva_export_id:
                raise ValueError("No export ID in Canva response")
            
            # Wait for export to complete
            download_url = await self._wait_for_export(
                access_token=access_token,
                design_id=design_id,
                export_id=canva_export_id
            )
            
            # Download file
            local_path = await self._download_export(
                export_id=export_id,
                download_url=download_url,
                export_type=export_type
            )
            
            # Update status
            status.status = "completed"
            status.completed_at = datetime.now()
            status.download_url = download_url
            status.local_path = str(local_path)
            
            logger.info(f"Design export {export_id} completed: {local_path}")
        
        except Exception as e:
            # Update status with error
            status.status = "failed"
            status.error = str(e)
            status.completed_at = datetime.now()
            
            logger.error(f"Design export {export_id} failed: {str(e)}")
    
    async def _wait_for_export(
        self,
        access_token: str,
        design_id: str,
        export_id: str,
        max_attempts: int = 30,
        delay: int = 2
    ) -> str:
        """
        Wait for an export to complete.
        
        Args:
            access_token: Canva API access token
            design_id: Canva design ID
            export_id: Canva export ID
            max_attempts: Maximum number of polling attempts
            delay: Delay between polling attempts in seconds
            
        Returns:
            Download URL
        """
        for attempt in range(max_attempts):
            # Get export status
            export_status = await canva_client.get_export_status(
                access_token=access_token,
                design_id=design_id,
                export_id=export_id
            )
            
            # Check status
            status = export_status.get("status")
            if status == "completed":
                download_url = export_status.get("downloadUrl")
                if not download_url:
                    raise ValueError("No download URL in export status")
                return download_url
            
            elif status == "failed":
                error = export_status.get("error", {}).get("message", "Unknown error")
                logger.error(f"Canva export failed: {error}")
                raise ValueError(f"Canva export failed: {error}")
            
            # Wait before checking again
            await asyncio.sleep(delay)
        
        # If we get here, the export timed out
        raise TimeoutError(f"Export timed out after {max_attempts * delay} seconds")
    
    async def _download_export(
        self,
        export_id: str,
        download_url: str,
        export_type: str
    ) -> Path:
        """
        Download an exported file.
        
        Args:
            export_id: Export ID
            download_url: Download URL
            export_type: Export type (pdf, png, jpg)
            
        Returns:
            Path to downloaded file
        """
        # Determine file extension
        extension = export_type.lower()
        
        # Prepare local path
        filename = f"{export_id}.{extension}"
        local_path = self.export_dir / filename
        
        try:
            # Download file
            async with aiohttp.ClientSession() as session:
                async with session.get(download_url) as response:
                    if not response.ok:
                        error_text = await response.text()
                        logger.error(f"Failed to download export: {error_text}")
                        raise ValueError(f"Failed to download export: {response.status}")
                    
                    # Save to file
                    content = await response.read()
                    with open(local_path, "wb") as f:
                        f.write(content)
            
            logger.info(f"Downloaded export to {local_path}")
            return local_path
        
        except Exception as e:
            logger.error(f"Failed to download export: {str(e)}")
            raise
    
    async def get_export_status(self, export_id: str) -> Optional[ExportStatus]:
        """
        Get the status of an export.
        
        Args:
            export_id: Export ID
            
        Returns:
            Export status, or None if not found
        """
        return self.exports.get(export_id)
    
    async def extract_images_from_pdf(
        self,
        pdf_path: Union[str, Path],
        output_dir: Optional[Union[str, Path]] = None,
        name_prefix: str = "image",
        min_size: int = 100
    ) -> List[str]:
        """
        Extract images from a PDF file.
        
        Args:
            pdf_path: Path to PDF file
            output_dir: Directory to save extracted images
            name_prefix: Prefix for image filenames
            min_size: Minimum image size in pixels
            
        Returns:
            List of paths to extracted images
        """
        # Convert to Path object
        pdf_path = Path(pdf_path)
        
        # Create output directory
        if output_dir:
            output_dir = Path(output_dir)
        else:
            output_dir = self.export_dir / f"images_{pdf_path.stem}"
        
        os.makedirs(output_dir, exist_ok=True)
        
        # Open PDF
        pdf = fitz.open(pdf_path)
        extracted_paths = []
        
        # Iterate through pages
        for page_num, page in enumerate(pdf):
            # Get page images
            image_list = page.get_images(full=True)
            
            # Process each image
            for img_index, img_info in enumerate(image_list):
                xref = img_info[0]
                
                # Extract image
                base_image = pdf.extract_image(xref)
                image_bytes = base_image["image"]
                
                # Check image type
                image_ext = base_image["ext"]
                
                # Create temp file to check size
                with tempfile.NamedTemporaryFile(suffix=f".{image_ext}", delete=False) as temp_img:
                    temp_img.write(image_bytes)
                    temp_img_path = temp_img.name
                
                # Open with PIL to check size
                try:
                    with Image.open(temp_img_path) as img:
                        width, height = img.size
                        
                        # Skip small images
                        if width < min_size or height < min_size:
                            os.unlink(temp_img_path)
                            continue
                        
                        # Save to output directory
                        image_name = f"{name_prefix}_p{page_num+1}_i{img_index+1}.{image_ext}"
                        image_path = output_dir / image_name
                        
                        # Copy to destination
                        shutil.copy(temp_img_path, image_path)
                        extracted_paths.append(str(image_path))
                
                finally:
                    # Clean up temp file
                    if os.path.exists(temp_img_path):
                        os.unlink(temp_img_path)
        
        logger.info(f"Extracted {len(extracted_paths)} images from {pdf_path}")
        return extracted_paths
    
    async def convert_pdf_to_kdp_format(
        self,
        pdf_path: Union[str, Path],
        output_path: Optional[Union[str, Path]] = None,
        metadata: Optional[BookMetadata] = None
    ) -> str:
        """
        Convert a PDF exported from Canva to KDP-compatible format.
        
        Args:
            pdf_path: Path to input PDF
            output_path: Path for output PDF
            metadata: Book metadata for sizing
            
        Returns:
            Path to converted PDF
        """
        # Convert to Path objects
        pdf_path = Path(pdf_path)
        
        if not output_path:
            output_path = self.export_dir / f"{pdf_path.stem}_kdp.pdf"
        else:
            output_path = Path(output_path)
        
        # Open PDF
        pdf = fitz.open(pdf_path)
        
        # Create output PDF
        output_pdf = fitz.open()
        
        # Iterate through pages
        for page_num, page in enumerate(pdf):
            # Get page dimensions
            width, height = page.rect.width, page.rect.height
            
            # If we have metadata, adjust dimensions to match KDP specs
            if metadata:
                # TODO: Implement KDP-specific adjustments based on trim size
                pass
            
            # Add page to output PDF
            new_page = output_pdf.new_page(width=width, height=height)
            
            # Copy contents from original page
            new_page.show_pdf_page(new_page.rect, pdf, page_num)
        
        # Save output PDF
        output_pdf.save(output_path)
        
        logger.info(f"Converted PDF to KDP format: {output_path}")
        return str(output_path)


# Create singleton instance
canva_export_manager = CanvaExportManager()
