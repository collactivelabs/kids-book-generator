"""
Canva template management system for Kids Book Generator.

This module handles the template library for Canva designs,
including template creation, management, and application.
"""
import os
import json
import logging
from typing import Dict, List, Optional, Any, Union
from pathlib import Path
from datetime import datetime
import uuid

from pydantic import BaseModel, Field

from src.config import settings
from src.utils.logging import get_logger
from src.api.models import BookMetadata, BookType, AgeGroup, TrimSize
from src.integrations.canva import canva_client, CanvaDesign


logger = get_logger(__name__)


class CanvaTemplate(BaseModel):
    """Model for Canva template metadata."""
    template_id: str = Field(..., description="Unique identifier for the template")
    canva_id: Optional[str] = Field(None, description="Canva design ID")
    name: str = Field(..., description="Template name")
    description: str = Field(..., description="Template description")
    book_type: BookType = Field(..., description="Book type (story or coloring)")
    trim_size: TrimSize = Field(..., description="Trim size")
    age_groups: List[str] = Field(..., description="Compatible age groups")
    thumbnail_url: Optional[str] = Field(None, description="Thumbnail image URL")
    created_at: datetime = Field(default_factory=datetime.now, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.now, description="Update timestamp")
    properties: Dict[str, Any] = Field(default_factory=dict, description="Template properties")
    tags: List[str] = Field(default_factory=list, description="Template tags")


