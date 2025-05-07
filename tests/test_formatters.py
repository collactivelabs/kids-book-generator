"""
Tests for the book formatting functionality.

This module contains tests for PDF formatting and KDP compliance services.
"""
import pytest
from pathlib import Path

from src.api.models import BookMetadata, BookType, TrimSize, AgeGroup
from src.formatters.book_formatter import BookFormatter


@pytest.fixture
def book_formatter():
    """
    Create a book formatter instance for testing.
    
    Returns:
        BookFormatter: Book formatter instance
    """
    return BookFormatter()


@pytest.fixture
def sample_book_metadata():
    """
    Create sample book metadata for testing.
    
    Returns:
        BookMetadata: Sample metadata
    """
    return BookMetadata(
        title="Test Book",
        author="Test Author",
        age_group=AgeGroup.PRESCHOOL,
        book_type=BookType.STORY,
        theme="Adventure",
        educational_focus="Nature",
        trim_size=TrimSize.STANDARD,
        page_count=24
    )


def test_dimension_calculations(book_formatter, sample_book_metadata):
    """Test that dimension calculations are correct for different trim sizes."""
    # Test standard trim size
    standard_dims = book_formatter._calculate_dimensions(TrimSize.STANDARD)
    assert standard_dims["width"] == 8.5 * 300  # 8.5 inches * 300 DPI
    assert standard_dims["height"] == 11 * 300  # 11 inches * 300 DPI
    assert standard_dims["bleed"] == 0.125 * 300  # 0.125 inches * 300 DPI
    
    # Test square trim size
    square_dims = book_formatter._calculate_dimensions(TrimSize.SQUARE)
    assert square_dims["width"] == 8.5 * 300  # 8.5 inches * 300 DPI
    assert square_dims["height"] == 8.5 * 300  # 8.5 inches * 300 DPI


def test_spine_width_calculation(book_formatter):
    """Test that spine width calculations are correct for different page counts."""
    # Test spine width for 24 pages with white paper
    spine_24_white = book_formatter._calculate_spine_width(24, "white")
    expected_spine_24_white = 24 * 0.002252  # 24 pages * 0.002252 inches per page
    assert spine_24_white == pytest.approx(expected_spine_24_white)
    
    # Test spine width for 100 pages with cream paper
    spine_100_cream = book_formatter._calculate_spine_width(100, "cream")
    expected_spine_100_cream = 100 * 0.0025  # 100 pages * 0.0025 inches per page
    assert spine_100_cream == pytest.approx(expected_spine_100_cream)


async def test_book_formatting(book_formatter, sample_book_metadata):
    """Test that book formatting returns a valid file path."""
    # Mock content and images for testing
    mock_content = {
        "chapters": [
            {
                "title": "Chapter 1",
                "content": "Test content",
                "illustration_prompt": "Test prompt"
            }
        ]
    }
    mock_images = ["test_image_1.png", "test_image_2.png"]
    
    # Format the book
    pdf_path = await book_formatter.format_book(
        sample_book_metadata, 
        mock_content, 
        mock_images
    )
    
    # Check that the path looks correct
    assert pdf_path is not None
    assert ".pdf" in pdf_path
    assert "test_book" in pdf_path.lower()


async def test_cover_creation(book_formatter, sample_book_metadata):
    """Test that cover creation returns a valid file path."""
    cover_path = await book_formatter.create_cover(sample_book_metadata)
    
    # Check that the path looks correct
    assert cover_path is not None
    assert ".pdf" in cover_path
    assert "cover" in cover_path.lower()
    assert "test_book" in cover_path.lower()
