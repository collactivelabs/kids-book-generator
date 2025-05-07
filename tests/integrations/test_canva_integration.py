"""
Tests for Canva integration functionality.

This module contains unit and integration tests for the Canva integration
components, including client, templates, export, and preview functionality.
"""
import os
import json
import pytest
from datetime import datetime
from unittest.mock import patch, MagicMock, AsyncMock
from pathlib import Path

import aiohttp
from fastapi import HTTPException

from src.api.models import BookMetadata, BookType, TrimSize, AgeGroup
from src.integrations.canva import (
    canva_client, CanvaDesign, CanvaDesignRequest, CanvaExportRequest
)
from src.integrations.canva_templates import (
    canva_template_manager, CanvaTemplate
)
from src.integrations.canva_export import (
    canva_export_manager, ExportStatus
)
from src.integrations.canva_preview import (
    canva_preview_manager, PreviewOptions, PreviewResult
)


# Fixture for test access token
@pytest.fixture
def mock_access_token():
    return "test_access_token"


# Fixture for test design ID
@pytest.fixture
def mock_design_id():
    return "test_design_id"


# Fixture for test export ID
@pytest.fixture
def mock_export_id():
    return "export_test123"


# Fixture for test template
@pytest.fixture
def mock_template():
    return CanvaTemplate(
        template_id="template_test123",
        name="Test Template",
        description="Test template description",
        book_type=BookType.STORY,
        trim_size=TrimSize.STANDARD,
        age_groups=["3-5", "5-7"],
        created_at=datetime.now(),
        updated_at=datetime.now(),
        properties={
            "page_layout": "text_with_image",
            "font_families": ["Roboto", "Open Sans"],
            "color_scheme": ["#4B9CD3", "#FFFFFF", "#333333"]
        },
        tags=["test", "story", "children"]
    )


# Fixture for test book metadata
@pytest.fixture
def mock_book_metadata():
    return BookMetadata(
        title="Test Book",
        author="Test Author",
        age_group=AgeGroup.PRESCHOOL,
        book_type=BookType.STORY,
        theme="Adventure",
        trim_size=TrimSize.STANDARD,
        page_count=24
    )


# Tests for CanvaConnectClient
class TestCanvaConnectClient:
    """Tests for the Canva Connect API client."""
    
    def test_get_authorization_url(self):
        """Test generating an authorization URL."""
        state = "test_state"
        auth_url = canva_client.get_authorization_url(state=state)
        
        assert "canva.com/oauth/authorize" in auth_url
        assert "client_id=" in auth_url
        assert f"state={state}" in auth_url
    
    @pytest.mark.asyncio
    async def test_exchange_code_for_token(self, monkeypatch):
        """Test exchanging an authorization code for an access token."""
        # Mock aiohttp.ClientSession
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value={
            "access_token": "test_access_token",
            "refresh_token": "test_refresh_token",
            "expires_in": 3600,
            "token_type": "bearer",
            "scope": "design.read design.write"
        })
        
        mock_session = AsyncMock()
        mock_session.__aenter__.return_value = mock_session
        mock_session.post.return_value.__aenter__.return_value = mock_response
        
        monkeypatch.setattr(aiohttp, "ClientSession", MagicMock(return_value=mock_session))
        
        # Test the method
        code = "test_code"
        token_response = await canva_client.exchange_code_for_token(code)
        
        assert token_response["access_token"] == "test_access_token"
        assert token_response["refresh_token"] == "test_refresh_token"
        assert token_response["expires_in"] == 3600
    
    @pytest.mark.asyncio
    async def test_refresh_access_token(self, monkeypatch):
        """Test refreshing an access token."""
        # Mock aiohttp.ClientSession
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value={
            "access_token": "new_access_token",
            "refresh_token": "new_refresh_token",
            "expires_in": 3600,
            "token_type": "bearer",
            "scope": "design.read design.write"
        })
        
        mock_session = AsyncMock()
        mock_session.__aenter__.return_value = mock_session
        mock_session.post.return_value.__aenter__.return_value = mock_response
        
        monkeypatch.setattr(aiohttp, "ClientSession", MagicMock(return_value=mock_session))
        
        # Test the method
        refresh_token = "test_refresh_token"
        token_response = await canva_client.refresh_access_token(refresh_token)
        
        assert token_response["access_token"] == "new_access_token"
        assert token_response["refresh_token"] == "new_refresh_token"
        assert token_response["expires_in"] == 3600
    
    @pytest.mark.asyncio
    async def test_create_design_from_book_metadata(self, mock_access_token, mock_book_metadata, monkeypatch):
        """Test creating a design from book metadata."""
        # Mock the create_design method
        expected_response = {"designId": "new_design_id", "title": mock_book_metadata.title}
        mock_create_design = AsyncMock(return_value=expected_response)
        monkeypatch.setattr(canva_client, "create_design", mock_create_design)
        
        # Test the method
        response = await canva_client.create_design_from_book_metadata(
            access_token=mock_access_token,
            metadata=mock_book_metadata
        )
        
        assert response == expected_response
        mock_create_design.assert_called_once()
        
        # Check that design request contains expected data
        call_args = mock_create_design.call_args[1]
        assert call_args["access_token"] == mock_access_token
        assert isinstance(call_args["design_request"], CanvaDesignRequest)
        assert call_args["design_request"].title == mock_book_metadata.title


