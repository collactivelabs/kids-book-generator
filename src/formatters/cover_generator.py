"""
Cover Generator module for Kids Book Generator.

This module handles the generation of KDP-compliant book covers,
including front, back, and spine calculations.
"""
import os
import io
import logging
from typing import Dict, List, Optional, Any, Tuple, Union
from pathlib import Path
from datetime import datetime
import uuid
import math

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch, mm
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from PIL import Image as PILImage, ImageDraw, ImageFont
from io import BytesIO

from src.api.models import BookMetadata, BookType, TrimSize
from src.config import settings
from src.utils.logging import get_logger
# Import deferred to avoid circular imports
# We'll import BookFormatter only when needed


logger = get_logger(__name__)


class CoverGenerator:
    """
    Cover generation service for KDP-compliant book covers.
    
    This class handles the creation of print-ready wraparound covers
    with front cover, spine, and back cover, including proper bleeds
    and safe zones.
    """
    
    def __init__(self, book_formatter = None):
        """
        Initialize the cover generator.
        
        Args:
            book_formatter: Optional BookFormatter instance for shared calculations
        """
        # Set up output directory
        self.output_dir = Path(settings.STORAGE_DIR) / "covers"
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Store book_formatter reference - will be set later if None
        # to avoid circular imports
        self.book_formatter = book_formatter
        
        # Cover design templates
        self.templates = {
            "simple": self._create_simple_cover,
            "gradient": self._create_gradient_cover,
            "photo": self._create_photo_cover
        }
        
        # Default colors for covers (can be customized)
        self.color_schemes = {
            "children": [
                {"primary": colors.HexColor("#FF9900"), "secondary": colors.HexColor("#FFCC00")},  # Orange/Yellow
                {"primary": colors.HexColor("#66CCFF"), "secondary": colors.HexColor("#3399FF")},  # Light/Dark Blue
                {"primary": colors.HexColor("#FF6699"), "secondary": colors.HexColor("#FF99CC")},  # Dark/Light Pink
                {"primary": colors.HexColor("#99CC33"), "secondary": colors.HexColor("#CCFF66")},  # Dark/Light Green
                {"primary": colors.HexColor("#9966CC"), "secondary": colors.HexColor("#CC99FF")}   # Purple/Lavender
            ],
            "fantasy": [
                {"primary": colors.HexColor("#4B0082"), "secondary": colors.HexColor("#9370DB")},  # Indigo/Medium Purple
                {"primary": colors.HexColor("#191970"), "secondary": colors.HexColor("#4169E1")},  # Midnight/Royal Blue
                {"primary": colors.HexColor("#006400"), "secondary": colors.HexColor("#32CD32")},  # Dark/Lime Green
                {"primary": colors.HexColor("#8B0000"), "secondary": colors.HexColor("#DC143C")},  # Dark/Crimson Red
                {"primary": colors.HexColor("#4B0082"), "secondary": colors.HexColor("#800080")}   # Indigo/Purple
            ],
            "educational": [
                {"primary": colors.HexColor("#1E90FF"), "secondary": colors.HexColor("#ADD8E6")},  # Dodger/Light Blue
                {"primary": colors.HexColor("#2E8B57"), "secondary": colors.HexColor("#90EE90")},  # Sea/Light Green
                {"primary": colors.HexColor("#FF8C00"), "secondary": colors.HexColor("#FFDAB9")},  # Dark Orange/Peach
                {"primary": colors.HexColor("#4682B4"), "secondary": colors.HexColor("#B0C4DE")},  # Steel/Light Steel Blue
                {"primary": colors.HexColor("#CD853F"), "secondary": colors.HexColor("#F5DEB3")}   # Peru/Wheat
            ]
        }
    
    def _get_color_scheme(self, theme: str) -> Dict[str, Any]:
        """Get a color scheme based on book theme."""
        if theme.lower() in self.color_schemes:
            schemes = self.color_schemes[theme.lower()]
            return schemes[hash(theme) % len(schemes)]
        
        # Default to children's color scheme
        schemes = self.color_schemes["children"]
        return schemes[0]
    
    def _calculate_cover_dimensions(self, metadata: BookMetadata) -> Dict[str, Any]:
        """
        Calculate dimensions for a KDP-compliant cover.
        
        Args:
            metadata: Book metadata
            
        Returns:
            Dictionary with cover dimensions
        """
        # Check if book_formatter is set, if not, import it now
        if self.book_formatter is None:
            # Import here to avoid circular import
            from src.formatters.book_formatter import book_formatter
            self.book_formatter = book_formatter
        
        # Get book dimensions
        book_dims = self.book_formatter._calculate_dimensions(metadata.trim_size)
        
        # Calculate spine width
        spine_width_in = self.book_formatter._calculate_spine_width(
            metadata.page_count, 
            paper_type="white"  # Default to white paper
        )
        spine_width_pt = spine_width_in * 72  # Convert to points
        
        # Calculate full cover dimensions (front + spine + back) with bleed
        width_with_spine_pt = (book_dims["width_pt"] * 2) + spine_width_pt
        width_with_spine_bleed_pt = width_with_spine_pt + (book_dims["bleed_pt"] * 2)
        height_with_bleed_pt = book_dims["height_with_bleed_pt"]
        
        # Return all dimensions
        return {
            **book_dims,  # Include all book dimensions
            "spine_width_in": spine_width_in,
            "spine_width_pt": spine_width_pt,
            "width_with_spine_pt": width_with_spine_pt,
            "width_with_spine_bleed_pt": width_with_spine_bleed_pt,
            "full_width_pt": width_with_spine_bleed_pt,
            "full_height_pt": height_with_bleed_pt
        }
    
    def _create_simple_cover(self, canvas_obj: canvas.Canvas, metadata: BookMetadata, 
                           dimensions: Dict[str, Any], cover_image: Optional[str] = None) -> None:
        """
        Create a simple cover with solid colors and text.
        
        Args:
            canvas_obj: ReportLab canvas object
            metadata: Book metadata
            dimensions: Cover dimensions
            cover_image: Optional path to cover image
        """
        # Get color scheme based on theme
        colors_scheme = self._get_color_scheme(metadata.theme)
        primary_color = colors_scheme["primary"]
        secondary_color = colors_scheme["secondary"]
        
        # Calculate key positions
        full_width = dimensions["full_width_pt"]
        full_height = dimensions["full_height_pt"]
        spine_width = dimensions["spine_width_pt"]
        bleed = dimensions["bleed_pt"]
        
        # Front cover area
        front_x = bleed + dimensions["width_pt"] + spine_width
        front_y = bleed
        front_width = dimensions["width_pt"]
        front_height = dimensions["height_pt"]
        
        # Back cover area
        back_x = bleed
        back_y = bleed
        back_width = dimensions["width_pt"]
        back_height = dimensions["height_pt"]
        
        # Spine area
        spine_x = bleed + dimensions["width_pt"]
        spine_y = bleed
        spine_height = dimensions["height_pt"]
        
        # Draw red bleed indicator lines (for debugging)
        if settings.DEBUG:
            canvas_obj.setStrokeColor(colors.red)
            canvas_obj.setDash(1, 2)
            # Outer bleed line
            canvas_obj.rect(0, 0, full_width, full_height)
            # Trim line
            canvas_obj.rect(bleed, bleed, full_width - 2*bleed, full_height - 2*bleed)
            canvas_obj.setDash(1, 0)  # Reset dash pattern
        
        # Draw back cover (left side)
        canvas_obj.setFillColor(secondary_color)
        canvas_obj.rect(back_x, back_y, back_width, back_height, fill=1, stroke=0)
        
        # Draw spine
        canvas_obj.setFillColor(primary_color)
        canvas_obj.rect(spine_x, spine_y, spine_width, spine_height, fill=1, stroke=0)
        
        # Draw front cover (right side)
        if cover_image and os.path.exists(cover_image):
            # Use the provided image for the front cover
            try:
                img = PILImage.open(cover_image)
                # Resize to cover the front cover area
                img_width, img_height = img.size
                img_aspect = img_width / img_height
                target_aspect = front_width / front_height
                
                if img_aspect > target_aspect:  # Image is wider
                    new_height = front_height
                    new_width = int(new_height * img_aspect)
                    left = int((new_width - front_width) / 2)
                    img = img.resize((new_width, int(new_height)), PILImage.LANCZOS)
                    img = img.crop((left, 0, left + int(front_width), int(front_height)))
                else:  # Image is taller
                    new_width = front_width
                    new_height = int(new_width / img_aspect)
                    top = int((new_height - front_height) / 2)
                    img = img.resize((int(new_width), new_height), PILImage.LANCZOS)
                    img = img.crop((0, top, int(front_width), top + int(front_height)))
                
                # Create temporary file for the resized image
                img_byte_arr = BytesIO()
                img.save(img_byte_arr, format='PNG')
                img_byte_arr.seek(0)
                
                # Draw image on canvas
                canvas_obj.drawImage(
                    ImageReader(img_byte_arr), 
                    front_x, front_y, 
                    width=front_width, 
                    height=front_height, 
                    mask='auto'
                )
            except Exception as e:
                logger.error(f"Error using cover image {cover_image}: {str(e)}")
                # Fall back to solid color if image fails
                canvas_obj.setFillColor(primary_color)
                canvas_obj.rect(front_x, front_y, front_width, front_height, fill=1, stroke=0)
        else:
            # Use solid color for front cover
            canvas_obj.setFillColor(primary_color)
            canvas_obj.rect(front_x, front_y, front_width, front_height, fill=1, stroke=0)
        
        # Add title to front cover
        canvas_obj.setFont("Helvetica-Bold", 24)
        canvas_obj.setFillColor(colors.white)
        title_x = front_x + (front_width / 2)
        title_y = front_y + (front_height / 2)
        canvas_obj.drawCentredString(title_x, title_y, metadata.title)
        
        # Add author to front cover
        canvas_obj.setFont("Helvetica", 16)
        author_y = title_y - 36
        canvas_obj.drawCentredString(title_x, author_y, f"By {metadata.author}")
        
        # Add spine text (rotated 90 degrees)
        canvas_obj.saveState()
        canvas_obj.translate(spine_x + (spine_width / 2), spine_y + (spine_height / 2))
        canvas_obj.rotate(90)
        canvas_obj.setFont("Helvetica-Bold", 12 if spine_width > 72 else 9)  # Adjust font size based on spine width
        canvas_obj.setFillColor(colors.white)
        canvas_obj.drawCentredString(0, 0, metadata.title)
        canvas_obj.restoreState()
        
        # Add barcode placeholder to back cover
        barcode_x = back_x + 72
        barcode_y = back_y + 72
        canvas_obj.setFillColor(colors.white)
        canvas_obj.rect(barcode_x, barcode_y, 144, 72, fill=1, stroke=1)
        canvas_obj.setFillColor(colors.black)
        canvas_obj.setFont("Helvetica", 8)
        canvas_obj.drawCentredString(barcode_x + 72, barcode_y + 36, "Barcode Placeholder")
    
    def _create_gradient_cover(self, canvas_obj: canvas.Canvas, metadata: BookMetadata, 
                             dimensions: Dict[str, Any], cover_image: Optional[str] = None) -> None:
        """
        Create a cover with gradient background.
        
        Args:
            canvas_obj: ReportLab canvas object
            metadata: Book metadata
            dimensions: Cover dimensions
            cover_image: Optional path to cover image
        """
        # This is a simplified version - for a real gradient, you would need to use
        # more complex drawing techniques or pre-generate a gradient image
        
        # Get color scheme based on theme
        colors_scheme = self._get_color_scheme(metadata.theme)
        primary_color = colors_scheme["primary"]
        secondary_color = colors_scheme["secondary"]
        
        # Calculate key positions
        full_width = dimensions["full_width_pt"]
        full_height = dimensions["full_height_pt"]
        spine_width = dimensions["spine_width_pt"]
        bleed = dimensions["bleed_pt"]
        
        # Front cover area
        front_x = bleed + dimensions["width_pt"] + spine_width
        front_y = bleed
        front_width = dimensions["width_pt"]
        front_height = dimensions["height_pt"]
        
        # Back cover area
        back_x = bleed
        back_y = bleed
        back_width = dimensions["width_pt"]
        back_height = dimensions["height_pt"]
        
        # Spine area
        spine_x = bleed + dimensions["width_pt"]
        spine_y = bleed
        spine_height = dimensions["height_pt"]
        
        # Draw background for entire cover (simplified gradient effect)
        steps = 20
        for i in range(steps):
            ratio = i / (steps - 1)
            # Interpolate between colors
            r = primary_color.red + (secondary_color.red - primary_color.red) * ratio
            g = primary_color.green + (secondary_color.green - primary_color.green) * ratio
            b = primary_color.blue + (secondary_color.blue - primary_color.blue) * ratio
            
            canvas_obj.setFillColor(colors.Color(r, g, b))
            
            # Draw a stripe
            start_y = bleed + (ratio * dimensions["height_pt"])
            height = dimensions["height_pt"] / steps
            canvas_obj.rect(bleed, start_y, dimensions["width_with_spine_pt"], height, fill=1, stroke=0)
        
        # Rest of the cover elements (similar to simple cover)
        # ...abbreviated for this implementation
        
        # Add title to front cover
        canvas_obj.setFont("Helvetica-Bold", 24)
        canvas_obj.setFillColor(colors.white)
        title_x = front_x + (front_width / 2)
        title_y = front_y + (front_height / 2)
        canvas_obj.drawCentredString(title_x, title_y, metadata.title)
        
        # Add author to front cover
        canvas_obj.setFont("Helvetica", 16)
        author_y = title_y - 36
        canvas_obj.drawCentredString(title_x, author_y, f"By {metadata.author}")
        
        # Add spine text (rotated 90 degrees)
        canvas_obj.saveState()
        canvas_obj.translate(spine_x + (spine_width / 2), spine_y + (spine_height / 2))
        canvas_obj.rotate(90)
        canvas_obj.setFont("Helvetica-Bold", 12 if spine_width > 72 else 9)
        canvas_obj.setFillColor(colors.white)
        canvas_obj.drawCentredString(0, 0, metadata.title)
        canvas_obj.restoreState()
    
    def _create_photo_cover(self, canvas_obj: canvas.Canvas, metadata: BookMetadata, 
                          dimensions: Dict[str, Any], cover_image: Optional[str] = None) -> None:
        """
        Create a cover using the cover image as full background.
        
        Args:
            canvas_obj: ReportLab canvas object
            metadata: Book metadata
            dimensions: Cover dimensions
            cover_image: Path to cover image
        """
        # Calculate key positions
        full_width = dimensions["full_width_pt"]
        full_height = dimensions["full_height_pt"]
        spine_width = dimensions["spine_width_pt"]
        bleed = dimensions["bleed_pt"]
        
        # Front cover area
        front_x = bleed + dimensions["width_pt"] + spine_width
        front_y = bleed
        front_width = dimensions["width_pt"]
        front_height = dimensions["height_pt"]
        
        # If no cover image provided, create a simple cover instead
        if not cover_image or not os.path.exists(cover_image):
            logger.warning("No cover image provided for photo cover style. Using simple style instead.")
            return self._create_simple_cover(canvas_obj, metadata, dimensions)
        
        try:
            # Load and resize image for full cover
            img = PILImage.open(cover_image)
            
            # Create a dark overlay for text readability
            overlay = PILImage.new('RGBA', img.size, (0, 0, 0, 0))
            draw = ImageDraw.Draw(overlay)
            
            # Draw the resized image on canvas
            canvas_obj.drawImage(
                cover_image, 
                bleed, bleed, 
                width=dimensions["width_with_spine_pt"], 
                height=dimensions["height_pt"], 
                mask='auto'
            )
            
            # Add title to front cover with shadow for readability
            canvas_obj.setFillColor(colors.black)
            title_x = front_x + (front_width / 2)
            title_y = front_y + (front_height / 2)
            
            # Draw title shadow
            canvas_obj.setFont("Helvetica-Bold", 24)
            canvas_obj.drawCentredString(title_x + 2, title_y - 2, metadata.title)
            
            # Draw title
            canvas_obj.setFillColor(colors.white)
            canvas_obj.drawCentredString(title_x, title_y, metadata.title)
            
            # Add author with shadow
            canvas_obj.setFont("Helvetica", 16)
            author_y = title_y - 36
            
            # Author shadow
            canvas_obj.setFillColor(colors.black)
            canvas_obj.drawCentredString(title_x + 2, author_y - 2, f"By {metadata.author}")
            
            # Author text
            canvas_obj.setFillColor(colors.white)
            canvas_obj.drawCentredString(title_x, author_y, f"By {metadata.author}")
            
            # Add spine text with background for readability
            spine_x = bleed + dimensions["width_pt"]
            spine_y = bleed
            
            # Add semi-transparent background for spine text
            canvas_obj.setFillColor(colors.Color(0, 0, 0, 0.5))
            canvas_obj.rect(spine_x, spine_y, spine_width, dimensions["height_pt"], fill=1, stroke=0)
            
            # Add spine text
            canvas_obj.saveState()
            canvas_obj.translate(spine_x + (spine_width / 2), spine_y + (spine_height / 2))
            canvas_obj.rotate(90)
            canvas_obj.setFont("Helvetica-Bold", 12 if spine_width > 72 else 9)
            canvas_obj.setFillColor(colors.white)
            canvas_obj.drawCentredString(0, 0, metadata.title)
            canvas_obj.restoreState()
            
        except Exception as e:
            logger.error(f"Error creating photo cover: {str(e)}")
            # Fall back to simple cover
            return self._create_simple_cover(canvas_obj, metadata, dimensions)
    
    async def generate_cover(self, metadata: BookMetadata, 
                           cover_image: Optional[str] = None, 
                           style: str = "simple") -> str:
        """
        Generate a KDP-compliant book cover.
        
        Args:
            metadata: Book metadata
            cover_image: Optional path to cover image
            style: Cover style to use
            
        Returns:
            Path to the generated cover PDF
        """
        logger.info(f"Generating {style} cover for book: {metadata.title}")
        
        # Calculate cover dimensions
        dimensions = self._calculate_cover_dimensions(metadata)
        
        # Create a safe filename
        safe_filename = "".join(c if c.isalnum() or c in "_- " else "_" for c in metadata.title.lower())
        safe_filename = safe_filename.replace(" ", "_")
        
        # Determine output path
        output_path = str(self.output_dir / f"{safe_filename}_cover.pdf")
        
        # Create a canvas
        c = canvas.Canvas(
            output_path,
            pagesize=(dimensions["full_width_pt"], dimensions["full_height_pt"])
        )
        
        # Select template function
        template_func = self.templates.get(style.lower(), self.templates["simple"])
        
        # Create the cover using the selected template
        template_func(c, metadata, dimensions, cover_image)
        
        # Save the PDF
        c.save()
        
        logger.info(f"Cover generated successfully: {output_path}")
        return output_path


# Add missing ImageReader import for reportlab
from reportlab.lib.utils import ImageReader

# Create a singleton instance for use in the application
# Use a lazy import to avoid circular references
from src.formatters.book_formatter import book_formatter as bf
cover_generator = CoverGenerator(None)  # Initialize without book_formatter

# Set book_formatter after initialization to avoid circular imports
from src.formatters.book_formatter import book_formatter
cover_generator.book_formatter = book_formatter
