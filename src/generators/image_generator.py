"""
Image Generator module for Kids Book Generator.

This module handles the generation of illustrations using OpenAI's DALL-E 3.
It implements style consistency and age-appropriate content filters.
"""
import os
import io
import json
import logging
import asyncio
import time
from typing import Dict, List, Optional, Any, Tuple, BinaryIO, Union
from pathlib import Path
import uuid
from datetime import datetime

import openai
import httpx
from PIL import Image, ImageDraw, ImageFilter
from tenacity import retry, stop_after_attempt, wait_exponential

from src.api.models import ImageGenerationRequest, BookType, AgeGroup
from src.config import settings
from src.utils.logging import get_logger


logger = get_logger(__name__)


class ImageGenerator:
    """
    Image generation service using OpenAI's DALL-E 3.
    
    This class handles the generation of high-quality book illustrations with
    consistent style and age-appropriate content.
    """
    
    def __init__(self):
        """Initialize the image generator with configuration settings."""
        self.api_key = settings.OPENAI_API_KEY
        # Initialize OpenAI client
        self.client = openai.AsyncOpenAI(api_key=self.api_key)
        
        # Set up output directories
        self.output_dir = Path(settings.STORAGE_DIR) / "images"
        self.coloring_dir = Path(settings.STORAGE_DIR) / "coloring"
        
        # Create output directories if they don't exist
        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(self.coloring_dir, exist_ok=True)
        
        # DALL-E 3 configuration
        self.MODEL = "dall-e-3"
        self.QUALITY = "hd"  # Using high-definition quality for print
        self.SIZE = "1024x1024"  # Base size - will be adjusted based on book dimensions
        
        # Style presets for different age groups
        self.AGE_GROUP_STYLES = {
            AgeGroup.TODDLER: "Bright, simple, cartoon style with bold outlines. Cheerful colors and minimal details. Very friendly and approachable characters with exaggerated features.",
            AgeGroup.PRESCHOOL: "Colorful, friendly, slightly more detailed cartoon style. Cute characters with clear emotions. Simplified backgrounds with recognizable elements.",
            AgeGroup.EARLY_READER: "Semi-realistic, detailed cartoon style. Diverse characters with clear expressions. More detailed backgrounds with environmental context.",
            AgeGroup.MIDDLE_GRADE: "More sophisticated illustration style with attention to detail. Characters with nuanced expressions. Detailed backgrounds that enhance the story context."
        }
        
        # Content safety filters
        self.PROHIBITED_CONTENT = [
            "scary", "violent", "blood", "weapon", "adult content", 
            "drug", "alcohol", "cigarette", "political figure", 
            "religious symbol", "brand logo", "trademarked character"
        ]
    
    async def _enhance_prompt(self, prompt: str, style: Optional[str] = None, age_group: Optional[AgeGroup] = None) -> str:
        """
        Enhance a base prompt with style guidance and quality instructions.
        
        Args:
            prompt: The base illustration prompt
            style: Optional style descriptor for the illustration
            age_group: Optional age group to use default style
            
        Returns:
            An enhanced prompt for DALL-E 3
        """
        # Start with the base prompt
        enhanced_prompt = prompt.strip()
        
        # Add age-appropriate style if age_group is provided and no custom style
        if not style and age_group and age_group in self.AGE_GROUP_STYLES:
            style = self.AGE_GROUP_STYLES[age_group]
        
        # Add style guidance if provided
        if style:
            enhanced_prompt += f" Illustration style: {style}"
        else:
            # Default style for children's book illustrations if no style provided
            enhanced_prompt += " Illustration in a colorful, friendly children's book style with clean lines and vibrant colors."
        
        # Add quality and detail guidance for book printing
        enhanced_prompt += " The image should be detailed, high quality, well-lit, and suitable for a children's book."
        enhanced_prompt += " Clear composition with no text or words in the image."
        
        # Add negative prompt to avoid prohibited content
        enhanced_prompt += " Please ensure the image is completely child-appropriate with no scary, violent, or adult content."
        
        return enhanced_prompt
    
    async def _validate_prompt(self, prompt: str) -> Tuple[bool, str]:
        """
        Validate the prompt for child-appropriate content.
        
        Args:
            prompt: The prompt to validate
            
        Returns:
            Tuple of (is_valid, reason)
        """
        prompt_lower = prompt.lower()
        
        # Check for prohibited content
        for term in self.PROHIBITED_CONTENT:
            if term in prompt_lower:
                return False, f"Prompt contains prohibited content: {term}"
        
        return True, "Prompt is valid"
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def _generate_dalle_image(self, prompt: str) -> Tuple[bytes, Dict[str, Any]]:
        """
        Generate an image using DALL-E 3.
        
        Args:
            prompt: The enhanced prompt
            
        Returns:
            Tuple of (image_data, metadata)
        """
        try:
            # Call OpenAI API
            response = await self.client.images.generate(
                model=self.MODEL,
                prompt=prompt,
                size=self.SIZE,
                quality=self.QUALITY,
                n=1,
                response_format="b64_json"
            )
            
            # Extract image data and metadata
            image_data = response.data[0].b64_json
            image_bytes = openai.util.convert_to_bytes(image_data)
            
            # Return image data and metadata
            return image_bytes, {
                "prompt": prompt,
                "model": self.MODEL,
                "size": self.SIZE,
                "quality": self.QUALITY,
                "created": response.created
            }
            
        except Exception as e:
            logger.error(f"Error generating image with DALL-E: {str(e)}")
            raise
    
    async def _save_image(self, image_data: bytes, filename: Optional[str] = None) -> str:
        """
        Save image data to file system.
        
        Args:
            image_data: Image bytes
            filename: Optional filename to use
            
        Returns:
            Path to saved image
        """
        # Generate a unique filename if none provided
        if not filename:
            timestamp = int(time.time())
            unique_id = str(uuid.uuid4())[:8]
            filename = f"image_{timestamp}_{unique_id}.png"
        
        # Ensure filename has .png extension
        if not filename.lower().endswith(".png"):
            filename += ".png"
        
        # Create full path
        image_path = self.output_dir / filename
        
        # Save the image
        try:
            with open(image_path, "wb") as f:
                f.write(image_data)
            logger.info(f"Image saved to: {image_path}")
            return str(image_path)
        except Exception as e:
            logger.error(f"Error saving image: {str(e)}")
            raise
    
    async def generate_image(self, request: ImageGenerationRequest) -> Dict[str, Any]:
        """
        Generate an illustration based on the provided request.
        
        Args:
            request: The image generation request containing prompt and style
            
        Returns:
            A dictionary containing the generated image metadata and paths
        """
        logger.info(f"Generating image: {request.prompt[:50]}...")
        
        # Validate prompt
        is_valid, reason = await self._validate_prompt(request.prompt)
        if not is_valid:
            logger.warning(f"Invalid prompt: {reason}")
            return {
                "error": reason,
                "status": "failed",
                "prompt": request.prompt
            }
        
        # Enhance prompt
        enhanced_prompt = await self._enhance_prompt(request.prompt, request.style)
        logger.debug(f"Enhanced prompt: {enhanced_prompt[:100]}...")
        
        try:
            # Generate image
            image_data, metadata = await self._generate_dalle_image(enhanced_prompt)
            
            # Generate filename based on prompt
            prompt_slug = "_".join(request.prompt.lower().split()[:5])
            prompt_slug = "".join(c if c.isalnum() or c == "_" else "_" for c in prompt_slug)[:30]
            timestamp = int(time.time())
            filename = f"{prompt_slug}_{timestamp}.png"
            
            # Save image
            image_path = await self._save_image(image_data, filename)
            
            # Return result
            return {
                "prompt": request.prompt,
                "enhanced_prompt": enhanced_prompt,
                "image_path": image_path,
                "width": request.width,
                "height": request.height,
                "generated": True,
                "metadata": metadata,
                "created_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error generating image: {str(e)}")
            
            # Return error response
            return {
                "prompt": request.prompt,
                "enhanced_prompt": enhanced_prompt,
                "error": str(e),
                "generated": False,
                "width": request.width,
                "height": request.height
            }
    
    async def _process_image_to_line_art(self, image_path: Union[str, Path]) -> Tuple[bytes, Dict[str, Any]]:
        """
        Process an image to convert it to line art for coloring pages.
        
        Args:
            image_path: Path to the source image
            
        Returns:
            Tuple of (processed_image_data, metadata)
        """
        # Convert path to Path object if string
        if isinstance(image_path, str):
            image_path = Path(image_path)
        
        try:
            # Open the image
            img = Image.open(image_path)
            
            # Convert to grayscale
            gray = img.convert('L')
            
            # Apply edge detection - this is a simple implementation
            # A more sophisticated approach would use dedicated libraries like OpenCV
            edges = gray.filter(ImageFilter.FIND_EDGES)
            
            # Enhance edges and invert (for black lines on white)
            edges = edges.point(lambda x: 255 if x < 128 else 0)
            
            # Save to bytes
            buffer = io.BytesIO()
            edges.save(buffer, format="PNG")
            line_art_data = buffer.getvalue()
            
            return line_art_data, {
                "source_image": str(image_path),
                "conversion_method": "edge_detection",
                "format": "PNG"
            }
            
        except Exception as e:
            logger.error(f"Error processing image to line art: {str(e)}")
            raise
    
    async def convert_to_coloring_page(self, image_path: str) -> str:
        """
        Convert a full-color illustration to a coloring page.
        
        Args:
            image_path: Path to the source illustration
            
        Returns:
            Path to the generated coloring page
        """
        logger.info(f"Converting image to coloring page: {image_path}")
        
        try:
            # Process the image
            line_art_data, metadata = await self._process_image_to_line_art(image_path)
            
            # Generate output filename
            source_path = Path(image_path)
            coloring_filename = f"coloring_{source_path.stem}.png"
            coloring_path = self.coloring_dir / coloring_filename
            
            # Save the coloring page
            with open(coloring_path, "wb") as f:
                f.write(line_art_data)
                
            logger.info(f"Coloring page saved to: {coloring_path}")
            return str(coloring_path)
            
        except Exception as e:
            logger.error(f"Failed to convert image to coloring page: {str(e)}")
            # Return the original path if conversion fails
            return image_path
    
    async def batch_generate_coloring_book(self, prompts: List[str], style: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate a batch of coloring pages from prompts.
        
        Args:
            prompts: List of prompts for generating images
            style: Optional common style for all images
            
        Returns:
            Dictionary with paths to generated coloring pages
        """
        logger.info(f"Generating coloring book with {len(prompts)} pages")
        
        results = []
        for i, prompt in enumerate(prompts):
            try:
                # Generate regular image
                request = ImageGenerationRequest(
                    prompt=prompt,
                    style=style,
                    width=1024,
                    height=1024
                )
                image_result = await self.generate_image(request)
                
                if image_result.get("generated", False):
                    # Convert to coloring page
                    coloring_path = await self.convert_to_coloring_page(image_result["image_path"])
                    
                    results.append({
                        "page_number": i + 1,
                        "prompt": prompt,
                        "image_path": image_result["image_path"],
                        "coloring_path": coloring_path,
                        "success": True
                    })
                else:
                    # Image generation failed
                    results.append({
                        "page_number": i + 1,
                        "prompt": prompt,
                        "error": image_result.get("error", "Unknown error"),
                        "success": False
                    })
                    
                # Be nice to the API with a small delay between requests
                await asyncio.sleep(1)
                
            except Exception as e:
                logger.error(f"Error generating coloring page {i+1}: {str(e)}")
                results.append({
                    "page_number": i + 1,
                    "prompt": prompt,
                    "error": str(e),
                    "success": False
                })
        
        return {
            "total_pages": len(prompts),
            "successful_pages": sum(1 for r in results if r.get("success", False)),
            "pages": results
        }


# Create a singleton instance for use in the application
image_generator = ImageGenerator()