# Tests for CanvaTemplateManager
class TestCanvaTemplateManager:
    """Tests for the Canva template manager."""
    
    def test_get_templates(self, mock_template, monkeypatch):
        """Test getting templates with filters."""
        # Mock the templates collection
        monkeypatch.setattr(canva_template_manager, "story_templates", {
            mock_template.template_id: mock_template
        })
        monkeypatch.setattr(canva_template_manager, "coloring_templates", {})
        
        # Test without filters
        templates = canva_template_manager.get_templates()
        assert len(templates) == 1
        assert templates[0].template_id == mock_template.template_id
        
        # Test with book type filter
        templates = canva_template_manager.get_templates(book_type=BookType.STORY)
        assert len(templates) == 1
        
        templates = canva_template_manager.get_templates(book_type=BookType.COLORING)
        assert len(templates) == 0
        
        # Test with age group filter
        templates = canva_template_manager.get_templates(age_group="3-5")
        assert len(templates) == 1
        
        templates = canva_template_manager.get_templates(age_group="0-3")
        assert len(templates) == 0
        
        # Test with tag filter
        templates = canva_template_manager.get_templates(tags=["test"])
        assert len(templates) == 1
        
        templates = canva_template_manager.get_templates(tags=["nonexistent"])
        assert len(templates) == 0
    
    def test_create_template(self):
        """Test creating a new template."""
        # Create a template
        template = canva_template_manager.create_template(
            name="Test Template",
            description="Test template description",
            book_type=BookType.STORY,
            trim_size=TrimSize.STANDARD,
            age_groups=["3-5", "5-7"],
            properties={
                "page_layout": "text_with_image"
            },
            tags=["test", "story"]
        )
        
        # Verify template was created correctly
        assert template.name == "Test Template"
        assert template.description == "Test template description"
        assert template.book_type == BookType.STORY
        assert template.trim_size == TrimSize.STANDARD
        assert "3-5" in template.age_groups
        assert "page_layout" in template.properties
        assert "test" in template.tags
        
        # Verify template was added to the correct collection
        assert template.template_id in canva_template_manager.story_templates
        
        # Clean up - Delete the template
        canva_template_manager.delete_template(template.template_id)
    
    def test_get_default_template(self, mock_template, monkeypatch):
        """Test getting the default template for a book type and trim size."""
        # Mock the default templates mapping
        monkeypatch.setattr(canva_template_manager, "default_templates", {
            BookType.STORY.value: {
                TrimSize.STANDARD.value: mock_template.template_id
            }
        })
        
        # Mock the get_template method
        monkeypatch.setattr(
            canva_template_manager, 
            "get_template", 
            MagicMock(return_value=mock_template)
        )
        
        # Test getting the default template
        template = canva_template_manager.get_default_template(
            book_type=BookType.STORY,
            trim_size=TrimSize.STANDARD
        )
        
        assert template is not None
        assert template.template_id == mock_template.template_id
        
        # Test getting a non-existent default template
        template = canva_template_manager.get_default_template(
            book_type=BookType.COLORING,
            trim_size=TrimSize.SQUARE
        )
        
        assert template is None


