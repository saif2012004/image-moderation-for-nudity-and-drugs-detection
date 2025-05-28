#!/usr/bin/env python3
"""
Simplified image moderation service with AI-powered detection

This module provides image moderation for nudity and drugs only
"""

import io
import logging
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
from PIL import Image

from .models import ModerationResult, ModerationCategory

# Import the real nudity detector
try:
    from .nudity_detector import detect_nudity
    NUDENET_AVAILABLE = True
    logging.info("✅ NudeNet-based nudity detection available")
except ImportError as e:
    NUDENET_AVAILABLE = False
    logging.warning(f"⚠️ NudeNet not available: {e}")

# Import AI drugs detector
from .drugs_detector import detect_drugs

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Moderation categories - SIMPLIFIED: Only nudity and drugs
MODERATION_CATEGORIES = ["nudity", "drugs"]

# Detection thresholds for each category
DETECTION_THRESHOLDS = {
    "nudity": 0.3,   # 30% threshold for nudity (using NudeNet)
    "drugs": 0.5,    # 50% threshold for drugs (using AI computer vision)
}

class ModerationService:
    """Simplified AI-powered image moderation service for nudity and drugs only"""
                                        
    def __init__(self):
        # Define moderation categories - SIMPLIFIED: Only nudity and drugs
        self.categories = MODERATION_CATEGORIES  # ["nudity", "drugs"]
        
        logging.info("🚀 Simplified moderation service initialized (nudity + drugs only)")
        if NUDENET_AVAILABLE:
            logging.info("✅ Using NudeNet for nudity detection")
        else:
            logging.info("⚠️ Using fallback nudity detection")
        
        logging.info("✅ Using AI computer vision for drugs detection")
    
    async def moderate_image(self, image_data: bytes, filename: str) -> ModerationResult:
        """
        Analyze an image for nudity and drugs content
        """
        try:
            # Validate image
            image = Image.open(io.BytesIO(image_data))
            logger.info(f"Processing image: {filename} ({image.size})")
            
            # Analyze for each category
            categories = await self._analyze_categories(image, image_data, filename)
            
            # Determine overall safety
            flagged_categories = [cat for cat in categories if cat.flagged]
            is_safe = len(flagged_categories) == 0
            
            # Calculate overall confidence
            overall_confidence = sum(cat.confidence for cat in categories) / len(categories)
            
            logger.info(f"Analysis complete for {filename}: safe={is_safe}, confidence={overall_confidence:.2f}")
            
            return ModerationResult(
                filename=filename,
                safe=is_safe,
                categories=categories,
                overall_confidence=overall_confidence,
                timestamp=datetime.now(timezone.utc)
            )
            
        except Exception as e:
            logger.error(f"Error processing {filename}: {e}")
            # If processing fails, return conservative result
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
                timestamp=datetime.now(timezone.utc)
            )
    
    async def _analyze_categories(self, image: Image.Image, image_data: bytes, filename: str) -> List[ModerationCategory]:
        """
        Analyze image for nudity and drugs categories only
        """
        categories = []
        
        for category in self.categories:
            if category == "nudity":
                # Use real NudeNet detection
                confidence = await self._detect_nudity_real(image_data, filename)
            elif category == "drugs":
                # Use real AI drugs detection
                confidence = await self._detect_drugs_real(image_data, filename)
            else:
                # This shouldn't happen with our simplified categories
                logger.warning(f"Unknown category: {category}")
                confidence = 0.05
            
            # Determine if flagged based on thresholds
            flagged = self._should_flag(category, confidence)
            
            categories.append(ModerationCategory(
                category=category,
                confidence=confidence,
                flagged=flagged
            ))
        
        return categories
    
    async def _detect_nudity_real(self, image_data: bytes, filename: str) -> float:
        """
        Real nudity detection using NudeNet
        """
        if not NUDENET_AVAILABLE:
            logger.warning(f"NudeNet not available for {filename}, using fallback")
            return 0.05  # Very conservative fallback
        
        try:
            # Use NudeNet for real detection
            result = detect_nudity(image_data, detailed=True)
            
            confidence = result.get('confidence', 0.0)
            is_nude = result.get('is_nude', False)
            method = result.get('method', 'unknown')
            
            logger.info(f"Nudity detection for {filename}: method={method}, nude={is_nude}, confidence={confidence:.3f}")
            
            # Log detailed results if available
            if 'nude_parts_count' in result:
                parts_count = result['nude_parts_count']
                logger.info(f"  └─ Detected {parts_count} nude parts")
            
            return confidence
            
        except Exception as e:
            logger.error(f"Error in nudity detection for {filename}: {e}")
            return 0.05  # Conservative fallback
    
    async def _detect_drugs_real(self, image_data: bytes, filename: str) -> float:
        """
        Real drugs detection using AI computer vision
        """
        try:
            # Use AI drugs detection
            result = detect_drugs(image_data, detailed=True)
            
            confidence = result.get('confidence', 0.0)
            is_drugs = result.get('is_drugs', False)
            method = result.get('method', 'unknown')
            
            logger.info(f"Drugs detection for {filename}: method={method}, drugs={is_drugs}, confidence={confidence:.3f}")
            
            # Log detailed results if available
            if 'detections' in result:
                detections = result['detections']
                logger.info(f"  └─ Pills: {detections.get('pills', 0):.3f}, Powder: {detections.get('powder', 0):.3f}")
            
            return confidence
            
        except Exception as e:
            logger.error(f"Error in real drugs detection for {filename}: {e}")
            return 0.05  # Conservative fallback
    
    def _should_flag(self, category: str, confidence: float) -> bool:
        """
        Determine if content should be flagged based on confidence and category
        Using the simplified threshold configuration
        """
        threshold = DETECTION_THRESHOLDS.get(category, 0.75)  # Default 75% if not found
        return confidence > threshold

# Global moderation service instance
moderation_service = ModerationService() 