"""
Book Formatter module for Kids Book Generator.

This module handles the formatting of books according to Amazon KDP specifications,
including page layout, bleed calculations, and PDF generation.
"""
import os
import io
import json
import logging
import tempfile
from typing import Dict, List, Optional, Any, Tuple, Union, BinaryIO
from pathlib import Path
from datetime import datetime
import math
import uuid

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.units import inch, mm, cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image as RLImage, Frame, PageTemplate, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from PIL import Image as PILImage, ImageDraw, ImageFont
from PyPDF2 import PdfWriter, PdfReader
from io import BytesIO

from src.api.models import BookMetadata, BookType, TrimSize, AgeGroup
from src.config import settings
from src.utils.logging import get_logger


logger = get_logger(__name__)


class BookFormatter:
    """
    Book formatting service for KDP-compliant PDFs.
    
    This class handles the creation of print-ready PDFs that meet
    Amazon KDP specifications for trim size, bleeds, margins, and resolution.
    """
    
    def __init__(self):
        """Initialize the book formatter with configuration settings."""
        # Set up output directories
        self.output_dir = Path(settings.STORAGE_DIR) / "books"
        self.cover_dir = Path(settings.STORAGE_DIR) / "covers"
        self.temp_dir = Path(settings.STORAGE_DIR) / "temp"
        
        # Create output directories if they don't exist
        for directory in [self.output_dir, self.cover_dir, self.temp_dir]:
            os.makedirs(directory, exist_ok=True)
        
        # Amazon KDP specifications
        self.specs = {
            "bleed": 0.125,  # inches
            "margins": {
                "outside": 0.25,  # inches
                "inside": 0.375,  # inches
                "top": 0.25,  # inches
                "bottom": 0.25  # inches
            },
            "dpi": 300,  # dots per inch (print quality)
            "trim_sizes": {
                TrimSize.STANDARD: (8.5, 11),   # inches (width, height)
                TrimSize.SQUARE: (8.5, 8.5)     # inches (width, height)
            },
            "min_pages": 24,      # KDP minimum page count
            "max_pages": 800,     # KDP maximum page count
            "page_multiple": 4,   # Pages must be multiple of this number
            "safe_zone": 0.25     # Safe zone inside the trim (no critical content)
        }
        
        # Paper types and their thickness for spine width calculations
        self.paper_types = {
            "white": 0.002252,  # inches per page (white paper)
            "cream": 0.0025    # inches per page (cream paper)
        }
        
        # Initialize fonts
        self._setup_fonts()
        
        # Initialize styles
        self.styles = self._create_styles()
    
    def _setup_fonts(self):
        """Set up fonts for PDF generation."""
        try:
            # Register default fonts (these are built-in with ReportLab)
            pdfmetrics.registerFont(TTFont('Vera', 'Vera.ttf'))
            pdfmetrics.registerFont(TTFont('VeraBd', 'VeraBd.ttf'))
            pdfmetrics.registerFont(TTFont('VeraIt', 'VeraIt.ttf'))
            pdfmetrics.registerFont(TTFont('VeraBI', 'VeraBI.ttf'))
            
            # Font families based on age group
            self.font_families = {
                AgeGroup.TODDLER: {
                    "title": "Vera",
                    "body": "Vera",
                    "caption": "Vera"
                },
                AgeGroup.PRESCHOOL: {
                    "title": "Vera",
                    "body": "Vera",
                    "caption": "Vera"
                },
                AgeGroup.EARLY_READER: {
                    "title": "Vera",
                    "body": "Vera",
                    "caption": "Vera"
                },
                AgeGroup.MIDDLE_GRADE: {
                    "title": "Vera",
                    "body": "Vera",
                    "caption": "Vera"
                }
            }
            
            # Default font family
            self.default_fonts = {
                "title": "Vera",
                "body": "Vera",
                "caption": "Vera"
            }
            
        except Exception as e:
            logger.error(f"Error setting up fonts: {str(e)}")
            # Fall back to basic fonts if TTF fonts are not available
            self.font_families = {age_group: {
                "title": "Helvetica-Bold",
                "body": "Helvetica",
                "caption": "Helvetica-Oblique"
            } for age_group in AgeGroup}
            
            self.default_fonts = {
                "title": "Helvetica-Bold",
                "body": "Helvetica",
                "caption": "Helvetica-Oblique"
            }
    
    def _create_styles(self) -> Dict[str, Dict[str, ParagraphStyle]]:
        """Create paragraph styles for different age groups."""
        base_styles = getSampleStyleSheet()
        
        # Create custom styles
        custom_styles = {}
        
        for age_group in AgeGroup:
            fonts = self.font_families.get(age_group, self.default_fonts)
            
            # Font sizes by age group
            if age_group == AgeGroup.TODDLER:
                title_size = 24
                body_size = 16
                caption_size = 12
            elif age_group == AgeGroup.PRESCHOOL:
                title_size = 22
                body_size = 14
                caption_size = 11
            elif age_group == AgeGroup.EARLY_READER:
                title_size = 20
                body_size = 12
                caption_size = 10
            else:  # MIDDLE_GRADE
                title_size = 18
                body_size = 11
                caption_size = 9
            
            # Create styles
            group_styles = {
                "title": ParagraphStyle(
                    name=f"Title-{age_group.value}",
                    fontName=fonts["title"],
                    fontSize=title_size,
                    leading=title_size * 1.2,
                    alignment=TA_CENTER,
                    spaceAfter=title_size
                ),
                "body": ParagraphStyle(
                    name=f"Body-{age_group.value}",
                    fontName=fonts["body"],
                    fontSize=body_size,
                    leading=body_size * 1.2,
                    alignment=TA_LEFT,
                    spaceAfter=body_size / 2
                ),
                "caption": ParagraphStyle(
                    name=f"Caption-{age_group.value}",
                    fontName=fonts["caption"],
                    fontSize=caption_size,
                    leading=caption_size * 1.2,
                    alignment=TA_CENTER,
                    spaceAfter=caption_size
                )
            }
            
            custom_styles[age_group.value] = group_styles
        
        return custom_styles
    
    def _calculate_dimensions(self, trim_size: TrimSize) -> Dict[str, Any]:
        """
        Calculate dimensions based on trim size and DPI.
        
        Args:
            trim_size: The KDP trim size for the book
            
        Returns:
            Dictionary with width, height, and bleed dimensions in various units
        """
        width_inches, height_inches = self.specs["trim_sizes"][trim_size]
        dpi = self.specs["dpi"]
        bleed_inches = self.specs["bleed"]
        bleed_pixels = int(bleed_inches * dpi)
        safe_zone_inches = self.specs["safe_zone"]
        
        # Calculate dimensions in pixels, inches, and points
        return {
            # Dimensions in pixels (for image processing)
            "width_px": int(width_inches * dpi),
            "height_px": int(height_inches * dpi),
            "bleed_px": bleed_pixels,
            "width_with_bleed_px": int((width_inches + 2 * bleed_inches) * dpi),
            "height_with_bleed_px": int((height_inches + 2 * bleed_inches) * dpi),
            
            # Dimensions in inches (for reference)
            "width_in": width_inches,
            "height_in": height_inches,
            "bleed_in": bleed_inches,
            "width_with_bleed_in": width_inches + 2 * bleed_inches,
            "height_with_bleed_in": height_inches + 2 * bleed_inches,
            "safe_zone_in": safe_zone_inches,
            
            # Dimensions in points (for ReportLab)
            "width_pt": width_inches * 72,  # 72 points per inch
            "height_pt": height_inches * 72,
            "bleed_pt": bleed_inches * 72,
            "width_with_bleed_pt": (width_inches + 2 * bleed_inches) * 72,
            "height_with_bleed_pt": (height_inches + 2 * bleed_inches) * 72,
            "safe_zone_pt": safe_zone_inches * 72,
            
            # Margins in points (for ReportLab)
            "margin_top_pt": self.specs["margins"]["top"] * 72,
            "margin_bottom_pt": self.specs["margins"]["bottom"] * 72,
            "margin_inside_pt": self.specs["margins"]["inside"] * 72,
            "margin_outside_pt": self.specs["margins"]["outside"] * 72
        }
    
    def _calculate_spine_width(self, page_count: int, paper_type: str = "white") -> float:
        """
        Calculate spine width based on page count and paper type.
        
        Args:
            page_count: Number of pages in the book
            paper_type: Paper type (white or cream)
            
        Returns:
            Spine width in inches
        """
        # Ensure page count is divisible by 4 (KDP requirement)
        page_count = math.ceil(page_count / self.specs["page_multiple"]) * self.specs["page_multiple"]
        
        # Get thickness per page from paper type
        thickness_per_page = self.paper_types.get(paper_type.lower(), self.paper_types["white"])
        
        # Calculate spine width
        return page_count * thickness_per_page
    
    def _resize_image_for_page(self, image_path: str, dimensions: Dict[str, Any], 
                             with_bleed: bool = True) -> PILImage.Image:
        """
        Resize an image to fit the page dimensions with proper bleed areas.
        
        Args:
            image_path: Path to the image file
            dimensions: Dictionary of dimensions from _calculate_dimensions
            with_bleed: Whether to include bleed area
            
        Returns:
            Resized PIL Image
        """
        try:
            # Open image
            img = PILImage.open(image_path)
            
            # Determine target size
            if with_bleed:
                target_width = dimensions["width_with_bleed_px"]
                target_height = dimensions["height_with_bleed_px"]
            else:
                target_width = dimensions["width_px"]
                target_height = dimensions["height_px"]
            
            # Calculate aspect ratios
            img_aspect = img.width / img.height
            target_aspect = target_width / target_height
            
            # Resize and crop to maintain aspect ratio and fill the target size
            if img_aspect > target_aspect:  # Image is wider
                new_height = target_height
                new_width = int(new_height * img_aspect)
                img = img.resize((new_width, new_height), PILImage.LANCZOS)
                # Crop from center
                left = (new_width - target_width) // 2
                img = img.crop((left, 0, left + target_width, target_height))
            else:  # Image is taller
                new_width = target_width
                new_height = int(new_width / img_aspect)
                img = img.resize((new_width, new_height), PILImage.LANCZOS)
                # Crop from center
                top = (new_height - target_height) // 2
                img = img.crop((0, top, target_width, top + target_height))
            
            return img
        except Exception as e:
            logger.error(f"Error resizing image {image_path}: {str(e)}")
            # Create a blank image if the source can't be processed
            return PILImage.new('RGB', (target_width, target_height), color='white')
    
    def _create_story_pdf(self, metadata: BookMetadata, content: Dict[str, Any], 
                        images: List[str], output_path: str) -> str:
        """
        Create a story book PDF with text and illustrations.
        
        Args:
            metadata: Book metadata
            content: Book content including chapters
            images: List of paths to illustrations
            output_path: Path to save the PDF
            
        Returns:
            Path to the generated PDF
        """
        logger.info(f"Creating story book PDF: {metadata.title}")
        
        # Get dimensions
        dimensions = self._calculate_dimensions(metadata.trim_size)
        
        # Get styles for the age group
        age_group = metadata.age_group.value
        styles = self.styles.get(age_group, self.styles.get(AgeGroup.PRESCHOOL.value))
        
        # Create PDF document
        doc = SimpleDocTemplate(
            output_path,
            pagesize=(dimensions["width_with_bleed_pt"], dimensions["height_with_bleed_pt"]),
            leftMargin=dimensions["margin_inside_pt"] + dimensions["bleed_pt"],
            rightMargin=dimensions["margin_outside_pt"] + dimensions["bleed_pt"],
            topMargin=dimensions["margin_top_pt"] + dimensions["bleed_pt"],
            bottomMargin=dimensions["margin_bottom_pt"] + dimensions["bleed_pt"]
        )
        
        # Story elements
        story = []
        
        # Add title page
        story.append(Paragraph(metadata.title, styles["title"]))
        story.append(Paragraph(f"By {metadata.author}", styles["caption"]))
        story.append(PageBreak())
        
        # Add chapters
        chapters = content.get("chapters", [])
        for i, chapter in enumerate(chapters):
            # Add chapter title
            story.append(Paragraph(chapter.get("title", f"Chapter {i+1}"), styles["title"]))
            
            # Add chapter content
            text = chapter.get("content", "")
            paragraphs = text.split('\n\n')  # Split by double newline
            for para in paragraphs:
                if para.strip():
                    story.append(Paragraph(para.replace('\n', '<br/>'), styles["body"]))
            
            # Add illustration if available
            if i < len(images):
                try:
                    # Resize image to fit page with margins
                    # We'll use a width that fits within the content area
                    content_width = dimensions["width_pt"] - dimensions["margin_inside_pt"] - dimensions["margin_outside_pt"]
                    img = RLImage(images[i], width=content_width * 0.8)  # 80% of content width
                    story.append(Spacer(1, 12))
                    story.append(img)
                    
                    # Add illustration caption if available
                    if "illustration_prompt" in chapter:
                        caption = chapter["illustration_prompt"]
                        if len(caption) > 100:  # Truncate long captions
                            caption = caption[:97] + "..."
                        story.append(Paragraph(caption, styles["caption"]))
                except Exception as e:
                    logger.error(f"Error adding image {images[i]}: {str(e)}")
            
            # Add page break between chapters
            story.append(PageBreak())
        
        # Build PDF
        doc.build(story)
        
        return output_path
    
    def _create_coloring_pdf(self, metadata: BookMetadata, images: List[str], output_path: str) -> str:
        """
        Create a coloring book PDF with line art images.
        
        Args:
            metadata: Book metadata
            images: List of paths to coloring page images
            output_path: Path to save the PDF
            
        Returns:
            Path to the generated PDF
        """
        logger.info(f"Creating coloring book PDF: {metadata.title}")
        
        # Get dimensions
        dimensions = self._calculate_dimensions(metadata.trim_size)
        
        # Get styles for the age group
        age_group = metadata.age_group.value
        styles = self.styles.get(age_group, self.styles.get(AgeGroup.PRESCHOOL.value))
        
        # Create PDF document
        doc = SimpleDocTemplate(
            output_path,
            pagesize=(dimensions["width_with_bleed_pt"], dimensions["height_with_bleed_pt"]),
            leftMargin=dimensions["margin_inside_pt"] + dimensions["bleed_pt"],
            rightMargin=dimensions["margin_outside_pt"] + dimensions["bleed_pt"],
            topMargin=dimensions["margin_top_pt"] + dimensions["bleed_pt"],
            bottomMargin=dimensions["margin_bottom_pt"] + dimensions["bleed_pt"]
        )
        
        # Story elements
        story = []
        
        # Add title page
        story.append(Paragraph(metadata.title, styles["title"]))
        story.append(Paragraph(f"By {metadata.author}", styles["caption"]))
        story.append(PageBreak())
        
        # Add coloring pages
        for i, img_path in enumerate(images):
            try:
                # Calculate content width (accounting for margins)
                content_width = dimensions["width_pt"] - dimensions["margin_inside_pt"] - dimensions["margin_outside_pt"]
                
                # Add the coloring page image
                img = RLImage(img_path, width=content_width * 0.9)  # 90% of content width
                story.append(img)
                story.append(PageBreak())
            except Exception as e:
                logger.error(f"Error adding coloring page {img_path}: {str(e)}")
                # Add blank page with error message
                story.append(Paragraph(f"Coloring page {i+1} could not be loaded", styles["body"]))
                story.append(PageBreak())
        
        # Build PDF
        doc.build(story)
        
        return output_path
    
    async def format_book(self, metadata: BookMetadata, content: Dict[str, Any], images: List[str], 
                        template_id: Optional[str] = None,
                        cover_image: Optional[str] = None,
                        cover_style: str = "simple") -> str:
        """
        Format a complete book as a print-ready PDF.
        
        Args:
            metadata: Book metadata including title, author, trim size, etc.
            content: Book content including text and chapter information
            images: List of paths to illustrations
            template_id: Optional template ID to use for formatting
            cover_image: Optional path to cover image
            cover_style: Cover style to use (simple, gradient, photo)
            
        Returns:
            Path to the generated PDF file
        """
        logger.info(f"Formatting book: {metadata.title}")
        
        # Create a safe filename
        safe_filename = "".join(c if c.isalnum() or c in "_- " else "_" for c in metadata.title.lower())
        safe_filename = safe_filename.replace(" ", "_")
        
        # Determine output path
        output_path = str(self.output_dir / f"{safe_filename}.pdf")
        
        # Import the template manager and cover generator here to avoid circular imports
        from src.formatters.template_manager import template_manager
        from src.formatters.cover_generator import cover_generator
        
        # Apply template to content if template_id is provided
        if template_id:
            template = template_manager.get_template(template_id)
            if template:
                content = template_manager.apply_template_properties(content, template)
            else:
                logger.warning(f"Template {template_id} not found, using default formatting")
        
        # Generate the book cover
        cover_path = await cover_generator.generate_cover(
            metadata=metadata,
            cover_image=cover_image,
            style=cover_style
        )
        logger.info(f"Generated cover: {cover_path}")
        
        # Create PDF based on book type
        if metadata.book_type == BookType.COLORING:
            book_pdf = await self._create_coloring_pdf_async(metadata, images, output_path)
        else:  # STORY and other types
            book_pdf = await self._create_story_pdf_async(metadata, content, images, output_path)
        
        # Combine book PDF with cover PDF if needed for print-ready PDF
        try:
            logger.info(f"Book PDF created at {book_pdf}, combining with cover...")
            final_pdf_path = str(self.output_dir / f"{safe_filename}_print_ready.pdf")
            
            # Combine PDFs
            output = PdfWriter()
            
            # Add cover page
            cover_reader = PdfReader(cover_path)
            output.add_page(cover_reader.pages[0])
            
            # Add book pages
            book_reader = PdfReader(book_pdf)
            for page in book_reader.pages:
                output.add_page(page)
            
            # Write the combined PDF
            with open(final_pdf_path, 'wb') as f:
                output.write(f)
            
            logger.info(f"Print-ready PDF created: {final_pdf_path}")
            return final_pdf_path
        except Exception as e:
            logger.error(f"Error creating print-ready PDF: {str(e)}")
            # Return book PDF if combining failed
            return book_pdf
    
    async def _create_story_pdf_async(self, metadata: BookMetadata, content: Dict[str, Any], 
                                    images: List[str], output_path: str) -> str:
        """Async wrapper for _create_story_pdf."""
        # Apply template-specific formatting if available in the content
        if "template" in content and "properties" in content["template"]:
            template_props = content["template"]["properties"]
            # Apply template-specific formatting (could modify the generation process)
            logger.info(f"Applying template {content['template'].get('name')} for story book generation")
            
            # Here we could customize the PDF creation based on template properties
            # For example, adjusting font styles, layout, etc.
        
        return self._create_story_pdf(metadata, content, images, output_path)
    
    async def _create_coloring_pdf_async(self, metadata: BookMetadata, images: List[str], output_path: str) -> str:
        """Async wrapper for _create_coloring_pdf."""
        # Import template manager here to avoid circular imports
        from src.formatters.template_manager import template_manager
        
        # Get appropriate template for coloring book if not already specified
        if "formatting" not in metadata.additional_metadata:
            # Find the default template for coloring books
            template = template_manager.get_default_template(BookType.COLORING, metadata.age_group.value)
            if template:
                # Apply template settings to metadata
                metadata.additional_metadata["formatting"] = template.properties
                logger.info(f"Applied default coloring book template: {template.name}")
        
        return self._create_coloring_pdf(metadata, images, output_path)


# Create a singleton instance for use in the application
book_formatter = BookFormatter()
