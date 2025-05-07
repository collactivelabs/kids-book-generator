"""
Tests for content generation functionality.

This module contains tests for story and image generation services.
"""
import pytest
from fastapi.testclient import TestClient

from src.api.models import StoryGenerationRequest, BookMetadata, BookType, AgeGroup, Character
from src.generators.story_generator import StoryGenerator
from src.generators.image_generator import ImageGenerator


@pytest.fixture
def story_generator():
    """
    Create a story generator instance for testing.
    
    Returns:
        StoryGenerator: Story generator instance
    """
    return StoryGenerator()


@pytest.fixture
def image_generator():
    """
    Create an image generator instance for testing.
    
    Returns:
        ImageGenerator: Image generator instance
    """
    return ImageGenerator()


@pytest.fixture
def sample_story_request():
    """
    Create a sample story generation request for testing.
    
    Returns:
        StoryGenerationRequest: Sample request
    """
    return StoryGenerationRequest(
        metadata=BookMetadata(
            title="Test Story",
            author="Test Author",
            age_group=AgeGroup.PRESCHOOL,
            book_type=BookType.STORY,
            theme="Adventure",
            educational_focus="Nature",
            trim_size="8.5x11",
            page_count=24
        ),
        characters=[
            Character(
                name="Luna",
                description="A friendly cat who loves to explore",
                visual_description="Gray tabby cat with green eyes"
            ),
            Character(
                name="Sam",
                description="Luna's owner, a curious child",
                visual_description="Child with curly brown hair and glasses"
            )
        ],
        additional_prompts="Include a lesson about friendship"
    )


async def test_story_generator_prompt_building(story_generator, sample_story_request):
    """Test that the story generator builds an appropriate prompt."""
    prompt = await story_generator._build_prompt(sample_story_request)
    
    # Check that the prompt contains key information
    assert "Test Story" in prompt
    assert "Adventure" in prompt
    assert "Nature" in prompt
    assert "PRESCHOOL" in prompt
    assert "Luna" in prompt
    assert "Sam" in prompt
    assert "friendship" in prompt


async def test_story_generation(story_generator, sample_story_request):
    """Test that the story generator returns structured content."""
    result = await story_generator.generate_story(sample_story_request)
    
    # Check the structure of the result
    assert "title" in result
    assert "chapters" in result
    assert isinstance(result["chapters"], list)
    assert len(result["chapters"]) > 0
    assert "characters" in result
    
    # Check first chapter structure
    chapter = result["chapters"][0]
    assert "title" in chapter
    assert "content" in chapter
    assert "illustration_prompt" in chapter


async def test_image_generator_prompt_enhancement(image_generator):
    """Test that the image generator enhances prompts appropriately."""
    base_prompt = "A cat sitting on a windowsill"
    enhanced_prompt = await image_generator._enhance_prompt(base_prompt)
    
    # Check that the enhancement adds style and quality guidance
    assert base_prompt in enhanced_prompt
    assert "children's book" in enhanced_prompt.lower()
    assert "high quality" in enhanced_prompt.lower()
    
    # Test with custom style
    custom_style = "Watercolor with soft pastel colors"
    custom_enhanced = await image_generator._enhance_prompt(base_prompt, custom_style)
    assert custom_style in custom_enhanced


async def test_image_generation_api_endpoint(test_client: TestClient):
    """Test that the image generation API endpoint returns the expected structure."""
    response = test_client.post(
        "/api/v1/generate/image",
        json={"prompt": "A cat sitting on a windowsill"}
    )
    
    # This is just checking the endpoint responds, not actual generation yet
    assert response.status_code == 200
    assert "message" in response.json()
