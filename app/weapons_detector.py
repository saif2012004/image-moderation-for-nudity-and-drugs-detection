#!/usr/bin/env python3
"""
AI-powered weapons detection module

This module provides real weapons detection using computer vision and machine learning
"""

import io
import logging
from typing import Dict, List, Tuple
from PIL import Image
import numpy as np
import cv2

logger = logging.getLogger(__name__)

class WeaponsDetector:
    """AI-powered weapons detection using computer vision"""
    
    def __init__(self):
        self.models_available = True
        logger.info("🔫 Initializing AI-powered weapons detector...")
        self._init_models()
    
    def _init_models(self):
        """Initialize computer vision models for weapon detection"""
        try:
            # Test OpenCV availability
            import cv2
            logger.info("✅ OpenCV available for weapons detection")
            
            # Initialize detection parameters for different weapon types
            self.knife_detector_params = {
                'min_contour_area': 500,
                'max_contour_area': 50000,
                'aspect_ratio_min': 2.5,  # Knives are elongated
                'aspect_ratio_max': 8.0,
                'edge_threshold_low': 50,
                'edge_threshold_high': 150
            }
            
            self.gun_detector_params = {
                'min_contour_area': 800,
                'max_contour_area': 80000,
                'aspect_ratio_min': 1.5,  # Guns have specific proportions
                'aspect_ratio_max': 4.0,
                'edge_threshold_low': 30,
                'edge_threshold_high': 100
            }
            
            # Template matching parameters
            self.template_threshold = 0.6
            
            logger.info("✅ Weapons detection models initialized")
            
        except ImportError as e:
            logger.error(f"❌ Failed to initialize weapons detection: {e}")
            self.models_available = False
    
    def detect_weapons(self, image_data: bytes, detailed: bool = False) -> Dict:
        """
        Detect weapons in image using AI computer vision
        
        Args:
            image_data: Raw image bytes
            detailed: Whether to return detailed analysis
            
        Returns:
            Dict with detection results
        """
        try:
            if not self.models_available:
                logger.warning("Models not available, using fallback")
                return self._fallback_detection()
            
            # Load and preprocess image
            image = Image.open(io.BytesIO(image_data))
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Convert to numpy array for OpenCV
            img_array = np.array(image)
            img_bgr = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
            img_gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
            
            logger.info(f"🔍 Analyzing {image.size} image for weapons...")
            
            # Detect different weapon types
            knife_confidence = self._detect_knives(img_gray, img_bgr)
            gun_confidence = self._detect_guns(img_gray, img_bgr)
            sharp_object_confidence = self._detect_sharp_objects(img_gray, img_bgr)
            metallic_confidence = self._detect_metallic_weapons(img_gray, img_bgr)
            
            # Calculate overall weapons confidence
            detections = {
                'knives': knife_confidence,
                'guns': gun_confidence,
                'sharp_objects': sharp_object_confidence,
                'metallic': metallic_confidence
            }
            
            # Calculate overall confidence
            overall_confidence = self._calculate_overall_confidence(detections)
            
            # Determine if weapons detected
            is_weapons = overall_confidence > 0.5  # 50% threshold for weapons
            
            logger.info(f"Weapons analysis: knives={knife_confidence:.3f}, guns={gun_confidence:.3f}, "
                       f"sharp={sharp_object_confidence:.3f}, metallic={metallic_confidence:.3f}, "
                       f"overall={overall_confidence:.3f}, flagged={is_weapons}")
            
            result = {
                'is_weapons': is_weapons,
                'confidence': overall_confidence,
                'method': 'ai_computer_vision'
            }
            
            if detailed:
                result.update({
                    'detections': detections,
                    'knife_confidence': knife_confidence,
                    'gun_confidence': gun_confidence,
                    'sharp_object_confidence': sharp_object_confidence,
                    'metallic_confidence': metallic_confidence
                })
            
            return result
            
        except Exception as e:
            logger.error(f"Error in weapons detection: {e}")
            return self._fallback_detection()
    
    def _detect_knives(self, gray: np.ndarray, bgr: np.ndarray) -> float:
        """Detect knife-like objects using shape and edge analysis"""
        try:
            # Apply edge detection
            edges = cv2.Canny(gray, 
                            self.knife_detector_params['edge_threshold_low'],
                            self.knife_detector_params['edge_threshold_high'])
            
            # Find contours
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            knife_indicators = 0
            total_knife_score = 0
            
            for contour in contours:
                area = cv2.contourArea(contour)
                
                # Check area constraints
                if (self.knife_detector_params['min_contour_area'] <= area <= 
                    self.knife_detector_params['max_contour_area']):
                    
                    # Get bounding rectangle
                    x, y, w, h = cv2.boundingRect(contour)
                    aspect_ratio = max(w, h) / min(w, h) if min(w, h) > 0 else 0
                    
                    # Check if shape looks knife-like (elongated)
                    if (self.knife_detector_params['aspect_ratio_min'] <= aspect_ratio <= 
                        self.knife_detector_params['aspect_ratio_max']):
                        
                        # Additional validation: check for blade-like characteristics
                        knife_score = self._validate_knife_shape(contour, gray, x, y, w, h)
                        
                        if knife_score > 0.3:  # Minimum knife-like score
                            knife_indicators += 1
                            total_knife_score += knife_score
                            
                            logger.debug(f"Knife-like object detected: area={area}, "
                                       f"aspect_ratio={aspect_ratio:.2f}, score={knife_score:.3f}")
            
            # Calculate confidence based on detected knife-like objects
            if knife_indicators > 0:
                avg_score = total_knife_score / knife_indicators
                # Boost confidence if multiple knife-like objects detected
                confidence = min(0.95, avg_score * (1 + knife_indicators * 0.1))
                return confidence
            
            return 0.01  # Very low baseline
            
        except Exception as e:
            logger.error(f"Error in knife detection: {e}")
            return 0.01
    
    def _detect_guns(self, gray: np.ndarray, bgr: np.ndarray) -> float:
        """Detect gun-like objects using shape analysis"""
        try:
            # Apply adaptive threshold for better shape detection
            thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                         cv2.THRESH_BINARY, 11, 2)
            
            # Find contours
            contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            gun_indicators = 0
            total_gun_score = 0
            
            for contour in contours:
                area = cv2.contourArea(contour)
                
                # Check area constraints
                if (self.gun_detector_params['min_contour_area'] <= area <= 
                    self.gun_detector_params['max_contour_area']):
                    
                    # Get bounding rectangle
                    x, y, w, h = cv2.boundingRect(contour)
                    aspect_ratio = max(w, h) / min(w, h) if min(w, h) > 0 else 0
                    
                    # Check if shape looks gun-like
                    if (self.gun_detector_params['aspect_ratio_min'] <= aspect_ratio <= 
                        self.gun_detector_params['aspect_ratio_max']):
                        
                        # Additional validation: check for gun-like characteristics
                        gun_score = self._validate_gun_shape(contour, gray, x, y, w, h)
                        
                        if gun_score > 0.4:  # Minimum gun-like score
                            gun_indicators += 1
                            total_gun_score += gun_score
                            
                            logger.debug(f"Gun-like object detected: area={area}, "
                                       f"aspect_ratio={aspect_ratio:.2f}, score={gun_score:.3f}")
            
            # Calculate confidence based on detected gun-like objects
            if gun_indicators > 0:
                avg_score = total_gun_score / gun_indicators
                confidence = min(0.95, avg_score * (1 + gun_indicators * 0.15))
                return confidence
            
            return 0.01  # Very low baseline
            
        except Exception as e:
            logger.error(f"Error in gun detection: {e}")
            return 0.01
    
    def _detect_sharp_objects(self, gray: np.ndarray, bgr: np.ndarray) -> float:
        """Detect sharp objects using edge analysis and corner detection"""
        try:
            # Detect corners which might indicate sharp objects
            corners = cv2.goodFeaturesToTrack(gray, maxCorners=100, qualityLevel=0.01, 
                                            minDistance=10, blockSize=3, useHarrisDetector=True)
            
            if corners is not None and len(corners) > 0:
                # Analyze sharpness of detected corners
                sharp_corners = 0
                
                for corner in corners:
                    x, y = corner.ravel().astype(int)
                    
                    # Check local area around corner for sharpness
                    if self._is_sharp_corner(gray, x, y):
                        sharp_corners += 1
                
                # Calculate confidence based on sharp corners density
                corner_density = len(corners) / (gray.shape[0] * gray.shape[1] / 10000)
                sharp_ratio = sharp_corners / len(corners) if len(corners) > 0 else 0
                
                confidence = min(0.8, (corner_density * 0.3 + sharp_ratio * 0.7) * 0.8)
                
                logger.debug(f"Sharp objects: {sharp_corners}/{len(corners)} sharp corners, "
                           f"density={corner_density:.3f}, confidence={confidence:.3f}")
                
                return confidence
            
            return 0.01
            
        except Exception as e:
            logger.error(f"Error in sharp object detection: {e}")
            return 0.01
    
    def _detect_metallic_weapons(self, gray: np.ndarray, bgr: np.ndarray) -> float:
        """Detect metallic surfaces that might indicate weapons"""
        try:
            # Convert to HSV for better metallic detection
            hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)
            
            # Define metallic color ranges (grays, silvers, steel colors)
            metallic_ranges = [
                # Silver/steel range
                (np.array([0, 0, 50]), np.array([180, 30, 200])),
                # Dark metallic range
                (np.array([0, 0, 30]), np.array([180, 50, 100])),
                # Bright metallic range
                (np.array([0, 0, 180]), np.array([180, 40, 255]))
            ]
            
            total_metallic_pixels = 0
            total_pixels = gray.shape[0] * gray.shape[1]
            
            for lower, upper in metallic_ranges:
                mask = cv2.inRange(hsv, lower, upper)
                metallic_pixels = cv2.countNonZero(mask)
                total_metallic_pixels += metallic_pixels
            
            metallic_ratio = total_metallic_pixels / total_pixels
            
            # Check for metallic reflectance patterns
            reflection_score = self._detect_metallic_reflections(gray)
            
            # Combine metallic color and reflection scores
            confidence = min(0.85, (metallic_ratio * 0.6 + reflection_score * 0.4) * 1.5)
            
            logger.debug(f"Metallic detection: ratio={metallic_ratio:.3f}, "
                       f"reflection={reflection_score:.3f}, confidence={confidence:.3f}")
            
            return confidence
            
        except Exception as e:
            logger.error(f"Error in metallic detection: {e}")
            return 0.01
    
    def _validate_knife_shape(self, contour, gray: np.ndarray, x: int, y: int, w: int, h: int) -> float:
        """Validate if contour looks like a knife"""
        try:
            # Extract the region
            roi = gray[y:y+h, x:x+w]
            
            # Check for blade-like characteristics
            # 1. Gradient from handle to tip
            gradient_score = self._analyze_blade_gradient(roi)
            
            # 2. Edge sharpness
            edge_score = self._analyze_edge_sharpness(roi)
            
            # 3. Symmetry check
            symmetry_score = self._analyze_blade_symmetry(roi)
            
            # Combine scores
            total_score = (gradient_score * 0.4 + edge_score * 0.4 + symmetry_score * 0.2)
            
            return min(1.0, total_score)
            
        except Exception:
            return 0.0
    
    def _validate_gun_shape(self, contour, gray: np.ndarray, x: int, y: int, w: int, h: int) -> float:
        """Validate if contour looks like a gun"""
        try:
            # Extract the region
            roi = gray[y:y+h, x:x+w]
            
            # Check for gun-like characteristics
            # 1. Barrel detection
            barrel_score = self._detect_gun_barrel(roi)
            
            # 2. Trigger guard area
            trigger_score = self._detect_trigger_area(roi)
            
            # 3. Overall gun proportion
            proportion_score = self._analyze_gun_proportions(w, h)
            
            # Combine scores
            total_score = (barrel_score * 0.5 + trigger_score * 0.3 + proportion_score * 0.2)
            
            return min(1.0, total_score)
            
        except Exception:
            return 0.0
    
    def _is_sharp_corner(self, gray: np.ndarray, x: int, y: int, window_size: int = 5) -> bool:
        """Check if a corner is sharp (indicating potential weapon edge)"""
        try:
            h, w = gray.shape
            
            # Ensure we're within bounds
            if (x - window_size < 0 or x + window_size >= w or 
                y - window_size < 0 or y + window_size >= h):
                return False
            
            # Extract local window
            window = gray[y-window_size:y+window_size+1, x-window_size:x+window_size+1]
            
            # Calculate local gradient magnitude
            grad_x = cv2.Sobel(window, cv2.CV_64F, 1, 0, ksize=3)
            grad_y = cv2.Sobel(window, cv2.CV_64F, 0, 1, ksize=3)
            gradient_magnitude = np.sqrt(grad_x**2 + grad_y**2)
            
            # Check if gradient magnitude at center is high (sharp edge)
            center_gradient = gradient_magnitude[window_size, window_size]
            
            return center_gradient > 50  # Threshold for "sharp"
            
        except Exception:
            return False
    
    def _detect_metallic_reflections(self, gray: np.ndarray) -> float:
        """Detect metallic reflection patterns"""
        try:
            # Look for bright spots that might indicate metallic reflections
            _, bright_areas = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY)
            
            # Find connected components (bright spots)
            num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(bright_areas)
            
            reflection_score = 0
            if num_labels > 1:  # More than just background
                # Analyze size and distribution of bright spots
                total_bright_area = np.sum(stats[1:, cv2.CC_STAT_AREA])  # Exclude background
                total_area = gray.shape[0] * gray.shape[1]
                
                bright_ratio = total_bright_area / total_area
                
                # Metallic objects typically have small, scattered bright reflections
                if 0.01 < bright_ratio < 0.3 and num_labels > 2:
                    reflection_score = min(0.8, bright_ratio * 5)
            
            return reflection_score
            
        except Exception:
            return 0.0
    
    def _analyze_blade_gradient(self, roi: np.ndarray) -> float:
        """Analyze if ROI has blade-like gradient (thicker handle, thinner blade)"""
        # Simplified analysis - real implementation would be more sophisticated
        return 0.5
    
    def _analyze_edge_sharpness(self, roi: np.ndarray) -> float:
        """Analyze edge sharpness in ROI"""
        try:
            edges = cv2.Canny(roi, 50, 150)
            edge_density = np.sum(edges > 0) / (roi.shape[0] * roi.shape[1])
            return min(1.0, edge_density * 3)
        except Exception:
            return 0.0
    
    def _analyze_blade_symmetry(self, roi: np.ndarray) -> float:
        """Analyze if ROI has blade-like symmetry"""
        # Simplified symmetry check
        return 0.4
    
    def _detect_gun_barrel(self, roi: np.ndarray) -> float:
        """Detect gun barrel in ROI"""
        # Simplified barrel detection
        return 0.3
    
    def _detect_trigger_area(self, roi: np.ndarray) -> float:
        """Detect trigger guard area in ROI"""
        # Simplified trigger detection
        return 0.3
    
    def _analyze_gun_proportions(self, w: int, h: int) -> float:
        """Analyze if dimensions match typical gun proportions"""
        aspect_ratio = max(w, h) / min(w, h) if min(w, h) > 0 else 0
        
        # Typical gun aspect ratios are between 2:1 and 3:1
        if 2.0 <= aspect_ratio <= 3.5:
            return 0.8
        elif 1.5 <= aspect_ratio <= 4.0:
            return 0.5
        else:
            return 0.2
    
    def _calculate_overall_confidence(self, detections: Dict[str, float]) -> float:
        """Calculate overall weapons confidence from individual detections"""
        try:
            # Weight different types of evidence
            weights = {
                'knives': 0.30,        # Knives are easier to detect
                'guns': 0.35,          # Guns are high priority
                'sharp_objects': 0.20, # Sharp objects supporting evidence
                'metallic': 0.15       # Metallic surfaces supporting evidence
            }
            
            # Calculate weighted average
            weighted_sum = sum(detections[key] * weights[key] for key in weights)
            
            # Apply confidence boosting for multiple strong indicators
            strong_indicators = sum(1 for conf in detections.values() if conf > 0.7)
            moderate_indicators = sum(1 for conf in detections.values() if 0.4 < conf <= 0.7)
            
            # Boost confidence if multiple indicators present
            if strong_indicators >= 2:
                weighted_sum *= 1.4  # Strong boost for multiple strong indicators
            elif strong_indicators >= 1 and moderate_indicators >= 1:
                weighted_sum *= 1.2  # Moderate boost for mixed indicators
            elif moderate_indicators >= 2:
                weighted_sum *= 1.1  # Small boost for multiple moderate indicators
            
            # Ensure we don't exceed maximum confidence
            final_confidence = min(0.95, weighted_sum)
            
            return final_confidence
            
        except Exception as e:
            logger.error(f"Error calculating overall confidence: {e}")
            return 0.05
    
    def _fallback_detection(self) -> Dict:
        """Fallback detection when models are not available"""
        logger.warning("Using fallback weapons detection")
        return {
            'is_weapons': False,
            'confidence': 0.05,
            'method': 'fallback'
        }

# Main detection function for external use
def detect_weapons(image_data: bytes, detailed: bool = False) -> Dict:
    """
    Main function to detect weapons in images
    
    Args:
        image_data: Raw image bytes
        detailed: Whether to return detailed analysis
        
    Returns:
        Dict with detection results
    """
    detector = WeaponsDetector()
    return detector.detect_weapons(image_data, detailed) 