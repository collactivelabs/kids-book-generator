"""
Tests for book formatting functionality.

This module tests the book formatter, cover generator, and template system.
"""
import os
import pytest
import asyncio
from pathlib import Path
import shutil
import tempfile
from typing import Dict, List, Any

# Import models first which don't depend on any formatters
from src.api.models import BookMetadata, BookType, TrimSize, AgeGroup

# Import templates, formatters, and cover generators in the right order
# to avoid circular imports
from src.formatters.template_manager import template_manager
from src.formatters.book_formatter import book_formatter
from src.formatters.cover_generator import cover_generator


@pytest.fixture
def sample_metadata() -> BookMetadata:
    """Sample book metadata for testing."""
    return BookMetadata(
        title="Test Children's Book",
        author="Test Author",
        description="A test book for children",
        book_type=BookType.STORY,
        age_group=AgeGroup.PRESCHOOL,
        trim_size=TrimSize.STANDARD,
        page_count=24,
        language="en",
        theme="adventure",
        additional_metadata={}
    )


@pytest.fixture
def sample_content() -> Dict[str, Any]:
    """Sample book content for testing."""
    return {
        "title": "Test Children's Book",
        "chapters": [
            {
                "title": "Chapter 1: The Beginning",
                "pages": [
                    {
                        "number": 1,
                        "text": "Once upon a time, there was a brave little rabbit named Hoppy.",
                        "image_prompt": "A small white rabbit sitting in a green meadow"
                    },
                    {
                        "number": 2,
                        "text": "Hoppy lived in a cozy burrow at the edge of the forest.",
                        "image_prompt": "A rabbit burrow at the edge of a forest with a small entrance"
                    }
                ]
            },
            {
                "title": "Chapter 2: The Adventure",
                "pages": [
                    {
                        "number": 3,
                        "text": "One day, Hoppy decided to explore the deep forest.",
                        "image_prompt": "A rabbit looking at a dark forest path with curiosity"
                    },
                    {
                        "number": 4,
                        "text": "In the forest, Hoppy met a wise old owl named Oliver.",
                        "image_prompt": "A rabbit looking up at an owl perched on a branch"
                    }
                ]
            }
        ]
    }


@pytest.fixture
def sample_images(tmp_path) -> List[str]:
    """Create sample images for testing."""
    from PIL import Image, ImageDraw, ImageFont
    
    # Create a directory for test images
    img_dir = tmp_path / "test_images"
    img_dir.mkdir(exist_ok=True)
    
    # Create 4 simple test images
    image_paths = []
    for i in range(4):
        # Create a colored image with some text - using smaller size to avoid layout issues
        img = Image.new('RGB', (600, 600), color=(255, 255, 255))
        draw = ImageDraw.Draw(img)
        
        # Draw a colored rectangle
        draw.rectangle(
            [(50, 50), (550, 550)],
            fill=(200, 200, 200),
            outline=(0, 0, 0),
            width=5
        )
        
        # Add text
        try:
            font = ImageFont.truetype("Arial", 40)
        except IOError:
            # Use default font if Arial is not available
            font = ImageFont.load_default()
        
        draw.text(
            (300, 300),
            f"Test Image {i+1}",
            fill=(0, 0, 0),
            font=font,
            anchor="mm"
        )
        
        # Save the image
        image_path = str(img_dir / f"test_image_{i+1}.png")
        img.save(image_path)
        image_paths.append(image_path)
    
    return image_paths


@pytest.fixture
def output_dir(tmp_path) -> Path:
    """Create and return a temporary output directory."""
    output_dir = tmp_path / "output"
    output_dir.mkdir(exist_ok=True)
    return output_dir


@pytest.mark.asyncio
async def test_cover_generator(sample_metadata, output_dir):
    """Test cover generation functionality."""
    # Generate a basic cover
    cover_path = await cover_generator.generate_cover(
        metadata=sample_metadata,
        style="simple"
    )
    
    # Check if the cover was created
    assert os.path.exists(cover_path)
    assert cover_path.endswith(".pdf")
    
    # Test with different styles
    for style in ["gradient", "photo"]:
        style_cover_path = await cover_generator.generate_cover(
            metadata=sample_metadata,
            style=style
        )
        assert os.path.exists(style_cover_path)


@pytest.mark.asyncio
async def test_template_system():
    """Test template system functionality."""
    # Check if default templates were created
    story_templates = template_manager.find_templates(BookType.STORY)
    coloring_templates = template_manager.find_templates(BookType.COLORING)
    
    assert len(story_templates) > 0
    assert len(coloring_templates) > 0
    
    # Test applying a template to content
    template = template_manager.get_default_template(BookType.STORY)
    sample_content = {"title": "Test Book", "chapters": []}
    
    formatted_content = template_manager.apply_template_properties(
        sample_content, template
    )
    
    # Verify the template was applied
    assert "template" in formatted_content
    assert formatted_content["template"]["id"] == template.template_id


@pytest.mark.asyncio
async def test_book_formatter(sample_metadata, sample_content, sample_images, output_dir):
    """Test the book formatting process."""
    # Format a book
    pdf_path = await book_formatter.format_book(
        metadata=sample_metadata,
        content=sample_content,
        images=sample_images
    )
    
    # Check if the PDF was created
    assert os.path.exists(pdf_path)
    assert pdf_path.endswith(".pdf")


@pytest.mark.asyncio
async def test_integrated_book_creation(sample_metadata, sample_content, sample_images, output_dir):
    """Test the integrated book creation process with templates and covers."""
    # Get a template
    template = template_manager.get_default_template(BookType.STORY)
    
    # Format a book with template and cover
    pdf_path = await book_formatter.format_book(
        metadata=sample_metadata,
        content=sample_content,
        images=sample_images,
        template_id=template.template_id,
        cover_style="gradient"
    )
    
    # Check if the print-ready PDF was created
    assert os.path.exists(pdf_path)
    assert "_print_ready.pdf" in pdf_path


if __name__ == "__main__":
    # This allows running the tests directly from this file
    pytest.main(["-xvs", __file__])
