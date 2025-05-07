"""
Prompt engineering module for the Kids Book Generator.

This module provides functions and classes for creating, managing,
and optimizing prompts for both story and image generation.
"""
import json
import logging
from typing import Dict, List, Optional, Any, Tuple, Union
from pathlib import Path
import uuid

from src.api.models import BookType, AgeGroup
from src.config import settings
from src.utils.logging import get_logger


logger = get_logger(__name__)


class PromptTemplate:
    """
    A structured prompt template with variable substitution.
    
    This class represents a reusable prompt template with placeholders
    that can be filled with specific content during prompt generation.
    """
    
    def __init__(self, template_id: str, template: str, variables: List[str], metadata: Dict[str, Any] = None):
        """
        Initialize a prompt template.
        
        Args:
            template_id: Unique identifier for the template
            template: Template string with {placeholders}
            variables: List of variable names used in the template
            metadata: Additional template metadata
        """
        self.template_id = template_id
        self.template = template
        self.variables = variables
        self.metadata = metadata or {}
    
    def render(self, values: Dict[str, str]) -> str:
        """
        Render the template with the provided values.
        
        Args:
            values: Dictionary of values to substitute into the template
            
        Returns:
            Rendered prompt string
            
        Raises:
            ValueError: If a required variable is missing
        """
        # Check for missing variables
        missing_vars = [var for var in self.variables if var not in values]
        if missing_vars:
            raise ValueError(f"Missing required variables: {', '.join(missing_vars)}")
        
        # Render template
        try:
            return self.template.format(**values)
        except KeyError as e:
            raise ValueError(f"Error rendering template - unknown variable: {str(e)}")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert template to dictionary for storage."""
        return {
            "template_id": self.template_id,
            "template": self.template,
            "variables": self.variables,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PromptTemplate':
        """Create template from dictionary."""
        return cls(
            template_id=data["template_id"],
            template=data["template"],
            variables=data["variables"],
            metadata=data.get("metadata", {})
        )


class PromptManager:
    """
    Manager for prompt templates and prompt generation.
    
    This class provides functionality for:
    - Loading and saving prompt templates
    - Managing template versions
    - Generating optimized prompts for different use cases
    """
    
    def __init__(self, templates_dir: Optional[str] = None):
        """
        Initialize the prompt manager.
        
        Args:
            templates_dir: Directory to store template files (optional)
        """
        self.templates_dir = Path(templates_dir) if templates_dir else Path(settings.STORAGE_DIR) / "templates" / "prompts"
        self.templates_dir.mkdir(parents=True, exist_ok=True)
        
        # Load templates
        self.story_templates: Dict[str, PromptTemplate] = {}
        self.image_templates: Dict[str, PromptTemplate] = {}
        self.system_templates: Dict[str, PromptTemplate] = {}
        
        # Initialize with default templates
        self._initialize_default_templates()
    
    def _initialize_default_templates(self):
        """Initialize default prompt templates."""
        # Default story system prompt template
        self.system_templates["default_story_system"] = PromptTemplate(
            template_id="default_story_system",
            template="""
You are an expert children's book author specializing in {age_group} age group stories.
Your task is to create an engaging, age-appropriate story that is suitable for publication.

Guidelines for {age_group} age group:
{age_guidelines}

Content restrictions:
- No violence, scary content, or adult themes
- No brand names or copyrighted characters
- No political, religious, or controversial content
- Ensure content is diverse and inclusive
- Focus on positive messages and educational value

Your response must be in JSON format with the following structure:
{{
  "title": "Story title", 
  "chapters": [
    {{
      "title": "Chapter title", 
      "content": "Chapter content", 
      "illustration_prompt": "Detailed illustration description for this chapter"
    }}, 
    ... more chapters ...
  ], 
  "moral_lesson": "The moral lesson of the story", 
  "target_age": "Target age group"
}}
            """.strip(),
            variables=["age_group", "age_guidelines"],
            metadata={"type": "system", "version": "1.0", "use_case": "story_generation"}
        )

        # Default story user prompt template
        self.story_templates["default_story"] = PromptTemplate(
            template_id="default_story",
            template="""
Please create a {book_type} book story for children in the {age_group} age group with the title "{title}".

Story details:
- Theme: {theme}
- Educational focus: {educational_focus}
- Target page count: {page_count} pages
- Chapters: approximately {chapter_count} chapters

{character_info}

{additional_guidelines}

The story should be engaging, age-appropriate, and have a clear moral lesson or educational takeaway.
Each chapter should be accompanied by a detailed illustration prompt describing what should be depicted.

Remember to format your response as valid JSON with the structure provided in the system message.
            """.strip(),
            variables=["book_type", "age_group", "title", "theme", "educational_focus", 
                      "page_count", "chapter_count", "character_info", "additional_guidelines"],
            metadata={"type": "user", "version": "1.0", "use_case": "story_generation"}
        )

        # Default image prompt template
        self.image_templates["default_image"] = PromptTemplate(
            template_id="default_image",
            template="""
{scene_description}

Illustration style: {style}