class CanvaTemplateManager:
    """
    Manager for Canva design templates.
    
    This class handles:
    - Storage and retrieval of templates
    - Finding appropriate templates for books
    - Converting templates to Canva designs
    """
    
    def __init__(self, templates_dir: Optional[str] = None):
        """
        Initialize the template manager.
        
        Args:
            templates_dir: Directory to store template files
        """
        # Set up directory
        self.templates_dir = Path(templates_dir) if templates_dir else Path(settings.STORAGE_DIR) / "canva_templates"
        os.makedirs(self.templates_dir, exist_ok=True)
        
        # Initialize template collections
        self.story_templates: Dict[str, CanvaTemplate] = {}
        self.coloring_templates: Dict[str, CanvaTemplate] = {}
        
        # Load existing templates
        self._load_templates()
        
        # Map of default templates by book type and trim size
        # This maps to template IDs in our local system
        self.default_templates = {
            BookType.STORY.value: {
                TrimSize.STANDARD.value: None,  # Will be populated when templates are loaded
                TrimSize.SQUARE.value: None,
            },
            BookType.COLORING.value: {
                TrimSize.STANDARD.value: None,
                TrimSize.SQUARE.value: None,
            }
        }
        
        # Pre-populate default templates if available
        self._set_default_templates()
    
    def _load_templates(self) -> None:
        """Load all templates from the templates directory."""
        logger.info(f"Loading Canva templates from {self.templates_dir}")
        
        try:
            # Find all template JSON files
            template_files = list(self.templates_dir.glob("*.json"))
            
            if not template_files:
                logger.info("No Canva template files found")
                self._create_default_templates()
                return
            
            # Load each template
            for file_path in template_files:
                try:
                    with open(file_path, "r") as f:
                        data = json.load(f)
                    
                    # Convert dictionary to CanvaTemplate model
                    template = CanvaTemplate(
                        template_id=data["template_id"],
                        canva_id=data.get("canva_id"),
                        name=data["name"],
                        description=data["description"],
                        book_type=data["book_type"],
                        trim_size=data["trim_size"],
                        age_groups=data["age_groups"],
                        thumbnail_url=data.get("thumbnail_url"),
                        created_at=datetime.fromisoformat(data["created_at"]),
                        updated_at=datetime.fromisoformat(data["updated_at"]),
                        properties=data.get("properties", {}),
                        tags=data.get("tags", [])
                    )
                    
                    # Add to appropriate collection
                    if template.book_type == BookType.COLORING:
                        self.coloring_templates[template.template_id] = template
                    else:
                        self.story_templates[template.template_id] = template
                    
                    logger.debug(f"Loaded Canva template: {template.name} ({template.template_id})")
                except Exception as e:
                    logger.error(f"Error loading Canva template from {file_path}: {str(e)}")
        
        except Exception as e:
            logger.error(f"Error loading Canva templates: {str(e)}")
    
    def _create_default_templates(self) -> None:
        """Create default templates if none exist."""
        logger.info("Creating default Canva templates")
        
        # Define default templates
        default_templates = [
            # Story book templates
            {
                "template_id": f"canva_story_standard_{uuid.uuid4().hex[:8]}",
                "name": "Standard Story Book",
                "description": "A standard 8.5x11 story book template with illustrations",
                "book_type": BookType.STORY,
                "trim_size": TrimSize.STANDARD,
                "age_groups": [age_group.value for age_group in AgeGroup],
                "properties": {
                    "page_layout": "text_with_image_below",
                    "font_families": ["Montserrat", "Open Sans"],
                    "color_scheme": ["#4B9CD3", "#FFFFFF", "#333333"],
                    "has_title_page": True,
                    "has_chapter_pages": True,
                    "has_page_numbers": True,
                    "margin_size": "standard"
                },
                "tags": ["story", "standard", "children"]
            },
            {
                "template_id": f"canva_story_square_{uuid.uuid4().hex[:8]}",
                "name": "Square Story Book",
                "description": "A square 8.5x8.5 story book template with illustrations",
                "book_type": BookType.STORY,
                "trim_size": TrimSize.SQUARE,
                "age_groups": [age_group.value for age_group in AgeGroup],
                "properties": {
                    "page_layout": "image_with_text_below",
                    "font_families": ["Quicksand", "Nunito"],
                    "color_scheme": ["#FF9900", "#FFFFFF", "#333333"],
                    "has_title_page": True,
                    "has_chapter_pages": False,
                    "has_page_numbers": True,
                    "margin_size": "large"
                },
                "tags": ["story", "square", "children"]
            },
            # Fantasy story book template
            {
                "template_id": f"canva_story_fantasy_{uuid.uuid4().hex[:8]}",
                "name": "Fantasy Story Book",
                "description": "A fantasy-themed story book template with decorative elements",
                "book_type": BookType.STORY,
                "trim_size": TrimSize.STANDARD,
                "age_groups": ["5-7", "7-12"],
                "properties": {
                    "page_layout": "fantasy_layout",
                    "font_families": ["MedievalSharp", "Fondamento"],
                    "color_scheme": ["#7B2CBF", "#9D4EDD", "#333333"],
                    "has_title_page": True,
                    "has_chapter_pages": True,
                    "has_page_numbers": True,
                    "margin_size": "medium",
                    "has_decorative_borders": True
                },
                "tags": ["story", "fantasy", "medieval", "children"]
            },
            # Coloring book templates
            {
                "template_id": f"canva_coloring_standard_{uuid.uuid4().hex[:8]}",
                "name": "Standard Coloring Book",
                "description": "A standard 8.5x11 coloring book template",
                "book_type": BookType.COLORING,
                "trim_size": TrimSize.STANDARD,
                "age_groups": [age_group.value for age_group in AgeGroup],
                "properties": {
                    "page_layout": "full_page_image",
                    "has_title_page": True,
                    "has_page_numbers": True,
                    "has_captions": False,
                    "image_border": False,
                    "margin_size": "small"
                },
                "tags": ["coloring", "standard", "children"]
            },
            {
                "template_id": f"canva_coloring_square_{uuid.uuid4().hex[:8]}",
                "name": "Square Coloring Book",
                "description": "A square 8.5x8.5 coloring book template",
                "book_type": BookType.COLORING,
                "trim_size": TrimSize.SQUARE,
                "age_groups": [age_group.value for age_group in AgeGroup],
                "properties": {
                    "page_layout": "full_page_image",
                    "has_title_page": True,
                    "has_page_numbers": True,
                    "has_captions": True,
                    "image_border": True,
                    "margin_size": "medium"
                },
                "tags": ["coloring", "square", "children"]
            },
            # Educational coloring book template
            {
                "template_id": f"canva_coloring_educational_{uuid.uuid4().hex[:8]}",
                "name": "Educational Coloring Book",
                "description": "A educational coloring book with facts and information",
                "book_type": BookType.COLORING,
                "trim_size": TrimSize.STANDARD,
                "age_groups": ["3-5", "5-7", "7-12"],
                "properties": {
                    "page_layout": "image_with_facts",
                    "font_families": ["Nunito", "Open Sans"],
                    "has_title_page": True,
                    "has_page_numbers": True,
                    "has_captions": True,
                    "has_fact_boxes": True,
                    "image_border": True,
                    "margin_size": "medium"
                },
                "tags": ["coloring", "educational", "facts", "children"]
            }
        ]
        
        # Save each template
        for template_data in default_templates:
            # Create template instance
            template = CanvaTemplate(
                template_id=template_data["template_id"],
                name=template_data["name"],
                description=template_data["description"],
                book_type=template_data["book_type"],
                trim_size=template_data["trim_size"],
                age_groups=template_data["age_groups"],
                properties=template_data.get("properties", {}),
                tags=template_data.get("tags", [])
            )
            
            # Add to collection and save
            if template.book_type == BookType.COLORING:
                self.coloring_templates[template.template_id] = template
            else:
                self.story_templates[template.template_id] = template
            
            self.save_template(template)
        
        logger.info(f"Created {len(default_templates)} default Canva templates")
        self._set_default_templates()
    
    def _set_default_templates(self) -> None:
        """Set the default templates for each book type and trim size."""
        # Find the best template for each book type and trim size
        for book_type in [BookType.STORY, BookType.COLORING]:
            templates = self.get_templates(book_type=book_type)
            
            # Group by trim size
            by_trim_size = {}
            for template in templates:
                if template.trim_size not in by_trim_size:
                    by_trim_size[template.trim_size] = []
                by_trim_size[template.trim_size].append(template)
            
            # Set default for each trim size
            for trim_size in [TrimSize.STANDARD, TrimSize.SQUARE]:
                if trim_size in by_trim_size and by_trim_size[trim_size]:
                    # Use the first template as default
                    default = by_trim_size[trim_size][0]
                    self.default_templates[book_type.value][trim_size.value] = default.template_id
    
    def save_template(self, template: CanvaTemplate) -> bool:
        """
        Save a template to file.
        
        Args:
            template: Template to save
            
        Returns:
            True if saved successfully
        """
        # Update timestamp
        template.updated_at = datetime.now()
        
        # Save template data
        filepath = self.templates_dir / f"{template.template_id}.json"
        try:
            # Convert template to dictionary
            template_dict = {
                "template_id": template.template_id,
                "canva_id": template.canva_id,
                "name": template.name,
                "description": template.description,
                "book_type": template.book_type.value,
                "trim_size": template.trim_size.value,
                "age_groups": template.age_groups,
                "thumbnail_url": template.thumbnail_url,
                "created_at": template.created_at.isoformat(),
                "updated_at": template.updated_at.isoformat(),
                "properties": template.properties,
                "tags": template.tags
            }
            
            with open(filepath, "w") as f:
                json.dump(template_dict, f, indent=2)
            
            logger.info(f"Canva template {template.template_id} saved to {filepath}")
            return True
        
        except Exception as e:
            logger.error(f"Error saving Canva template {template.template_id}: {str(e)}")
            return False
    
    def get_template(self, template_id: str) -> Optional[CanvaTemplate]:
        """
        Get a template by ID.
        
        Args:
            template_id: Template ID
            
        Returns:
            Template if found, None otherwise
        """
        # Check story templates
        if template_id in self.story_templates:
            return self.story_templates[template_id]
        
        # Check coloring templates
        if template_id in self.coloring_templates:
            return self.coloring_templates[template_id]
        
        # Try to load from file
        filepath = self.templates_dir / f"{template_id}.json"
        if filepath.exists():
            try:
                with open(filepath, "r") as f:
                    data = json.load(f)
                
                # Convert dictionary to CanvaTemplate model
                template = CanvaTemplate(
                    template_id=data["template_id"],
                    canva_id=data.get("canva_id"),
                    name=data["name"],
                    description=data["description"],
                    book_type=data["book_type"],
                    trim_size=data["trim_size"],
                    age_groups=data["age_groups"],
                    thumbnail_url=data.get("thumbnail_url"),
                    created_at=datetime.fromisoformat(data["created_at"]),
                    updated_at=datetime.fromisoformat(data["updated_at"]),
                    properties=data.get("properties", {}),
                    tags=data.get("tags", [])
                )
                
                # Add to appropriate collection
                if template.book_type == BookType.COLORING:
                    self.coloring_templates[template.template_id] = template
                else:
                    self.story_templates[template.template_id] = template
                
                return template
            
            except Exception as e:
                logger.error(f"Error loading Canva template {template_id}: {str(e)}")
        
        logger.warning(f"Canva template {template_id} not found")
        return None
    
    def get_templates(
        self,
        book_type: Optional[BookType] = None,
        trim_size: Optional[TrimSize] = None,
        age_group: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> List[CanvaTemplate]:
        """
        Get templates matching the specified criteria.
        
        Args:
            book_type: Book type filter
            trim_size: Trim size filter
            age_group: Age group filter
            tags: Tags filter (templates must have at least one matching tag)
            
        Returns:
            List of matching templates
        """
        # Start with all templates
        if book_type == BookType.COLORING:
            templates = list(self.coloring_templates.values())
        elif book_type == BookType.STORY:
            templates = list(self.story_templates.values())
        else:
            templates = list(self.coloring_templates.values()) + list(self.story_templates.values())
        
        # Apply filters
        if trim_size:
            templates = [t for t in templates if t.trim_size == trim_size]
        
        if age_group:
            templates = [t for t in templates if age_group in t.age_groups]
        
        if tags:
            templates = [t for t in templates if any(tag in t.tags for tag in tags)]
        
        return templates
    
    def create_template(
        self,
        name: str,
        description: str,
        book_type: BookType,
        trim_size: TrimSize,
        age_groups: List[str],
        canva_id: Optional[str] = None,
        thumbnail_url: Optional[str] = None,
        properties: Optional[Dict[str, Any]] = None,
        tags: Optional[List[str]] = None
    ) -> CanvaTemplate:
        """
        Create a new template.
        
        Args:
            name: Template name
            description: Template description
            book_type: Book type
            trim_size: Trim size
            age_groups: Compatible age groups
            canva_id: Optional Canva design ID
            thumbnail_url: Optional thumbnail URL
            properties: Optional template properties
            tags: Optional template tags
            
        Returns:
            The created template
        """
        # Generate unique ID
        template_id = f"canva_{book_type.value}_{trim_size.value}_{uuid.uuid4().hex[:8]}"
        
        # Create template
        template = CanvaTemplate(
            template_id=template_id,
            canva_id=canva_id,
            name=name,
            description=description,
            book_type=book_type,
            trim_size=trim_size,
            age_groups=age_groups,
            thumbnail_url=thumbnail_url,
            properties=properties or {},
            tags=tags or []
        )
        
        # Save template
        self.save_template(template)
        
        # Add to appropriate collection
        if book_type == BookType.COLORING:
            self.coloring_templates[template_id] = template
        else:
            self.story_templates[template_id] = template
        
        return template
    
    def update_template(
        self,
        template_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        canva_id: Optional[str] = None,
        thumbnail_url: Optional[str] = None,
        properties: Optional[Dict[str, Any]] = None,
        tags: Optional[List[str]] = None
    ) -> Optional[CanvaTemplate]:
        """
        Update an existing template.
        
        Args:
            template_id: Template ID
            name: New template name
            description: New template description
            canva_id: New Canva design ID
            thumbnail_url: New thumbnail URL
            properties: New template properties
            tags: New template tags
            
        Returns:
            The updated template, or None if not found
        """
        template = self.get_template(template_id)
        if not template:
            logger.error(f"Cannot update template {template_id}: not found")
            return None
        
        # Update fields
        if name:
            template.name = name
        if description:
            template.description = description
        if canva_id:
            template.canva_id = canva_id
        if thumbnail_url:
            template.thumbnail_url = thumbnail_url
        if properties:
            template.properties.update(properties)
        if tags:
            template.tags = tags
        
        # Update timestamp and save
        template.updated_at = datetime.now()
        self.save_template(template)
        
        return template
    
    def delete_template(self, template_id: str) -> bool:
        """
        Delete a template.
        
        Args:
            template_id: Template ID
            
        Returns:
            True if deleted successfully
        """
        # Check if template exists
        template = self.get_template(template_id)
        if not template:
            logger.error(f"Cannot delete template {template_id}: not found")
            return False
        
        # Remove from collections
        if template.book_type == BookType.COLORING:
            if template_id in self.coloring_templates:
                del self.coloring_templates[template_id]
        else:
            if template_id in self.story_templates:
                del self.story_templates[template_id]
        
        # Delete file
        filepath = self.templates_dir / f"{template_id}.json"
        try:
            if filepath.exists():
                os.remove(filepath)
            
            logger.info(f"Deleted Canva template {template_id}")
            return True
        
        except Exception as e:
            logger.error(f"Error deleting Canva template {template_id}: {str(e)}")
            return False
    
    def get_default_template(
        self,
        book_type: BookType,
        trim_size: TrimSize
    ) -> Optional[CanvaTemplate]:
        """
        Get the default template for a book type and trim size.
        
        Args:
            book_type: Book type
            trim_size: Trim size
            
        Returns:
            Default template, or None if not found
        """
        template_id = self.default_templates.get(book_type.value, {}).get(trim_size.value)
        if template_id:
            return self.get_template(template_id)
        
        # If no default is set, try to find any template that matches
        templates = self.get_templates(book_type=book_type, trim_size=trim_size)
        if templates:
            return templates[0]
        
        return None
    
    def import_template_from_canva(
        self,
        access_token: str,
        canva_design_id: str,
        name: str,
        description: str,
        book_type: BookType,
        trim_size: TrimSize,
        age_groups: List[str],
        tags: Optional[List[str]] = None
    ) -> Optional[CanvaTemplate]:
        """
        Import a template from Canva.
        
        Args:
            access_token: Canva API access token
            canva_design_id: Canva design ID
            name: Template name
            description: Template description
            book_type: Book type
            trim_size: Trim size
            age_groups: Compatible age groups
            tags: Optional template tags
            
        Returns:
            The imported template, or None if failed
        """
        # Create placeholder for the template
        template = self.create_template(
            name=name,
            description=description,
            book_type=book_type,
            trim_size=trim_size,
            age_groups=age_groups,
            canva_id=canva_design_id,
            tags=tags
        )
        
        # Update with additional information from Canva API
        try:
            # This would be an async call, but we're simulating it for now
            # design_info = await canva_client.get_design(access_token, canva_design_id)
            
            # Set a dummy thumbnail URL for now
            template.thumbnail_url = f"https://placeholder.canva.com/design/{canva_design_id}/thumbnail"
            
            # Save updated template
            self.save_template(template)
            
            return template
        
        except Exception as e:
            logger.error(f"Error importing template from Canva: {str(e)}")
            # Clean up the partially created template
            self.delete_template(template.template_id)
            return None
    
    def find_template_for_book(
        self,
        metadata: BookMetadata
    ) -> Optional[CanvaTemplate]:
        """
        Find the best template for a book based on its metadata.
        
        Args:
            metadata: Book metadata
            
        Returns:
            Best matching template, or None if not found
        """
        # Try to get the default template first
        template = self.get_default_template(
            book_type=metadata.book_type,
            trim_size=metadata.trim_size
        )
        
        if template:
            return template
        
        # If no default, search for templates with matching criteria
        templates = self.get_templates(
            book_type=metadata.book_type,
            trim_size=metadata.trim_size,
            age_group=metadata.age_group.value
        )
        
        if templates:
            # Prioritize templates with matching theme or tags
            if metadata.theme:
                for t in templates:
                    if metadata.theme.lower() in [tag.lower() for tag in t.tags]:
                        return t
            
            # If no theme match, return the first template
            return templates[0]
        
        # No matching template found
        return None


# Create singleton instance
canva_template_manager = CanvaTemplateManager()
