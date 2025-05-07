"""
Content moderation utilities for the Kids Book Generator.

This module provides functions and classes for filtering and moderating 
content to ensure it's appropriate for children's books.
"""
import re
import json
import logging
from typing import Dict, List, Optional, Any, Tuple, Union
import asyncio

import openai
from tenacity import retry, stop_after_attempt, wait_exponential

from src.config import settings
from src.utils.logging import get_logger


logger = get_logger(__name__)


class ContentModerator:
    """
    Content moderation service for ensuring all generated content is 
    appropriate for children.
    
    This class provides methods for:
    - Text content moderation
    - Image prompt validation
    - Age-appropriateness checking
    - Content classification
    """
    
    def __init__(self):
        """Initialize the content moderator with configuration settings."""
        self.api_key = settings.OPENAI_API_KEY
        self.client = openai.AsyncOpenAI(api_key=self.api_key)
        
        # Content moderation configuration
        self.MODERATION_MODEL = "text-moderation-latest"
        
        # Age-appropriate content guidelines
        self.AGE_GUIDELINES = {
            "0-3": {
                "vocabulary_level": "Simple, familiar words. Short sentences.",
                "themes": "Everyday experiences, family, animals, bedtime routines",
                "prohibited": ["scary situations", "complex problems", "abstract concepts"]
            },
            "3-5": {
                "vocabulary_level": "Basic vocabulary with some new words. Simple sentences.",
                "themes": "Friendship, sharing, simple adventures, basic emotions",
                "prohibited": ["violence", "scary characters", "complex moral dilemmas"]
            },
            "5-7": {
                "vocabulary_level": "Expanded vocabulary. Simple paragraphs.",
                "themes": "School experiences, friendships, adventures, problem-solving",
                "prohibited": ["violence", "intense fear", "mature themes"]
            },
            "7-12": {
                "vocabulary_level": "Rich vocabulary. More complex sentences and paragraphs.",
                "themes": "More complex adventures, problem-solving, emotional growth",
                "prohibited": ["graphic violence", "romantic relationships", "mature themes"]
            }
        }
        
        # General prohibited content for all ages
        self.PROHIBITED_CONTENT = [
            "violence", "weapons", "blood", "injury", "death", "killing",
            "scary monsters", "frightening scenarios", "adult relationships",
            "discrimination", "prejudice", "politics", "religion",
            "alcohol", "drugs", "smoking", "gambling",
            "branded products", "copyrighted characters",
            "dangerous activities without safety context"
        ]
        
        # Regular expression patterns for prohibited content
        self.PROHIBITED_PATTERNS = [
            r'\b(?:kill|kills|killed|killing|murder|murders|murdered|murdering)\b',
            r'\b(?:die|dies|died|dying|death)\b',
            r'\b(?:weapon|weapons|gun|guns|knife|knives|sword|swords)\b',
            r'\b(?:blood|bloody|bleeding)\b',
            r'\b(?:scary|frightening|terrifying|horrifying)\b',
            r'\b(?:alcohol|wine|beer|liquor|drunk|intoxicated)\b',
            r'\b(?:cigarette|smoking|tobacco|vape|vaping)\b',
        ]
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def moderate_openai(self, text: str) -> Dict[str, Any]:
        """
        Use OpenAI's moderation API to check content.
        
        Args:
            text: Text to check
            
        Returns:
            Moderation results from OpenAI
        """
        try:
            response = await self.client.moderations.create(input=text)
            return {
                "flagged": response.results[0].flagged,
                "categories": response.results[0].categories.model_dump(),
                "category_scores": response.results[0].category_scores.model_dump(),
            }
        except Exception as e:
            logger.error(f"Error using OpenAI moderation API: {str(e)}")
            # Fallback to internal moderation if API fails
            return {
                "flagged": False,  # Default to non-flagged but log the error
                "error": str(e),
                "categories": {},
                "category_scores": {}
            }
    
    async def check_text_content(self, text: str, age_group: str = "0-3") -> Tuple[bool, List[str], Dict[str, Any]]:
        """
        Check if text content is appropriate for the specified age group.
        
        Args:
            text: Text content to check
            age_group: Target age group (e.g., "0-3", "3-5", etc.)
            
        Returns:
            Tuple of (is_appropriate, issues, details)
        """
        issues = []
        details = {}
        
        # 1. Check against prohibited patterns
        for pattern in self.PROHIBITED_PATTERNS:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                unique_matches = set(matches)
                issues.append(f"Found prohibited terms: {', '.join(unique_matches)}")
                details[f"pattern_{pattern}"] = list(unique_matches)
        
        # 2. Check against prohibited content for age group
        age_prohibitions = self.AGE_GUIDELINES.get(age_group, {}).get("prohibited", [])
        for prohibited in age_prohibitions:
            if prohibited.lower() in text.lower():
                issues.append(f"Content contains age-inappropriate theme: {prohibited}")
                details[f"age_prohibited_{prohibited}"] = True
        
        # 3. Use OpenAI's moderation API
        moderation_result = await self.moderate_openai(text)
        details["openai_moderation"] = moderation_result
        
        if moderation_result.get("flagged", False):
            issues.append("Content flagged by content moderation system")
        
        is_appropriate = len(issues) == 0
        return is_appropriate, issues, details
    
    async def filter_story_content(self, story_content: Dict[str, Any], age_group: str) -> Tuple[Dict[str, Any], bool, List[str]]:
        """
        Filter and sanitize story content for the specified age group.
        
        Args:
            story_content: Story content dictionary
            age_group: Target age group
            
        Returns:
            Tuple of (filtered_content, is_modified, issues)
        """
        filtered_content = story_content.copy()
        all_issues = []
        is_modified = False
        
        # Check and filter title
        title = story_content.get("title", "")
        title_appropriate, title_issues, _ = await self.check_text_content(title, age_group)
        if not title_appropriate:
            is_modified = True
            all_issues.extend([f"Title issue: {issue}" for issue in title_issues])
            # Sanitize title if needed - for now just log the issue
            
        # Check and filter each chapter
        for i, chapter in enumerate(story_content.get("chapters", [])):
            chapter_title = chapter.get("title", "")
            chapter_content = chapter.get("content", "")
            illustration_prompt = chapter.get("illustration_prompt", "")
            
            # Check chapter title
            title_appropriate, title_issues, _ = await self.check_text_content(chapter_title, age_group)
            if not title_appropriate:
                is_modified = True
                all_issues.extend([f"Chapter {i+1} title issue: {issue}" for issue in title_issues])
            
            # Check chapter content
            content_appropriate, content_issues, _ = await self.check_text_content(chapter_content, age_group)
            if not content_appropriate:
                is_modified = True
                all_issues.extend([f"Chapter {i+1} content issue: {issue}" for issue in content_issues])
                
                # Simple content sanitization - replace problematic words
                for pattern in self.PROHIBITED_PATTERNS:
                    filtered_content["chapters"][i]["content"] = re.sub(
                        pattern, 
                        "[age-appropriate term]", 
                        chapter_content, 
                        flags=re.IGNORECASE
                    )
            
            # Check illustration prompt
            prompt_appropriate, prompt_issues, _ = await self.check_text_content(illustration_prompt, age_group)
            if not prompt_appropriate:
                is_modified = True
                all_issues.extend([f"Chapter {i+1} illustration prompt issue: {issue}" for issue in prompt_issues])
                
                # Sanitize illustration prompt
                for pattern in self.PROHIBITED_PATTERNS:
                    filtered_content["chapters"][i]["illustration_prompt"] = re.sub(
                        pattern, 
                        "[age-appropriate description]", 
                        illustration_prompt, 
                        flags=re.IGNORECASE
                    )
        
        return filtered_content, is_modified, all_issues
    
    async def validate_image_prompt(self, prompt: str, age_group: str = "0-3") -> Tuple[bool, List[str], Dict[str, Any]]:
        """
        Validate if an image generation prompt is appropriate for the specified age group.
        
        Args:
            prompt: Image generation prompt
            age_group: Target age group
            
        Returns:
            Tuple of (is_valid, issues, details)
        """
        # We can reuse the text content check for prompts
        return await self.check_text_content(prompt, age_group)
    
    async def sanitize_image_prompt(self, prompt: str, age_group: str = "0-3") -> Tuple[str, bool, List[str]]:
        """
        Sanitize an image generation prompt to make it age-appropriate.
        
        Args:
            prompt: Image generation prompt
            age_group: Target age group
            
        Returns:
            Tuple of (sanitized_prompt, is_modified, issues)
        """
        is_valid, issues, _ = await self.validate_image_prompt(prompt, age_group)
        
        if is_valid:
            return prompt, False, []
        
        # Simple sanitization - replace problematic patterns
        sanitized_prompt = prompt
        for pattern in self.PROHIBITED_PATTERNS:
            sanitized_prompt = re.sub(pattern, "[age-appropriate term]", sanitized_prompt, flags=re.IGNORECASE)
        
        return sanitized_prompt, True, issues


# Create a singleton instance for use in the application
content_moderator = ContentModerator()