The image should be detailed, high quality, well-lit, and suitable for a children's book.
Clear composition with no text or words in the image.
Please ensure the image is completely child-appropriate with no scary, violent, or adult content.
            """.strip(),
            variables=["scene_description", "style"],
            metadata={"type": "user", "version": "1.0", "use_case": "image_generation"}
        )

        # Age-specific story templates
        for age_group in ["0-3", "3-5", "5-7", "7-12"]:
            template_id = f"story_{age_group.replace('-', '_')}"
            self.story_templates[template_id] = self._create_age_specific_template(age_group)
    
    def _create_age_specific_template(self, age_group: str) -> PromptTemplate:
        """Create an age-specific story template."""
        age_guidelines = {
            "0-3": """
                Use simple vocabulary with short sentences.
                Focus on familiar concepts and everyday objects.
                Create repetitive patterns and rhythmic language.
                Include bright and friendly imagery.
                Ideal for bedtime stories or learning basic concepts.
            """.strip(),
            "3-5": """
                Use slightly more complex vocabulary with short paragraphs.
                Include clear narrative structure.
                Explore basic emotions and social situations.
                Include educational elements about numbers, letters, or concepts.
                Balance entertainment with subtle learning opportunities.
            """.strip(),
            "5-7": """
                Use varied vocabulary with clear chapters.
                Develop simple but engaging plots.
                Include humor and relatable situations.
                Focus on friendship, adventure, and problem-solving.
                Incorporate subtle moral lessons without being preachy.
            """.strip(),
            "7-12": """
                Use rich vocabulary with more complex sentence structures.
                Develop multi-dimensional characters and plots.
                Explore more complex emotional and social themes.
                Include educational elements integrated naturally into the story.
                Balance entertainment with deeper learning and reflection.
            """.strip()
        }
        
        template_id = f"story_{age_group.replace('-', '_')}"
        template = f"""
Please write an engaging children's story for {age_group} year olds with the title "{{title}}".

Story guidelines:
- Theme: {{theme}}
- Educational focus: {{educational_focus}}
- Reading level: {age_group} years old
- Length: {{page_count}} pages / {{chapter_count}} chapters

Special requirements for {age_group} age group:
{age_guidelines.get(age_group, "")}

{{character_info}}

{{additional_guidelines}}

The story should be enriching, entertaining, and age-appropriate.
Each chapter should include a detailed illustration prompt.

