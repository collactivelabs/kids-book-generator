"""
Story Generator module for Kids Book Generator.

This module handles the generation of children's book stories using OpenAI's GPT-4.
It implements age-appropriate content filters and maintains character consistency.
"""
import json
import logging
import asyncio
from typing import Dict, List, Optional, Any, Tuple

import openai
from tenacity import retry, stop_after_attempt, wait_exponential

from src.api.models import StoryGenerationRequest, BookType, AgeGroup, Character, ChapterBase
from src.config import settings
from src.utils.logging import get_logger


logger = get_logger(__name__)


class StoryGenerator:
    """
    Story generation service using OpenAI's GPT-4.
    
    This class handles the generation of children's book stories with
    consideration for age-appropriate content, character consistency,
    and educational value.
    """
    
    def __init__(self):
        """Initialize the story generator with configuration settings."""
        self.api_key = settings.OPENAI_API_KEY
        # Initialize OpenAI client
        self.client = openai.AsyncOpenAI(api_key=self.api_key)
        
        # Constants for story generation
        self.MODEL = "gpt-4-turbo"
        self.TEMPERATURE = 0.7
        self.MAX_TOKENS = 4000
        self.AGE_APPROPRIATE_GUIDELINES = {
            AgeGroup.TODDLER: "Simple sentences, repetitive patterns, basic concepts, bright and friendly imagery, familiar objects and animals.",
            AgeGroup.PRESCHOOL: "Short paragraphs, clear narrative, educational elements, exploration of emotions, diverse characters.",
            AgeGroup.EARLY_READER: "Clear chapters, simple plot, positive messages, humor, adventure, and characters that children can relate to.",
            AgeGroup.MIDDLE_GRADE: "More complex plots, character development, moral dilemmas, educational elements integrated into the story."
        }
        
    async def _build_system_prompt(self, request: StoryGenerationRequest) -> str:
        """Build the system prompt to guide story generation."""
        age_group = request.metadata.age_group
        age_guidelines = self.AGE_APPROPRIATE_GUIDELINES.get(age_group, "")
        
        system_prompt = f"""
        You are an expert children's book author specializing in {request.metadata.age_group.value} age group stories.
        Your task is to create an engaging, age-appropriate story that is suitable for publication.
        
        Guidelines for {request.metadata.age_group.value} age group:
        {age_guidelines}
        
        Content restrictions:
        - No violence, scary content, or adult themes
        - No brand names or copyrighted characters
        - No political, religious, or controversial content
        - Ensure content is diverse and inclusive
        - Focus on positive messages and educational value
        
        Your response must be in JSON format with the following structure:
        {{"title": "Story title", 
          "chapters": [{{
            "title": "Chapter title", 
            "content": "Chapter content", 
            "illustration_prompt": "Detailed illustration description for this chapter"}}, ...], 
          "moral_lesson": "The moral lesson of the story", 
          "target_age": "Target age group"
        }}
        """
        return system_prompt.strip()
        
    async def _build_user_prompt(self, request: StoryGenerationRequest) -> str:
        """
        Build a detailed prompt for story generation based on request parameters.
        
        Args:
            request: The story generation request containing metadata and characters
            
        Returns:
            A formatted prompt string for GPT-4
        """
        age_group = request.metadata.age_group
        book_type = request.metadata.book_type
        theme = request.metadata.theme
        educational_focus = request.metadata.educational_focus or "general knowledge"
        page_count = request.metadata.page_count
        
        # Calculate approximate chapter count based on age group and page count
        if age_group in [AgeGroup.TODDLER, AgeGroup.PRESCHOOL]:
            chapter_count = min(page_count // 2, 5)  # Fewer chapters for younger children
        else:
            chapter_count = min(page_count // 3, 10)  # More chapters for older children
        
        chapter_count = max(chapter_count, 1)  # Ensure at least one chapter
        
        # Build the user prompt
        prompt = f"""
        Please create a {book_type.value} book story for children in the {age_group.value} age group with the title "{request.metadata.title}".
        
        Story details:
        - Theme: {theme}
        - Educational focus: {educational_focus}
        - Target page count: {page_count} pages
        - Chapters: approximately {chapter_count} chapters
        
        The story should be engaging, age-appropriate, and have a clear moral lesson or educational takeaway.
        Each chapter should be accompanied by a detailed illustration prompt describing what should be depicted.
        """
        
        # Add character information if provided
        if request.characters:
            prompt += "\n\nCharacters:\n"
            for character in request.characters:
                prompt += f"- {character.name}: {character.description}\n  Visual description: {character.visual_description}\n  Role: {character.role}\n"
        
        # Add any additional prompts provided by the user
        if request.additional_prompts:
            prompt += f"\n\nAdditional Guidelines:\n{request.additional_prompts}"
            
        # Add reminder for JSON output
        prompt += "\n\nRemember to format your response as valid JSON with the structure provided in the system message."
        
        return prompt.strip()
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def _call_openai_api(self, system_prompt: str, user_prompt: str) -> Dict[str, Any]:
        """Call the OpenAI API with retry logic."""
        try:
            response = await self.client.chat.completions.create(
                model=self.MODEL,
                temperature=self.TEMPERATURE,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=self.MAX_TOKENS,
                response_format={"type": "json_object"}
            )
            
            # Extract and parse JSON content from response
            content = response.choices[0].message.content
            return json.loads(content)
            
        except Exception as e:
            logger.error(f"Error calling OpenAI API: {str(e)}")
            raise
    
    async def _generate_illustration_prompts(self, story_content: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance illustration prompts with more details if needed."""
        # This could be expanded later to generate more detailed prompts
        # For now, we'll just return the original content with basic validation
        
        # Ensure each chapter has an illustration prompt
        for chapter in story_content.get("chapters", []):
            if not chapter.get("illustration_prompt"):
                chapter["illustration_prompt"] = f"Illustration for chapter: {chapter.get('title', 'Untitled')}"
        
        return story_content
    
    async def _content_filter(self, story_content: Dict[str, Any]) -> Tuple[Dict[str, Any], bool, str]:
        """Filter content for age-appropriateness and quality."""
        # This would be expanded with more sophisticated filtering
        # For now, implement a basic check
        
        content_issues = []
        filtered_content = story_content.copy()
        
        # Check for problematic words or phrases
        problematic_terms = ["die", "death", "kill", "blood", "scary", "monster", "gun", "weapon"]
        
        # Check each chapter for problematic content
        for i, chapter in enumerate(filtered_content.get("chapters", [])):
            content = chapter.get("content", "").lower()
            
            for term in problematic_terms:
                if term in content:
                    content_issues.append(f"Chapter {i+1} contains problematic term: {term}")
                    # Replace with more age-appropriate wording
                    modified_content = chapter["content"]
                    # This is a simplistic approach; would need more sophisticated processing
                    # in a production environment
                    modified_content = modified_content.replace(term, "[age-appropriate term]")
                    chapter["content"] = modified_content
        
        has_issues = len(content_issues) > 0
        issues_summary = "\n".join(content_issues) if has_issues else "No content issues detected."
        
        return filtered_content, has_issues, issues_summary
    
    async def generate_story(self, request: StoryGenerationRequest) -> Dict[str, Any]:
        """
        Generate a children's book story based on the provided request.
        
        Args:
            request: The story generation request containing metadata and characters
            
        Returns:
            A dictionary containing the generated story content
        """
        logger.info(f"Generating story: {request.metadata.title}")
        
        # Build prompts
        system_prompt = await self._build_system_prompt(request)
        user_prompt = await self._build_user_prompt(request)
        
        logger.debug(f"System prompt: {system_prompt[:100]}...")
        logger.debug(f"User prompt: {user_prompt[:100]}...")
        
        try:
            # Call OpenAI API
            raw_story = await self._call_openai_api(system_prompt, user_prompt)
            
            # Generate/enhance illustration prompts
            story_with_illustrations = await self._generate_illustration_prompts(raw_story)
            
            # Apply content filtering
            filtered_story, has_issues, issues_summary = await self._content_filter(story_with_illustrations)
            
            if has_issues:
                logger.warning(f"Content issues detected: {issues_summary}")
            
            # Add metadata to the story
            result = {
                **filtered_story,
                "metadata": {
                    "title": request.metadata.title,
                    "author": request.metadata.author,
                    "age_group": request.metadata.age_group.value,
                    "book_type": request.metadata.book_type.value,
                    "theme": request.metadata.theme,
                    "educational_focus": request.metadata.educational_focus,
                    "generated_at": "2025-05-07T12:40:24+02:00",  # Use current time
                    "content_filtered": has_issues,
                },
                "characters": [c.dict() for c in request.characters] if request.characters else []
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Error generating story: {str(e)}")
            # Fallback to a basic placeholder in case of API failure
            return {
                "title": request.metadata.title,
                "chapters": [
                    {
                        "title": "Chapter 1: Introduction",
                        "content": "Once upon a time, there was a wonderful adventure waiting to happen.",
                        "illustration_prompt": "A colorful landscape with hills, trees, and a bright sky."
                    }
                ],
                "characters": [c.dict() for c in request.characters],
                "moral_lesson": "Every story teaches us something new.",
                "error": str(e)
            }


# Create a singleton instance for use in the application
story_generator = StoryGenerator()