# Tests for CanvaExportManager
class TestCanvaExportManager:
    """Tests for the Canva export manager."""
    
    @pytest.mark.asyncio
    async def test_export_design(self, mock_access_token, mock_design_id, monkeypatch):
        """Test starting a design export."""
        # Mock the _process_export method
        mock_process_export = AsyncMock()
        monkeypatch.setattr(canva_export_manager, "_process_export", mock_process_export)
        
        # Test the method
        export_id = await canva_export_manager.export_design(
            access_token=mock_access_token,
            design_id=mock_design_id
        )
        
        assert export_id is not None
        assert export_id in canva_export_manager.exports
        assert canva_export_manager.exports[export_id].status == "pending"
        assert canva_export_manager.exports[export_id].design_id == mock_design_id
        
        # Verify _process_export was called
        mock_process_export.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_export_status(self, mock_export_id, monkeypatch):
        """Test getting the status of an export."""
        # Create a test export status
        status = ExportStatus(
            export_id=mock_export_id,
            design_id="test_design_id",
            status="completed",
            completed_at=datetime.now(),
            download_url="https://example.com/download",
            local_path="/tmp/export.pdf",
            export_type="pdf"
        )
        
        # Add to exports dictionary
        monkeypatch.setattr(canva_export_manager, "exports", {mock_export_id: status})
        
        # Test the method
        result = await canva_export_manager.get_export_status(mock_export_id)
        
        assert result is not None
        assert result.export_id == mock_export_id
        assert result.status == "completed"
        assert result.download_url == "https://example.com/download"
        assert result.local_path == "/tmp/export.pdf"
        
        # Test with non-existent export ID
        result = await canva_export_manager.get_export_status("nonexistent")
        assert result is None


# Tests for CanvaPreviewManager
class TestCanvaPreviewManager:
    """Tests for the Canva preview manager."""
    
    @pytest.mark.asyncio
    async def test_generate_design_preview(self, mock_access_token, mock_design_id, monkeypatch):
        """Test generating a preview for a design."""
        # Mock the get_design method
        mock_design_info = {
            "thumbnail": {
                "url": "https://example.com/thumbnail.jpg"
            }
        }
        mock_get_design = AsyncMock(return_value=mock_design_info)
        monkeypatch.setattr(canva_client, "get_design", mock_get_design)
        
        # Mock the _process_thumbnail method
        mock_preview_data = "data:image/png;base64,abc123"
        mock_process_thumbnail = AsyncMock(return_value=mock_preview_data)
        monkeypatch.setattr(canva_preview_manager, "_process_thumbnail", mock_process_thumbnail)
        
        # Test the method
        options = PreviewOptions(width=300, height=400)
        result = await canva_preview_manager.generate_design_preview(
            access_token=mock_access_token,
            design_id=mock_design_id,
            options=options
        )
        
        assert result is not None
        assert result.preview_type == "image"
        assert result.preview_data == mock_preview_data
        assert "design_id" in result.metadata
        assert result.metadata["design_id"] == mock_design_id
        
        # Verify get_design was called
        mock_get_design.assert_called_once_with(
            access_token=mock_access_token,
            design_id=mock_design_id
        )
        
        # Verify _process_thumbnail was called
        mock_process_thumbnail.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_preview(self, monkeypatch):
        """Test getting a previously generated preview."""
        # Create a test preview
        preview_id = "preview_test123"
        preview_data = {
            "preview_id": preview_id,
            "preview_data": "data:image/png;base64,abc123",
            "preview_type": "image",
            "width": 300,
            "height": 400,
            "created_at": datetime.now().isoformat(),
            "metadata": {"design_id": "test_design_id"}
        }
        
        # Add to previews dictionary
        monkeypatch.setattr(canva_preview_manager, "previews", {preview_id: preview_data})
        
        # Test the method
        result = await canva_preview_manager.get_preview(preview_id)
        
        assert result is not None
        assert result.preview_id == preview_id
        assert result.preview_data == "data:image/png;base64,abc123"
        assert result.preview_type == "image"
        assert result.width == 300
        assert result.height == 400
        
        # Test with non-existent preview ID
        result = await canva_preview_manager.get_preview("nonexistent")
        assert result is None