Remember to format your response as valid JSON according to the system instructions.
        """.strip()
        
        return PromptTemplate(
            template_id=template_id,
            template=template,
            variables=["title", "theme", "educational_focus", "page_count", 
                      "chapter_count", "character_info", "additional_guidelines"],
            metadata={"type": "user", "version": "1.0", "use_case": "story_generation", "age_group": age_group}
        )
    
    def save_template(self, template: PromptTemplate, category: str = "story") -> bool:
        """
        Save a prompt template to the appropriate category.
        
        Args:
            template: The template to save
            category: Template category ("story", "image", or "system")
            
        Returns:
            True if saved successfully
        """
        # Select the appropriate template collection
        if category == "story":
            self.story_templates[template.template_id] = template
        elif category == "image":
            self.image_templates[template.template_id] = template
        elif category == "system":
            self.system_templates[template.template_id] = template
        else:
            raise ValueError(f"Unknown template category: {category}")
        
        # Save to file
        filepath = self.templates_dir / f"{category}_{template.template_id}.json"
        try:
            with open(filepath, "w") as f:
                json.dump(template.to_dict(), f, indent=2)
            logger.info(f"Template {template.template_id} saved to {filepath}")
            return True
        except Exception as e:
            logger.error(f"Error saving template {template.template_id}: {str(e)}")
            return False
    
    def load_template(self, template_id: str, category: str = "story") -> Optional[PromptTemplate]:
        """
        Load a prompt template by ID and category.
        
        Args:
            template_id: Template ID to load
            category: Template category
            
        Returns:
            Loaded template or None if not found
        """
        # Check if already loaded
        if category == "story" and template_id in self.story_templates:
            return self.story_templates[template_id]
        elif category == "image" and template_id in self.image_templates:
            return self.image_templates[template_id]
        elif category == "system" and template_id in self.system_templates:
            return self.system_templates[template_id]
        
        # Try to load from file
        filepath = self.templates_dir / f"{category}_{template_id}.json"
        if not filepath.exists():
            logger.warning(f"Template file not found: {filepath}")
            return None
        
        try:
            with open(filepath, "r") as f:
                data = json.load(f)
            template = PromptTemplate.from_dict(data)
            
            # Add to appropriate collection
            if category == "story":
                self.story_templates[template_id] = template
            elif category == "image":
                self.image_templates[template_id] = template
            elif category == "system":
                self.system_templates[template_id] = template
            
            return template
        except Exception as e:
            logger.error(f"Error loading template {template_id}: {str(e)}")
            return None
    
    def get_story_system_prompt(self, age_group: str, custom_template_id: Optional[str] = None) -> str:
        """
        Get a system prompt for story generation.
        
        Args:
            age_group: Target age group
            custom_template_id: Optional custom template ID
            
        Returns:
            Rendered system prompt
        """
        # Determine which template to use
        template_id = custom_template_id or "default_story_system"
        template = self.system_templates.get(template_id)
        
        if not template:
            logger.warning(f"System prompt template {template_id} not found, using default")
            template = self.system_templates["default_story_system"]
        
        # Age-specific guidelines
        age_guidelines = {
            "0-3": "Simple sentences, repetitive patterns, basic concepts, bright and friendly imagery.",
            "3-5": "Short paragraphs, clear narrative, educational elements, exploration of emotions.",
            "5-7": "Clear chapters, simple plot, positive messages, humor, adventure, relatable characters.",
            "7-12": "More complex plots, character development, moral dilemmas, educational integration."
        }.get(age_group, "Age-appropriate content with clear language and positive themes.")
        
        # Render template
        return template.render({
            "age_group": age_group,
            "age_guidelines": age_guidelines
        })
    
    def get_story_prompt(self, 
                       title: str, 
                       book_type: str,
                       age_group: str, 
                       theme: str,
                       educational_focus: str,
                       page_count: int,
                       chapter_count: int,
                       characters: List[Dict[str, str]] = None,
                       additional_guidelines: str = "",
                       custom_template_id: Optional[str] = None) -> str:
        """
        Get a user prompt for story generation.
        
        Args:
            title: Story title
            book_type: Type of book
            age_group: Target age group
            theme: Story theme
            educational_focus: Educational focus
            page_count: Target page count
            chapter_count: Target chapter count
            characters: List of character dictionaries
            additional_guidelines: Additional guidelines
            custom_template_id: Optional custom template ID
            
        Returns:
            Rendered user prompt
        """
        # Determine which template to use
        age_specific_id = f"story_{age_group.replace('-', '_')}"
        template_id = custom_template_id or age_specific_id
        
        if template_id not in self.story_templates and template_id != "default_story":
            logger.warning(f"Story template {template_id} not found, using default")
            template_id = "default_story"
        
        template = self.story_templates.get(template_id)
        if not template:
            template = self.story_templates["default_story"]
        
        # Format character info
        character_info = ""
        if characters and len(characters) > 0:
            character_info = "Characters:\n"
            for char in characters:
                character_info += f"- {char.get('name')}: {char.get('description')}\n"
                if char.get('visual_description'):
                    character_info += f"  Visual description: {char.get('visual_description')}\n"
                if char.get('role'):
                    character_info += f"  Role: {char.get('role')}\n"
        
        # Render template
        return template.render({
            "title": title,
            "book_type": book_type,
            "age_group": age_group,
            "theme": theme,
            "educational_focus": educational_focus,
            "page_count": str(page_count),
            "chapter_count": str(chapter_count),
            "character_info": character_info,
            "additional_guidelines": additional_guidelines
        })
    
    def get_image_prompt(self, 
                       scene_description: str,
                       style: str = "",
                       age_group: Optional[str] = None,
                       custom_template_id: Optional[str] = None) -> str:
        """
        Get a prompt for image generation.
        
        Args:
            scene_description: Description of the scene to generate
            style: Illustration style
            age_group: Optional target age group
            custom_template_id: Optional custom template ID
            
        Returns:
            Rendered image prompt
        """
        # Determine which template to use
        template_id = custom_template_id or "default_image"
        template = self.image_templates.get(template_id)
        
        if not template:
            logger.warning(f"Image prompt template {template_id} not found, using default")
            template = self.image_templates["default_image"]
        
        # Age-specific style if not provided
        if not style and age_group:
            style = {
                "0-3": "Bright, simple, cartoon style with bold outlines. Cheerful colors and minimal details.",
                "3-5": "Colorful, friendly cartoon style. Cute characters with clear emotions.",
                "5-7": "Semi-realistic cartoon style. Diverse characters with clear expressions.",
                "7-12": "More sophisticated illustration style with attention to detail and nuanced expressions."
            }.get(age_group, "Colorful, friendly children's book illustration style")
        
        # Default style if none provided
        if not style:
            style = "Colorful, friendly children's book illustration style with clean lines and vibrant colors"
        
        # Render template
        return template.render({
            "scene_description": scene_description,
            "style": style
        })
    
    def create_custom_template(self, 
                             template: str, 
                             variables: List[str], 
                             category: str = "story",
                             metadata: Dict[str, Any] = None) -> PromptTemplate:
        """
        Create a new custom template.
        
        Args:
            template: Template string with {placeholders}
            variables: List of variable names used in the template
            category: Template category
            metadata: Additional template metadata
            
        Returns:
            New template instance
        """
        # Generate unique template ID
        timestamp = metadata.get("created_at", "").replace(":", "").replace("-", "").replace(".", "")[:14] if metadata else ""
        uid = str(uuid.uuid4())[:8]
        template_id = f"custom_{category}_{timestamp}_{uid}"
        
        # Create new template
        new_template = PromptTemplate(
            template_id=template_id,
            template=template,
            variables=variables,
            metadata=metadata or {"type": "custom", "category": category}
        )
        
        # Save to appropriate collection
        self.save_template(new_template, category)
        
        return new_template


# Create singleton instance for use in the application
prompt_manager = PromptManager()
