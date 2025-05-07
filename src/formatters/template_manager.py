"""
Template Manager module for Kids Book Generator.

This module handles the loading, management, and application of book templates
to ensure consistent formatting and styling.
"""
import os
import json
import logging
from typing import Dict, List, Optional, Any, Tuple, Union
from pathlib import Path
from datetime import datetime
import uuid
import shutil

from src.api.models import BookMetadata, BookType, TrimSize, AgeGroup
from src.config import settings
from src.utils.logging import get_logger


logger = get_logger(__name__)


class BookTemplate:
    """
    Book template class representing a reusable book layout.
    
    A template contains configuration for page layouts, fonts,
    colors, and other formatting properties.
    """
    
    def __init__(self, 
                 template_id: str,
                 name: str,
                 description: str,
                 book_type: BookType,
                 age_groups: List[str],
                 properties: Dict[str, Any],
                 preview_image: Optional[str] = None):
        """
        Initialize a book template.
        
        Args:
            template_id: Unique identifier for the template
            name: User-friendly template name
            description: Template description
            book_type: Type of book this template is for
            age_groups: List of age groups this template is suitable for
            properties: Dictionary of template properties
            preview_image: Optional path to preview image
        """
        self.template_id = template_id
        self.name = name
        self.description = description
        self.book_type = book_type
        self.age_groups = age_groups
        self.properties = properties
        self.preview_image = preview_image
        self.created_at = datetime.now().isoformat()
        self.updated_at = self.created_at
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert template to dictionary for storage."""
        return {
            "template_id": self.template_id,
            "name": self.name,
            "description": self.description,
            "book_type": self.book_type.value if isinstance(self.book_type, BookType) else self.book_type,
            "age_groups": self.age_groups,
            "properties": self.properties,
            "preview_image": self.preview_image,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BookTemplate':
        """Create template from dictionary."""
        # Convert string book_type to enum if needed
        book_type = data.get("book_type")
        if isinstance(book_type, str):
            book_type = BookType(book_type)
        
        return cls(
            template_id=data["template_id"],
            name=data["name"],
            description=data["description"],
            book_type=book_type,
            age_groups=data["age_groups"],
            properties=data["properties"],
            preview_image=data.get("preview_image")
        )


class TemplateManager:
    """
    Manager for book templates.
    
    This class handles:
    - Loading and saving templates
    - Finding appropriate templates for a book
    - Applying templates to book content
    """
    
    def __init__(self, templates_dir: Optional[str] = None):
        """
        Initialize the template manager.
        
        Args:
            templates_dir: Directory to store template files
        """
        # Set up directory
        self.templates_dir = Path(templates_dir) if templates_dir else Path(settings.STORAGE_DIR) / "templates"
        self.templates_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize template collections
        self.story_templates: Dict[str, BookTemplate] = {}
        self.coloring_templates: Dict[str, BookTemplate] = {}
        
        # Load existing templates
        self._load_templates()
        
        # If no templates exist, create default templates
        if not self.story_templates and not self.coloring_templates:
            self._create_default_templates()
    
    def _load_templates(self) -> None:
        """Load all templates from the templates directory."""
        logger.info(f"Loading templates from {self.templates_dir}")
        
        try:
            # Find all template JSON files
            template_files = list(self.templates_dir.glob("*.json"))
            
            if not template_files:
                logger.info("No template files found")
                return
            
            # Load each template
            for file_path in template_files:
                try:
                    with open(file_path, "r") as f:
                        data = json.load(f)
                    
                    template = BookTemplate.from_dict(data)
                    
                    # Add to appropriate collection
                    if template.book_type == BookType.COLORING:
                        self.coloring_templates[template.template_id] = template
                    else:
                        self.story_templates[template.template_id] = template
                    
                    logger.debug(f"Loaded template: {template.name} ({template.template_id})")
                except Exception as e:
                    logger.error(f"Error loading template from {file_path}: {str(e)}")
        
        except Exception as e:
            logger.error(f"Error loading templates: {str(e)}")
    
    def _create_default_templates(self) -> None:
        """Create default templates if none exist."""
        logger.info("Creating default templates")
        
        # Default story book templates
        story_templates = [
            {
                "template_id": "story_standard_simple",
                "name": "Simple Story Book",
                "description": "A clean, simple layout for story books with illustrations.",
                "book_type": BookType.STORY,
                "age_groups": [ag.value for ag in AgeGroup],
                "properties": {
                    "layout": "standard",
                    "font_family": "Helvetica",
                    "title_font": "Helvetica-Bold",
                    "body_font": "Helvetica",
                    "caption_font": "Helvetica-Oblique",
                    "color_scheme": {
                        "primary": "#4B9CD3",  # Blue
                        "secondary": "#FFFFFF",  # White
                        "text": "#333333"  # Dark Gray
                    },
                    "title_alignment": "center",
                    "body_alignment": "left",
                    "image_placement": "below_text",
                    "page_numbering": True
                }
            },
            {
                "template_id": "story_fantasy",
                "name": "Fantasy Adventure",
                "description": "A magical template for fantasy and adventure stories.",
                "book_type": BookType.STORY,
                "age_groups": ["5-7", "7-12"],
                "properties": {
                    "layout": "fantasy",
                    "font_family": "Helvetica",
                    "title_font": "Helvetica-Bold",
                    "body_font": "Helvetica",
                    "caption_font": "Helvetica-Oblique",
                    "color_scheme": {
                        "primary": "#7B2CBF",  # Purple
                        "secondary": "#9D4EDD",  # Light Purple
                        "text": "#333333"  # Dark Gray
                    },
                    "page_borders": "decorative",
                    "title_alignment": "center",
                    "body_alignment": "justified",
                    "image_placement": "alternating",
                    "page_numbering": True
                }
            },
            {
                "template_id": "story_educational",
                "name": "Educational Journey",
                "description": "A template designed for educational content with clear structure.",
                "book_type": BookType.STORY,
                "age_groups": ["3-5", "5-7", "7-12"],
                "properties": {
                    "layout": "educational",
                    "font_family": "Helvetica",
                    "title_font": "Helvetica-Bold",
                    "body_font": "Helvetica",
                    "caption_font": "Helvetica-Oblique",
                    "color_scheme": {
                        "primary": "#2A9D8F",  # Teal
                        "secondary": "#E9C46A",  # Yellow
                        "text": "#264653"  # Dark Blue
                    },
                    "info_boxes": True,
                    "title_alignment": "center",
                    "body_alignment": "left",
                    "image_placement": "alternating",
                    "page_numbering": True,
                    "educational_notes": True
                }
            }
        ]
        
        # Default coloring book templates
        coloring_templates = [
            {
                "template_id": "coloring_simple",
                "name": "Simple Coloring Book",
                "description": "A basic coloring book with one image per page.",
                "book_type": BookType.COLORING,
                "age_groups": [ag.value for ag in AgeGroup],
                "properties": {
                    "layout": "standard",
                    "font_family": "Helvetica",
                    "title_font": "Helvetica-Bold",
                    "page_numbering": True,
                    "image_border": False,
                    "image_placement": "centered",
                    "captions": False
                }
            },
            {
                "template_id": "coloring_educational",
                "name": "Educational Coloring Book",
                "description": "A coloring book with educational captions for each image.",
                "book_type": BookType.COLORING,
                "age_groups": ["3-5", "5-7", "7-12"],
                "properties": {
                    "layout": "educational",
                    "font_family": "Helvetica",
                    "title_font": "Helvetica-Bold",
                    "caption_font": "Helvetica",
                    "page_numbering": True,
                    "image_border": True,
                    "image_placement": "centered",
                    "captions": True,
                    "fun_facts": True
                }
            }
        ]
        
        # Save story book templates
        for template_data in story_templates:
            template = BookTemplate.from_dict(template_data)
            self.story_templates[template.template_id] = template
            self.save_template(template)
        
        # Save coloring book templates
        for template_data in coloring_templates:
            template = BookTemplate.from_dict(template_data)
            self.coloring_templates[template.template_id] = template
            self.save_template(template)
        
        logger.info(f"Created {len(story_templates)} story templates and {len(coloring_templates)} coloring templates")
    
    def save_template(self, template: BookTemplate) -> bool:
        """
        Save a template to file.
        
        Args:
            template: The template to save
            
        Returns:
            True if saved successfully
        """
        # Update timestamp
        template.updated_at = datetime.now().isoformat()
        
        # Save preview image if provided
        if template.preview_image and os.path.exists(template.preview_image):
            preview_filename = f"{template.template_id}_preview.png"
            preview_path = self.templates_dir / preview_filename
            try:
                shutil.copy(template.preview_image, preview_path)
                template.preview_image = str(preview_path)
            except Exception as e:
                logger.error(f"Error saving preview image: {str(e)}")
        
        # Save template data
        filepath = self.templates_dir / f"{template.template_id}.json"
        try:
            with open(filepath, "w") as f:
                json.dump(template.to_dict(), f, indent=2)
            logger.info(f"Template {template.template_id} saved to {filepath}")
            return True
        except Exception as e:
            logger.error(f"Error saving template {template.template_id}: {str(e)}")
            return False
    
    def get_template(self, template_id: str) -> Optional[BookTemplate]:
        """
        Get a template by ID.
        
        Args:
            template_id: Template ID to retrieve
            
        Returns:
            Template object or None if not found
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
                
                template = BookTemplate.from_dict(data)
                
                # Add to appropriate collection
                if template.book_type == BookType.COLORING:
                    self.coloring_templates[template_id] = template
                else:
                    self.story_templates[template_id] = template
                
                return template
            except Exception as e:
                logger.error(f"Error loading template {template_id}: {str(e)}")
        
        logger.warning(f"Template {template_id} not found")
        return None
    
    def create_template(self, 
                      name: str,
                      description: str,
                      book_type: BookType,
                      age_groups: List[str],
                      properties: Dict[str, Any],
                      preview_image: Optional[str] = None) -> BookTemplate:
        """
        Create a new template.
        
        Args:
            name: Template name
            description: Template description
            book_type: Type of book this template is for
            age_groups: List of age groups this template is suitable for
            properties: Dictionary of template properties
            preview_image: Optional path to preview image
            
        Returns:
            New template instance
        """
        # Generate unique template ID
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        uid = str(uuid.uuid4())[:8]
        template_id = f"template_{book_type.value}_{timestamp}_{uid}"
        
        # Create template
        template = BookTemplate(
            template_id=template_id,
            name=name,
            description=description,
            book_type=book_type,
            age_groups=age_groups,
            properties=properties,
            preview_image=preview_image
        )
        
        # Save template
        self.save_template(template)
        
        # Add to appropriate collection
        if book_type == BookType.COLORING:
            self.coloring_templates[template_id] = template
        else:
            self.story_templates[template_id] = template
        
        return template
    
    def find_templates(self, book_type: BookType, age_group: Optional[str] = None) -> List[BookTemplate]:
        """
        Find templates suitable for a specific book type and age group.
        
        Args:
            book_type: Type of book
            age_group: Optional age group filter
            
        Returns:
            List of suitable templates
        """
        # Determine which collection to search
        templates = self.coloring_templates if book_type == BookType.COLORING else self.story_templates
        
        # Filter templates by age group if provided
        if age_group:
            return [t for t in templates.values() if age_group in t.age_groups]
        else:
            return list(templates.values())
    
    def get_default_template(self, book_type: BookType, age_group: Optional[str] = None) -> BookTemplate:
        """
        Get the default template for a book type and age group.
        
        Args:
            book_type: Type of book
            age_group: Optional age group filter
            
        Returns:
            Default template
        """
        templates = self.find_templates(book_type, age_group)
        
        if not templates:
            # No suitable template found, use the first template of this type
            all_templates = self.coloring_templates if book_type == BookType.COLORING else self.story_templates
            if all_templates:
                return next(iter(all_templates.values()))
            else:
                # No templates at all, create a default
                self._create_default_templates()
                return self.get_default_template(book_type, age_group)
        
        # Return the first suitable template
        return templates[0]
    
    def apply_template_properties(self, content: Dict[str, Any], template: BookTemplate) -> Dict[str, Any]:
        """
        Apply template properties to book content.
        
        Args:
            content: Book content
            template: Template to apply
            
        Returns:
            Content with template properties applied
        """
        # Make a copy of the content to avoid modifying the original
        result = content.copy()
        
        # Add template metadata
        result["template"] = {
            "id": template.template_id,
            "name": template.name,
            "description": template.description,
            "properties": template.properties
        }
        
        # Apply specific formatting based on template properties
        if template.book_type == BookType.STORY:
            # Apply story book formatting
            result = self._apply_story_template(result, template)
        else:
            # Apply coloring book formatting
            result = self._apply_coloring_template(result, template)
        
        return result
    
    def _apply_story_template(self, content: Dict[str, Any], template: BookTemplate) -> Dict[str, Any]:
        """Apply story book template."""
        # Apply template properties to each chapter
        if "chapters" in content:
            for chapter in content["chapters"]:
                # Apply formatting properties to chapter
                chapter["formatting"] = {
                    "title_font": template.properties.get("title_font", "Helvetica-Bold"),
                    "body_font": template.properties.get("body_font", "Helvetica"),
                    "caption_font": template.properties.get("caption_font", "Helvetica-Oblique"),
                    "title_alignment": template.properties.get("title_alignment", "center"),
                    "body_alignment": template.properties.get("body_alignment", "left"),
                    "image_placement": template.properties.get("image_placement", "below_text"),
                    "color_scheme": template.properties.get("color_scheme", {
                        "primary": "#000000",
                        "secondary": "#FFFFFF",
                        "text": "#333333"
                    })
                }
        
        return content
    
    def _apply_coloring_template(self, content: Dict[str, Any], template: BookTemplate) -> Dict[str, Any]:
        """Apply coloring book template."""
        # Apply formatting properties to content
        content["formatting"] = {
            "title_font": template.properties.get("title_font", "Helvetica-Bold"),
            "caption_font": template.properties.get("caption_font", "Helvetica"),
            "image_border": template.properties.get("image_border", False),
            "image_placement": template.properties.get("image_placement", "centered"),
            "captions": template.properties.get("captions", False),
            "page_numbering": template.properties.get("page_numbering", True)
        }
        
        return content


# Create a singleton instance for use in the application
template_manager = TemplateManager()
