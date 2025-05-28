#!/usr/bin/env python3
"""
NudeNet-based nudity detection module

This module provides real nudity detection using the pre-trained NudeNet model
"""

import io
import logging
from typing import Dict, List, Tuple
from PIL import Image
import numpy as np

logger = logging.getLogger(__name__)

class NudityDetector:
    """Nudity detection using NudeNet"""
    
    def __init__(self):
        self.detector = None
        self._init_models()
    
    def _init_models(self):
        """Initialize NudeNet models"""
        try:
            from nudenet import NudeDetector
            
            logger.info("🔥 Initializing NudeNet detector...")
            
            # Initialize detector (gives detailed analysis)
            self.detector = NudeDetector()
            logger.info("✅ NudeNet detector loaded")
            
            self.models_available = True
            
        except ImportError as e:
            logger.error(f"❌ NudeNet not available: {e}")
            self.models_available = False
        except Exception as e:
            logger.error(f"❌ Error loading NudeNet: {e}")
            self.models_available = False
    
    def analyze_image(self, image_data: bytes, use_detailed_analysis: bool = True) -> Dict:
        """
        Analyze image for nudity content
        
        Args:
            image_data: Raw image bytes
            use_detailed_analysis: Whether to use detailed detection (slower but more accurate)
            
        Returns:
            Dict with analysis results
        """
        if not self.models_available:
            return self._fallback_analysis()
        
        try:
            # Save image temporarily for NudeNet
            image = Image.open(io.BytesIO(image_data))
            temp_path = "temp_image.jpg"
            image.save(temp_path, "JPEG")
            
            # Use NudeDetector for analysis
            result = self._detailed_analysis(temp_path)
            
            # Clean up temp file
            import os
            if os.path.exists(temp_path):
                os.remove(temp_path)
            
            return result
            
        except Exception as e:
            logger.error(f"Error in nudity analysis: {e}")
            return self._fallback_analysis()
    
    def _detailed_analysis(self, image_path: str) -> Dict:
        """Detailed analysis using NudeDetector"""
        try:
            # Get detection results
            detections = self.detector.detect(image_path)
            
            # Analyze detected parts
            nude_parts = []
            total_confidence = 0.0
            num_detections = 0
            safe_parts = 0
            
            # NudeNet classes that indicate nudity (updated to match actual NudeNet output)
            nude_classes = [
                'EXPOSED_ANUS', 'ARMPITS_EXPOSED', 'BELLY_EXPOSED',
                'FEMALE_BREAST_EXPOSED', 'MALE_BREAST_EXPOSED', 'BUTTOCKS_EXPOSED',
                'FEMALE_GENITALIA_EXPOSED', 'MALE_GENITALIA_EXPOSED', 'THIGHS_EXPOSED'
            ]
            
            # Safe classes (updated to match actual NudeNet output)
            safe_classes = [
                'FEMALE_BREAST_COVERED', 'MALE_BREAST_COVERED', 'BUTTOCKS_COVERED',
                'FEMALE_GENITALIA_COVERED', 'MALE_GENITALIA_COVERED', 'FACE_FEMALE', 'FACE_MALE',
                'HAND', 'FOOT_EXPOSED', 'ARM', 'LEG'
            ]
            
            for detection in detections:
                class_name = detection['class']
                confidence = detection['score']
                
                if class_name in nude_classes and confidence > 0.25:  # Lowered threshold to 25%
                    nude_parts.append({
                        'part': class_name,
                        'confidence': confidence,
                        'bbox': detection['box']
                    })
                    total_confidence += confidence
                    num_detections += 1
                elif class_name in safe_classes and confidence > 0.25:
                    safe_parts += 1
            
            # Calculate overall nudity score
            if num_detections > 0:
                avg_confidence = total_confidence / num_detections
                # Boost confidence if multiple nude parts detected
                boosted_confidence = min(1.0, avg_confidence * (1 + 0.1 * (num_detections - 1)))
                is_nude = boosted_confidence > 0.3  # Lowered threshold to 30%
            else:
                # If NudeNet found no nude parts, try backup skin detection
                boosted_confidence = self._backup_skin_detection(image_path)
                is_nude = boosted_confidence > 0.3
            
            # Calculate equivalent safe/unsafe scores for compatibility
            if is_nude:
                unsafe_score = boosted_confidence
                safe_score = 1.0 - boosted_confidence
            else:
                safe_score = 1.0 - boosted_confidence
                unsafe_score = boosted_confidence
            
            logger.info(f"Detailed analysis: {num_detections} nude parts, {safe_parts} safe parts, confidence={boosted_confidence:.3f}")
            
            return {
                'method': 'detector',
                'is_nude': is_nude,
                'confidence': float(boosted_confidence),
                'safe_score': float(safe_score),
                'unsafe_score': float(unsafe_score),
                'nude_parts_count': num_detections,
                'nude_parts': nude_parts,
                'details': {
                    'all_detections': len(detections),
                    'nude_detections': num_detections,
                    'safe_detections': safe_parts,
                    'avg_confidence': float(total_confidence / max(1, num_detections))
                }
            }
            
        except Exception as e:
            logger.error(f"Error in detailed analysis: {e}")
            return self._fallback_analysis()
    
    def _backup_skin_detection(self, image_path: str) -> float:
        """Backup skin-based nudity detection when NudeNet finds no body parts"""
        try:
            from PIL import Image
            import numpy as np
            
            # Load image
            image = Image.open(image_path)
            image_array = np.array(image)
            
            # Convert to RGB if needed
            if len(image_array.shape) == 3 and image_array.shape[2] == 3:
                # Calculate skin-like pixels
                skin_confidence = self._calculate_skin_exposure(image_array)
                
                if skin_confidence > 0.4:  # High skin exposure
                    logger.info(f"Backup skin detection: {skin_confidence:.3f} skin exposure detected")
                    return min(0.8, skin_confidence)  # Cap at 80%
                else:
                    logger.info(f"Backup skin detection: {skin_confidence:.3f} skin exposure (low)")
                    return skin_confidence * 0.5  # Reduce confidence for low skin exposure
            
            return 0.0
            
        except Exception as e:
            logger.error(f"Error in backup skin detection: {e}")
            return 0.0
    
    def _calculate_skin_exposure(self, image_array: np.ndarray) -> float:
        """Calculate the amount of skin-like pixels in the image"""
        try:
            # Define skin color ranges in RGB
            # These ranges cover various skin tones
            skin_ranges = [
                # Light skin tones
                ([180, 120, 90], [255, 200, 170]),
                # Medium skin tones  
                ([120, 80, 50], [200, 150, 120]),
                # Darker skin tones
                ([80, 50, 30], [150, 100, 80]),
                # Pink/red tones
                ([200, 150, 140], [255, 220, 200])
            ]
            
            total_pixels = image_array.shape[0] * image_array.shape[1]
            skin_pixels = 0
            
            for lower, upper in skin_ranges:
                # Create mask for this skin range
                mask = np.all((image_array >= lower) & (image_array <= upper), axis=2)
                skin_pixels += np.sum(mask)
            
            skin_ratio = skin_pixels / total_pixels
            
            # Additional checks for nudity indicators
            # Check for large connected skin regions
            if skin_ratio > 0.3:  # More than 30% skin
                # Look for body-like proportions
                height, width = image_array.shape[:2]
                aspect_ratio = height / width
                
                # Typical body proportions
                if 1.2 <= aspect_ratio <= 2.5:  # Portrait orientation with body proportions
                    skin_ratio *= 1.3  # Boost confidence
                elif 0.4 <= aspect_ratio <= 0.8:  # Landscape orientation
                    skin_ratio *= 1.1  # Slight boost
            
            return min(1.0, skin_ratio)
            
        except Exception as e:
            logger.error(f"Error calculating skin exposure: {e}")
            return 0.0
    
    def _fallback_analysis(self) -> Dict:
        """Fallback when NudeNet is not available"""
        return {
            'method': 'fallback',
            'is_nude': False,
            'confidence': 0.05,  # Very low confidence
            'safe_score': 0.95,
            'unsafe_score': 0.05,
            'details': {
                'message': 'NudeNet not available, using fallback'
            }
        }

# Global instance
nudity_detector = NudityDetector()

def detect_nudity(image_data: bytes, detailed: bool = True) -> Dict:
    """
    Convenience function for nudity detection
    
    Args:
        image_data: Raw image bytes
        detailed: Whether to use detailed analysis
        
    Returns:
        Dict with detection results
    """
    return nudity_detector.analyze_image(image_data, detailed) 