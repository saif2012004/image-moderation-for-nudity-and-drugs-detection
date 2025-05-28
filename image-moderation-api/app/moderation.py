import io
import hashlib
from typing import List, Optional
from datetime import datetime
from PIL import Image
import numpy as np

from .models import ModerationResult, ModerationCategory

class ModerationService:
    """Image moderation service for content analysis"""
    
    def __init__(self):
        # Define moderation categories
        self.categories = [
            "nudity",
            "drugs"
        ]
    
    async def moderate_image(self, image_data: bytes, filename: str) -> ModerationResult:
        """
        Analyze an image for harmful content
        This is a mock implementation - in production you would use:
        - AWS Rekognition
        - Google Cloud Vision AI
        - Azure Computer Vision
        - Custom ML models
        """
        try:
            # Validate image
            image = Image.open(io.BytesIO(image_data))
            
            # Mock moderation analysis
            categories = await self._analyze_categories(image_data, image)
            
            # Determine overall safety
            flagged_categories = [cat for cat in categories if cat.flagged]
            is_safe = len(flagged_categories) == 0
            
            # Calculate overall confidence (average of all category confidences)
            overall_confidence = sum(cat.confidence for cat in categories) / len(categories)
            
            return ModerationResult(
                filename=filename,
                safe=is_safe,
                categories=categories,
                overall_confidence=overall_confidence,
                timestamp=datetime.utcnow()
            )
            
        except Exception as e:
            # If image processing fails, flag as unsafe with all categories flagged
            return ModerationResult(
                filename=filename,
                safe=False,
                categories=[
                    ModerationCategory(
                        category=cat,
                        confidence=1.0,
                        flagged=True
                    ) for cat in self.categories
                ],
                overall_confidence=1.0,
                timestamp=datetime.utcnow()
            )
    
    async def _analyze_categories(self, image_data: bytes, image: Image.Image) -> List[ModerationCategory]:
        """
        Mock analysis of different content categories
        In production, this would use real ML models
        """
        categories = []
        
        # Generate deterministic "analysis" based on image hash
        image_hash = hashlib.md5(image_data).hexdigest()
        hash_int = int(image_hash[:8], 16)
        
        for i, category in enumerate(self.categories):
            # Use hash to generate pseudo-random but deterministic results
            seed = (hash_int + i * 1000) % 1000000
            confidence = (seed % 100) / 100.0  # 0.0 to 1.0
            
            # Flag as unsafe if confidence > 0.8 for demonstration
            flagged = confidence > 0.8
            
            categories.append(ModerationCategory(
                category=category,
                confidence=confidence,
                flagged=flagged
            ))
        
        # Additional analysis based on image properties
        width, height = image.size
        aspect_ratio = width / height if height > 0 else 1
        
        # Enhanced analysis for specific categories
        # Check for potential drug-related content (white powdery substances)
        img_array = np.array(image)
        mean_brightness = np.mean(img_array)
        if mean_brightness > 200:  # Very bright/white images
            drugs_category = next((cat for cat in categories if cat.category == "drugs"), None)
            if drugs_category and drugs_category.confidence < 0.7:
                drugs_category.confidence = min(0.85, drugs_category.confidence * 1.5)
                drugs_category.flagged = drugs_category.confidence > 0.7
        
        return categories
    
    def _extract_image_features(self, image: Image.Image) -> dict:
        """Extract basic image features for analysis"""
        # Convert to RGB if needed
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Convert to numpy array
        img_array = np.array(image)
        
        # Basic features
        features = {
            "width": image.size[0],
            "height": image.size[1],
            "aspect_ratio": image.size[0] / image.size[1] if image.size[1] > 0 else 1,
            "mean_brightness": np.mean(img_array),
            "dominant_color": self._get_dominant_color(img_array),
        }
        
        return features
    
    def _get_dominant_color(self, img_array: np.ndarray) -> tuple:
        """Get the dominant color in the image"""
        # Reshape to list of pixels
        pixels = img_array.reshape(-1, 3)
        
        # Calculate mean color
        mean_color = np.mean(pixels, axis=0)
        
        return tuple(map(int, mean_color)) 