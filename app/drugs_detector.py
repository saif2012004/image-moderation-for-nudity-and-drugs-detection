#!/usr/bin/env python3
"""
AI-powered drugs detection module

This module provides real drugs detection using computer vision and machine learning
"""

import io
import logging
from typing import Dict, List, Tuple
from PIL import Image
import numpy as np
import cv2

logger = logging.getLogger(__name__)

class DrugsDetector:
    """AI-powered drugs detection using computer vision"""
    
    def __init__(self):
        self.models_available = True
        logger.info("🔥 Initializing AI-powered drugs detector...")
        self._init_models()
    
    def _init_models(self):
        """Initialize computer vision models for drug detection"""
        try:
            # Test OpenCV availability
            import cv2
            logger.info("✅ OpenCV available for drugs detection")
            
            # Initialize detection parameters - FIXED: More sensitive parameters
            self.pill_detector_params = {
                'min_radius': 5,        # Reduced from 8 to detect smaller pills
                'max_radius': 80,       # Increased from 50 to detect larger pills
                'param1': 50,           # Reduced from 100 for more sensitivity
                'param2': 20,           # Reduced from 30 for more sensitivity
                'min_dist': 15          # Reduced from 20 for closer pills
            }
            
            self.powder_detector_params = {
                'texture_threshold': 0.2,      # Reduced from 0.3 for more sensitivity
                'color_variance_threshold': 20, # Reduced from 25
                'white_threshold': 0.6          # Reduced from 0.7
            }
            
            self.plant_detector_params = {
                'green_threshold': 0.25,        # Reduced from 0.3
                'leaf_pattern_threshold': 0.3,  # Reduced from 0.4
                'texture_complexity': 0.4       # Reduced from 0.5
            }
            
            logger.info("✅ Drugs detection models initialized with enhanced sensitivity")
            
        except ImportError as e:
            logger.error(f"❌ OpenCV not available: {e}")
            self.models_available = False
        except Exception as e:
            logger.error(f"❌ Error initializing drugs detection: {e}")
            self.models_available = False
    
    def analyze_image(self, image_data: bytes, detailed: bool = True) -> Dict:
        """
        Analyze image for drugs content
        
        Args:
            image_data: Raw image bytes
            detailed: Whether to use detailed analysis
            
        Returns:
            Dict with analysis results
        """
        if not self.models_available:
            return self._fallback_analysis()
        
        try:
            # Load image
            image = Image.open(io.BytesIO(image_data))
            image_array = np.array(image)
            
            # Convert to BGR for OpenCV
            if len(image_array.shape) == 3:
                image_bgr = cv2.cvtColor(image_array, cv2.COLOR_RGB2BGR)
            else:
                image_bgr = cv2.cvtColor(image_array, cv2.COLOR_GRAY2BGR)
            
            # Perform multi-method detection
            results = self._comprehensive_analysis(image_bgr, image_array)
            
            return results
            
        except Exception as e:
            logger.error(f"Error in drugs analysis: {e}")
            return self._fallback_analysis()
    
    def _comprehensive_analysis(self, image_bgr: np.ndarray, image_rgb: np.ndarray) -> Dict:
        """Comprehensive drugs analysis using multiple detection methods"""
        try:
            # FIRST: Check if this looks like a nudity/body image
            is_likely_nudity = self._detect_nudity_context(image_bgr)
            
            # Individual detection methods
            pill_confidence = self._detect_pills_advanced(image_bgr)
            powder_confidence = self._detect_powder_advanced(image_bgr)
            plant_confidence = self._detect_plants_advanced(image_bgr)
            paraphernalia_confidence = self._detect_paraphernalia_advanced(image_bgr)
            
            # FIXED: Apply nudity context penalty to reduce false positives
            if is_likely_nudity:
                # Significantly reduce drug detection confidence for nudity images
                nudity_penalty = 0.3  # Reduce to 30% of original confidence
                pill_confidence *= nudity_penalty
                powder_confidence *= nudity_penalty
                plant_confidence *= nudity_penalty
                paraphernalia_confidence *= nudity_penalty
                
                logger.info(f"Applied nudity context penalty: {nudity_penalty}")
            
            # Combine results with weighted scoring
            detections = {
                'pills': pill_confidence,
                'powder': powder_confidence,
                'plants': plant_confidence,
                'paraphernalia': paraphernalia_confidence
            }
            
            # Calculate overall confidence
            overall_confidence = self._calculate_overall_confidence(detections)
            
            # Determine if drugs detected - FIXED: Lowered threshold for more sensitivity
            is_drugs = overall_confidence > 0.5  # 50% threshold for drugs (was 60%)
            
            logger.info(f"Drugs analysis: pills={pill_confidence:.3f}, powder={powder_confidence:.3f}, "
                       f"plants={plant_confidence:.3f}, paraphernalia={paraphernalia_confidence:.3f}, "
                       f"overall={overall_confidence:.3f}, flagged={is_drugs}, nudity_context={is_likely_nudity}")
            
            return {
                'method': 'ai_detection',
                'is_drugs': is_drugs,
                'confidence': float(overall_confidence),
                'detections': detections,
                'details': {
                    'pills_detected': pill_confidence > 0.5,
                    'powder_detected': powder_confidence > 0.5,
                    'plants_detected': plant_confidence > 0.5,
                    'paraphernalia_detected': paraphernalia_confidence > 0.5,
                    'primary_indicator': max(detections, key=detections.get),
                    'nudity_context_detected': is_likely_nudity
                }
            }
            
        except Exception as e:
            logger.error(f"Error in comprehensive analysis: {e}")
            return self._fallback_analysis()
    
    def _detect_nudity_context(self, image_bgr: np.ndarray) -> bool:
        """Detect if image contains nudity/body context to avoid false drug positives"""
        try:
            # Convert to different color spaces for analysis
            hsv = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2HSV)
            
            # Method 1: Detect skin tones
            skin_ratio = self._detect_skin_tones(hsv)
            
            # Method 2: Detect smooth body-like gradients
            smoothness_ratio = self._detect_body_smoothness(image_bgr)
            
            # Method 3: Detect large organic shapes (body parts)
            organic_shapes = self._detect_organic_shapes(image_bgr)
            
            logger.debug(f"Nudity context: skin={skin_ratio:.3f}, smoothness={smoothness_ratio:.3f}, "
                        f"organic={organic_shapes:.3f}")
            
            # Determine if this looks like nudity/body content
            is_nudity = (
                skin_ratio > 0.3 or  # High skin tone coverage
                (skin_ratio > 0.15 and smoothness_ratio > 0.5) or  # Some skin + smoothness
                (skin_ratio > 0.2 and organic_shapes > 0.3)  # Some skin + organic shapes
            )
            
            return is_nudity
            
        except Exception as e:
            logger.debug(f"Nudity context detection error: {e}")
            return False
    
    def _detect_skin_tones(self, hsv: np.ndarray) -> float:
        """Detect percentage of image that appears to be skin tone"""
        try:
            # Define multiple skin tone ranges in HSV
            skin_ranges = [
                # Light skin tones
                ([0, 10, 60], [20, 150, 255]),
                ([0, 10, 50], [25, 120, 230]),
                # Medium skin tones
                ([0, 20, 80], [25, 180, 255]),
                # Darker skin tones
                ([0, 30, 40], [30, 200, 200]),
                # Additional ranges for different lighting
                ([5, 25, 70], [15, 140, 240]),
            ]
            
            total_pixels = hsv.shape[0] * hsv.shape[1]
            max_skin_pixels = 0
            
            for lower, upper in skin_ranges:
                mask = cv2.inRange(hsv, np.array(lower), np.array(upper))
                skin_pixels = cv2.countNonZero(mask)
                max_skin_pixels = max(max_skin_pixels, skin_pixels)
            
            skin_ratio = max_skin_pixels / total_pixels
            return skin_ratio
            
        except Exception:
            return 0.0
    
    def _detect_body_smoothness(self, image_bgr: np.ndarray) -> float:
        """Detect smooth gradients typical of body contours"""
        try:
            gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)
            
            # Apply strong blur to detect smooth regions
            blur = cv2.GaussianBlur(gray, (21, 21), 0)
            
            # Calculate difference - smooth regions have low difference
            diff = cv2.absdiff(gray, blur)
            smooth_pixels = cv2.countNonZero(diff < 15)  # Very smooth regions
            total_pixels = gray.shape[0] * gray.shape[1]
            
            smoothness_ratio = smooth_pixels / total_pixels
            return smoothness_ratio
            
        except Exception:
            return 0.0
    
    def _detect_organic_shapes(self, image_bgr: np.ndarray) -> float:
        """Detect large organic shapes typical of body parts"""
        try:
            gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)
            
            # Edge detection
            edges = cv2.Canny(gray, 30, 80)  # Gentler edge detection
            
            # Find contours
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            organic_score = 0.0
            total_area = gray.shape[0] * gray.shape[1]
            
            for contour in contours:
                area = cv2.contourArea(contour)
                
                # Look for large, smooth contours (body parts)
                if area > total_area * 0.05:  # At least 5% of image
                    # Check if contour is organic (not too angular)
                    hull = cv2.convexHull(contour)
                    hull_area = cv2.contourArea(hull)
                    
                    if hull_area > 0:
                        solidity = area / hull_area
                        # Organic shapes have moderate solidity (0.6-0.9)
                        if 0.6 < solidity < 0.9:
                            organic_score += area / total_area
            
            return min(1.0, organic_score)
            
        except Exception:
            return 0.0
    
    def _detect_pills_advanced(self, image_bgr: np.ndarray) -> float:
        """Advanced pill detection using multiple techniques"""
        try:
            gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)
            
            # Method 1: Circle detection (Hough Circles)
            circles_confidence = self._detect_circular_objects(gray)
            
            # Method 2: Blob detection
            blobs_confidence = self._detect_pill_blobs(gray)
            
            # Method 3: Color-based detection (white/colored pills)
            color_confidence = self._detect_pill_colors(image_bgr)
            
            # Method 4: Size and shape analysis
            shape_confidence = self._detect_pill_shapes(gray)
            
            # Combine methods with weights
            pill_confidence = (
                circles_confidence * 0.4 +
                blobs_confidence * 0.3 +
                color_confidence * 0.2 +
                shape_confidence * 0.1
            )
            
            logger.info(f"Pill detection: circles={circles_confidence:.3f}, blobs={blobs_confidence:.3f}, "
                       f"colors={color_confidence:.3f}, shapes={shape_confidence:.3f}")
            
            return min(1.0, pill_confidence)
            
        except Exception as e:
            logger.error(f"Error in pill detection: {e}")
            return 0.0
    
    def _detect_circular_objects(self, gray: np.ndarray) -> float:
        """Detect circular objects that might be pills"""
        try:
            # Apply Gaussian blur
            blurred = cv2.GaussianBlur(gray, (9, 9), 2)
            
            # Detect circles
            circles = cv2.HoughCircles(
                blurred,
                cv2.HOUGH_GRADIENT,
                dp=1,
                minDist=self.pill_detector_params['min_dist'],
                param1=self.pill_detector_params['param1'],
                param2=self.pill_detector_params['param2'],
                minRadius=self.pill_detector_params['min_radius'],
                maxRadius=self.pill_detector_params['max_radius']
            )
            
            if circles is not None:
                circles = np.round(circles[0, :]).astype("int")
                num_circles = len(circles)
                
                logger.info(f"🔵 Detected {num_circles} circular objects")
                
                # Validate circles (check if they look like pills)
                valid_circles = 0
                for (x, y, r) in circles:
                    if self._validate_pill_circle(gray, x, y, r):
                        valid_circles += 1
                
                logger.info(f"💊 {valid_circles} circles validated as pill-like")
                
                # FIXED: MUCH more aggressive confidence calculation - prioritize detection
                if valid_circles >= 30:
                    return min(0.98, 0.8 + (valid_circles * 0.005))  # Very high for many pills
                elif valid_circles >= 20:
                    return min(0.95, 0.7 + (valid_circles * 0.01))   # High confidence
                elif valid_circles >= 10:
                    return min(0.90, 0.6 + (valid_circles * 0.02))   # Good confidence
                elif valid_circles >= 5:
                    return min(0.85, 0.5 + (valid_circles * 0.05))   # Moderate-high confidence
                elif valid_circles >= 3:
                    return min(0.75, 0.4 + (valid_circles * 0.08))   # Decent confidence
                elif valid_circles >= 1:
                    return min(0.65, 0.3 + (valid_circles * 0.15))   # Some confidence
                else:
                    return 0.2  # Even invalid circles suggest some pattern
            
            return 0.0
            
        except Exception as e:
            logger.error(f"Error in circular detection: {e}")
            return 0.0
    
    def _validate_pill_circle(self, gray: np.ndarray, x: int, y: int, r: int) -> bool:
        """Validate if a detected circle looks like a pill"""
        try:
            # Check bounds
            if x - r < 0 or y - r < 0 or x + r >= gray.shape[1] or y + r >= gray.shape[0]:
                return False
            
            # Size validation first - pills should be reasonable size - FIXED: Much more lenient
            if not (5 <= r <= 50):  # Broader size range (was 8-35)
                return False
            
            # ADDED: Check if this circle appears to be skin-colored (body part)
            if self._is_skin_colored_circle(gray, x, y, r):
                logger.debug(f"❌ Circle rejected: appears to be skin-colored body part")
                return False
            
            # Extract region around circle
            mask = np.zeros(gray.shape, dtype=np.uint8)
            cv2.circle(mask, (x, y), r, 255, -1)
            
            # Check intensity uniformity (pills are usually uniform)
            region = cv2.bitwise_and(gray, mask)
            non_zero = region[region > 0]
            
            if len(non_zero) > 0:
                std_dev = np.std(non_zero)
                mean_intensity = np.mean(non_zero)
                
                # FIXED: Much more lenient validation - prioritize detection over false negatives
                
                # Only reject if circle is CLEARLY part of a weapon structure
                if self._is_clearly_weapon_structure(gray, x, y, r):
                    logger.debug(f"❌ Circle rejected: clearly weapon structure")
                    return False
                
                # Very lenient intensity requirements - accept almost any intensity
                if mean_intensity < 20:  # Only reject very dark (was 50)
                    logger.debug(f"❌ Circle rejected: too dark (intensity={mean_intensity:.1f})")
                    return False
                
                # Much more lenient uniformity requirements - pills can vary
                if mean_intensity > 230:  # Very bright (white)
                    uniformity_ok = std_dev < 60  # Much more lenient (was 25)
                elif mean_intensity > 180:  # Bright objects
                    uniformity_ok = std_dev < 50  # Much more lenient (was 20)
                else:  # Medium intensity
                    uniformity_ok = std_dev < 40  # Much more lenient (was 15)
                
                # RELAXED: Edge smoothness check - much more tolerant
                edge_smoothness = self._check_circle_edge_smoothness(gray, x, y, r)
                if edge_smoothness < 0.3:  # Much more lenient (was 0.6)
                    logger.debug(f"❌ Circle rejected: very rough edges (smoothness={edge_smoothness:.2f})")
                    return False
                
                is_valid = uniformity_ok
                
                if is_valid:
                    logger.debug(f"✅ Circle VALID: intensity={mean_intensity:.1f}, std_dev={std_dev:.1f}, radius={r}, smoothness={edge_smoothness:.2f}")
                else:
                    logger.debug(f"❌ Circle rejected: intensity={mean_intensity:.1f}, std_dev={std_dev:.1f}, radius={r}")
                
                return is_valid
            
            return False
            
        except Exception as e:
            logger.debug(f"Circle validation error: {e}")
            return False
    
    def _is_skin_colored_circle(self, gray: np.ndarray, x: int, y: int, r: int) -> bool:
        """Check if a circle appears to be skin-colored (potential body part)"""
        try:
            # Extract circle region
            mask = np.zeros(gray.shape, dtype=np.uint8)
            cv2.circle(mask, (x, y), r, 255, -1)
            
            # Get the region and check if it's in skin tone range
            region = gray[mask > 0]
            if len(region) == 0:
                return False
            
            mean_intensity = np.mean(region)
            std_dev = np.std(region)
            
            # Skin tones in grayscale typically fall in these ranges
            # and have relatively low variation (smooth)
            is_skin_intensity = 120 < mean_intensity < 200  # Typical skin range
            is_smooth = std_dev < 25  # Skin is relatively smooth
            is_large = r > 25  # Large circles more likely to be body parts
            
            # Additional check: see if circle is part of a larger skin-colored region
            expanded_mask = np.zeros(gray.shape, dtype=np.uint8)
            cv2.circle(expanded_mask, (x, y), r * 2, 255, -1)
            expanded_region = gray[expanded_mask > 0]
            
            if len(expanded_region) > 0:
                expanded_mean = np.mean(expanded_region)
                # If the expanded area has similar intensity, likely body part
                intensity_similarity = abs(mean_intensity - expanded_mean) < 15
            else:
                intensity_similarity = False
            
            # Consider it skin if multiple indicators suggest body part
            skin_indicators = sum([is_skin_intensity, is_smooth, is_large, intensity_similarity])
            
            is_likely_skin = skin_indicators >= 3  # Need 3+ indicators
            
            if is_likely_skin:
                logger.debug(f"Skin detection: intensity={mean_intensity:.1f}, std={std_dev:.1f}, "
                            f"large={is_large}, similar={intensity_similarity}")
            
            return is_likely_skin
            
        except Exception:
            return False
    
    def _is_clearly_weapon_structure(self, gray: np.ndarray, x: int, y: int, r: int) -> bool:
        """Check if circle is CLEARLY part of a weapon structure - much more restrictive"""
        try:
            # Only check for very obvious weapon patterns
            expand_r = r * 2  # Smaller check area (was r * 3)
            
            # Ensure bounds
            x1 = max(0, x - expand_r)
            y1 = max(0, y - expand_r)
            x2 = min(gray.shape[1], x + expand_r)
            y2 = min(gray.shape[0], y + expand_r)
            
            # Extract expanded region
            region = gray[y1:y2, x1:x2]
            
            # Threshold to find structures
            _, thresh = cv2.threshold(region, 127, 255, cv2.THRESH_BINARY)
            
            # Find contours in expanded area
            contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            # Only reject if there are VERY LARGE rectangular structures (clear weapons)
            for contour in contours:
                area = cv2.contourArea(contour)
                if area > (r * r * 50):  # Much larger threshold (was 20)
                    # Check if it's very rectangular (clear weapon-like)
                    rect = cv2.boundingRect(contour)
                    rect_area = rect[2] * rect[3]
                    if area / rect_area > 0.9:  # Very rectangular (was 0.7)
                        # Additional check: must be much larger than the circle
                        if rect_area > (r * r * 30):  # Much larger requirement
                            return True
            
            return False
            
        except Exception:
            return False
    
    def _check_circle_edge_smoothness(self, gray: np.ndarray, x: int, y: int, r: int) -> float:
        """Check if circle edges are smooth (pills have smooth edges)"""
        try:
            # Create circle mask
            mask = np.zeros(gray.shape, dtype=np.uint8)
            cv2.circle(mask, (x, y), r, 255, 2)  # Only edge pixels
            
            # Get edge pixels
            edge_pixels = np.where(mask > 0)
            if len(edge_pixels[0]) == 0:
                return 0.0
            
            # Calculate gradient along edge
            edge_coords = list(zip(edge_pixels[1], edge_pixels[0]))  # (x, y) format
            
            if len(edge_coords) < 8:  # Too few edge pixels
                return 0.0
            
            # Sample edge points and check gradient consistency
            gradient_consistency = 0
            sample_count = min(len(edge_coords), 16)
            
            for i in range(0, len(edge_coords), len(edge_coords) // sample_count):
                ex, ey = edge_coords[i]
                if 1 <= ex < gray.shape[1] - 1 and 1 <= ey < gray.shape[0] - 1:
                    # Calculate local gradient
                    gx = int(gray[ey, ex + 1]) - int(gray[ey, ex - 1])
                    gy = int(gray[ey + 1, ex]) - int(gray[ey - 1, ex])
                    gradient_mag = np.sqrt(gx*gx + gy*gy)
                    
                    # Smooth edges have moderate, consistent gradients
                    if 10 < gradient_mag < 100:
                        gradient_consistency += 1
            
            smoothness = gradient_consistency / sample_count if sample_count > 0 else 0
            return smoothness
            
        except Exception:
            return 0.0
    
    def _detect_pill_blobs(self, gray: np.ndarray) -> float:
        """Detect pill-like blobs using blob detection"""
        try:
            # Set up blob detector parameters - FIXED: More sensitive parameters
            params = cv2.SimpleBlobDetector_Params()
            
            # Filter by Area - FIXED: Broader range
            params.filterByArea = True
            params.minArea = 50        # Reduced from 100
            params.maxArea = 8000      # Increased from 5000
            
            # Filter by Circularity - FIXED: More lenient
            params.filterByCircularity = True
            params.minCircularity = 0.4  # Reduced from 0.6 for more tolerance
            
            # Filter by Convexity - FIXED: More lenient
            params.filterByConvexity = True
            params.minConvexity = 0.6    # Reduced from 0.8
            
            # Filter by Inertia - FIXED: Add inertia filtering
            params.filterByInertia = True
            params.minInertiaRatio = 0.3
            
            # Create detector
            detector = cv2.SimpleBlobDetector_create(params)
            
            # Detect blobs
            keypoints = detector.detect(gray)
            
            logger.info(f"🔵 Blob detector found {len(keypoints)} potential pill blobs")
            
            if len(keypoints) > 0:
                # Analyze detected blobs - FIXED: More generous scoring
                valid_blobs = 0
                for kp in keypoints:
                    # Check blob characteristics - FIXED: Broader size range
                    if 5 < kp.size < 120:  # Broader size range (was 10-100)
                        valid_blobs += 1
                
                logger.info(f"💊 {valid_blobs} blobs validated as pill-like")
                
                # FIXED: More generous confidence calculation
                if valid_blobs >= 5:
                    return min(0.9, 0.5 + (valid_blobs * 0.08))
                elif valid_blobs >= 3:
                    return min(0.8, 0.4 + (valid_blobs * 0.1))
                elif valid_blobs >= 2:
                    return min(0.7, 0.3 + (valid_blobs * 0.15))
                elif valid_blobs >= 1:
                    return 0.5  # Increased from 0.4
            
            return 0.0
            
        except Exception as e:
            logger.error(f"Error in blob detection: {e}")
            return 0.0
    
    def _detect_pill_colors(self, image_bgr: np.ndarray) -> float:
        """Detect typical pill colors"""
        try:
            # Convert to HSV for better color analysis
            hsv = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2HSV)
            
            # Define color ranges for common pill colors
            color_ranges = {
                'white': ([0, 0, 200], [180, 30, 255]),
                'blue': ([100, 50, 50], [130, 255, 255]),
                'red': ([0, 50, 50], [10, 255, 255]),
                'yellow': ([20, 50, 50], [30, 255, 255]),
                'green': ([40, 50, 50], [80, 255, 255])
            }
            
            total_pixels = image_bgr.shape[0] * image_bgr.shape[1]
            pill_color_pixels = 0
            
            for color_name, (lower, upper) in color_ranges.items():
                lower = np.array(lower)
                upper = np.array(upper)
                mask = cv2.inRange(hsv, lower, upper)
                pill_color_pixels += cv2.countNonZero(mask)
            
            color_ratio = pill_color_pixels / total_pixels
            
            # High concentration of pill colors suggests pills
            if color_ratio > 0.3:
                return min(0.7, color_ratio * 1.5)
            elif color_ratio > 0.1:
                return color_ratio * 2
            
            return 0.0
            
        except Exception as e:
            logger.error(f"Error in color detection: {e}")
            return 0.0
    
    def _detect_pill_shapes(self, gray: np.ndarray) -> float:
        """Detect pill-like shapes using contour analysis"""
        try:
            # Edge detection
            edges = cv2.Canny(gray, 50, 150)
            
            # Find contours
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            pill_shapes = 0
            for contour in contours:
                area = cv2.contourArea(contour)
                if 100 < area < 2000:  # Reasonable pill size
                    # Check if shape is pill-like (circular or oval)
                    perimeter = cv2.arcLength(contour, True)
                    if perimeter > 0:
                        circularity = 4 * np.pi * area / (perimeter * perimeter)
                        if circularity > 0.6:  # Reasonably circular
                            pill_shapes += 1
            
            if pill_shapes >= 3:
                return min(0.6, 0.2 + (pill_shapes * 0.1))
            elif pill_shapes >= 1:
                return 0.3
            
            return 0.0
            
        except Exception as e:
            logger.error(f"Error in shape detection: {e}")
            return 0.0
    
    def _detect_powder_advanced(self, image_bgr: np.ndarray) -> float:
        """Advanced powder detection using texture and color analysis"""
        try:
            gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)
            
            # Method 1: Texture analysis
            texture_confidence = self._analyze_powder_texture(gray)
            
            # Method 2: Color analysis (white/off-white powders)
            color_confidence = self._analyze_powder_colors(image_bgr)
            
            # Method 3: Pattern analysis
            pattern_confidence = self._analyze_powder_patterns(gray)
            
            # Combine methods
            powder_confidence = (
                texture_confidence * 0.5 +
                color_confidence * 0.3 +
                pattern_confidence * 0.2
            )
            
            logger.info(f"Powder detection: texture={texture_confidence:.3f}, "
                       f"color={color_confidence:.3f}, pattern={pattern_confidence:.3f}")
            
            return min(1.0, powder_confidence)
            
        except Exception as e:
            logger.error(f"Error in powder detection: {e}")
            return 0.0
    
    def _analyze_powder_texture(self, gray: np.ndarray) -> float:
        """Analyze texture patterns typical of powders"""
        try:
            # Method 1: Calculate texture using Local Binary Pattern-like approach
            laplacian = cv2.Laplacian(gray, cv2.CV_64F)
            texture_variance = laplacian.var()
            
            # Method 2: Look for smooth, uniform regions (fine powder characteristic)
            blur = cv2.GaussianBlur(gray, (15, 15), 0)
            smoothness = cv2.absdiff(gray, blur)
            smooth_pixels = cv2.countNonZero(smoothness < 10)
            total_pixels = gray.shape[0] * gray.shape[1]
            smoothness_ratio = smooth_pixels / total_pixels
            
            # Method 3: Check for white/bright regions that are uniform
            bright_mask = gray > 200  # Bright regions
            bright_pixels = cv2.countNonZero(bright_mask)
            bright_ratio = bright_pixels / total_pixels
            
            # FIXED: Much more aggressive texture confidence for powder
            texture_score = 0.0
            
            # Fine powder has moderate texture variance
            if 20 < texture_variance < 300:  # Broader range (was 50-500)
                texture_score += min(0.7, texture_variance / 300)
            elif texture_variance < 20:  # Very smooth (fine powder)
                texture_score += 0.8  # High score for smooth powder
            
            # Smooth, uniform regions suggest powder
            if smoothness_ratio > 0.6:
                texture_score += 0.6
            elif smoothness_ratio > 0.4:
                texture_score += 0.4
            elif smoothness_ratio > 0.2:
                texture_score += 0.2
            
            # Bright uniform regions suggest white powder
            if bright_ratio > 0.3:
                texture_score += min(0.8, bright_ratio * 2.0)
            elif bright_ratio > 0.1:
                texture_score += min(0.5, bright_ratio * 3.0)
            
            # Combine and boost
            final_score = min(0.9, texture_score)
            
            logger.debug(f"Powder texture: variance={texture_variance:.1f}, "
                        f"smoothness={smoothness_ratio:.3f}, bright={bright_ratio:.3f}, "
                        f"score={final_score:.3f}")
            
            return final_score
            
        except Exception as e:
            logger.debug(f"Powder texture analysis error: {e}")
            return 0.0
    
    def _analyze_powder_colors(self, image_bgr: np.ndarray) -> float:
        """Analyze colors typical of drug powders"""
        try:
            # Convert to HSV
            hsv = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2HSV)
            
            # FIXED: Much more aggressive white/off-white powder detection
            # Broader white range for powder detection
            lower_white = np.array([0, 0, 150])     # Lower brightness threshold (was 180)
            upper_white = np.array([180, 80, 255])  # Higher saturation tolerance (was 50)
            white_mask = cv2.inRange(hsv, lower_white, upper_white)
            
            # Brown/tan powder detection (heroin-like)
            lower_brown = np.array([10, 30, 40])    # More lenient (was 50, 50, 50)
            upper_brown = np.array([30, 255, 200])
            brown_mask = cv2.inRange(hsv, lower_brown, upper_brown)
            
            # Additional off-white/cream detection
            lower_cream = np.array([15, 20, 120])
            upper_cream = np.array([35, 100, 240])
            cream_mask = cv2.inRange(hsv, lower_cream, upper_cream)
            
            total_pixels = image_bgr.shape[0] * image_bgr.shape[1]
            white_ratio = cv2.countNonZero(white_mask) / total_pixels
            brown_ratio = cv2.countNonZero(brown_mask) / total_pixels
            cream_ratio = cv2.countNonZero(cream_mask) / total_pixels
            
            # Take the maximum ratio from any powder color
            powder_ratio = max(white_ratio, brown_ratio, cream_ratio)
            
            # FIXED: Much more aggressive confidence calculation for powder
            if powder_ratio > 0.6:
                return min(0.95, powder_ratio * 1.3)  # Very high confidence
            elif powder_ratio > 0.4:
                return min(0.85, powder_ratio * 1.8)  # High confidence
            elif powder_ratio > 0.2:
                return min(0.75, powder_ratio * 2.5)  # Good confidence
            elif powder_ratio > 0.1:
                return min(0.6, powder_ratio * 4.0)   # Decent confidence
            elif powder_ratio > 0.05:
                return min(0.4, powder_ratio * 6.0)   # Some confidence
            
            return 0.0
            
        except Exception:
            return 0.0
    
    def _analyze_powder_patterns(self, gray: np.ndarray) -> float:
        """Analyze patterns typical of powder substances"""
        try:
            # Look for granular patterns using morphological operations
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
            
            # Opening operation to detect small granules
            opened = cv2.morphologyEx(gray, cv2.MORPH_OPEN, kernel)
            
            # Calculate difference to detect granular texture
            diff = cv2.absdiff(gray, opened)
            granular_pixels = cv2.countNonZero(diff > 5)  # More sensitive (was 10)
            total_pixels = gray.shape[0] * gray.shape[1]
            
            granular_ratio = granular_pixels / total_pixels
            
            # FIXED: More aggressive pattern confidence
            if granular_ratio > 0.5:
                return min(0.8, granular_ratio * 1.4)
            elif granular_ratio > 0.3:
                return min(0.7, granular_ratio * 2.0)
            elif granular_ratio > 0.1:
                return min(0.5, granular_ratio * 3.0)
            
            return 0.0
            
        except Exception:
            return 0.0
    
    def _detect_plants_advanced(self, image_bgr: np.ndarray) -> float:
        """Advanced plant detection (cannabis, etc.)"""
        try:
            # Method 1: Green color analysis
            green_confidence = self._analyze_plant_colors(image_bgr)
            
            # Method 2: Leaf pattern detection
            leaf_confidence = self._detect_leaf_patterns(image_bgr)
            
            # Method 3: Texture analysis
            texture_confidence = self._analyze_plant_texture(image_bgr)
            
            # Combine methods
            plant_confidence = (
                green_confidence * 0.4 +
                leaf_confidence * 0.4 +
                texture_confidence * 0.2
            )
            
            logger.info(f"Plant detection: green={green_confidence:.3f}, "
                       f"leaf={leaf_confidence:.3f}, texture={texture_confidence:.3f}")
            
            return min(1.0, plant_confidence)
            
        except Exception as e:
            logger.error(f"Error in plant detection: {e}")
            return 0.0
    
    def _analyze_plant_colors(self, image_bgr: np.ndarray) -> float:
        """Analyze green colors typical of cannabis plants"""
        try:
            hsv = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2HSV)
            
            # Multiple green ranges for different plant conditions
            green_ranges = [
                ([35, 40, 40], [85, 255, 255]),    # General green
                ([40, 50, 50], [80, 255, 200]),    # Healthy green
                ([25, 30, 30], [95, 255, 180])     # Dried/brown-green
            ]
            
            total_pixels = image_bgr.shape[0] * image_bgr.shape[1]
            max_green_ratio = 0
            
            for lower, upper in green_ranges:
                mask = cv2.inRange(hsv, np.array(lower), np.array(upper))
                green_ratio = cv2.countNonZero(mask) / total_pixels
                max_green_ratio = max(max_green_ratio, green_ratio)
            
            if max_green_ratio > 0.5:
                return min(0.8, max_green_ratio * 1.2)
            elif max_green_ratio > 0.3:
                return max_green_ratio
            
            return 0.0
            
        except Exception:
            return 0.0
    
    def _detect_leaf_patterns(self, image_bgr: np.ndarray) -> float:
        """Detect leaf-like patterns characteristic of cannabis"""
        try:
            gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)
            
            # Edge detection to find leaf structures
            edges = cv2.Canny(gray, 30, 100)
            
            # Find contours
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            leaf_like_shapes = 0
            for contour in contours:
                area = cv2.contourArea(contour)
                if area > 500:  # Reasonable leaf size
                    # Check if shape is leaf-like
                    hull = cv2.convexHull(contour)
                    hull_area = cv2.contourArea(hull)
                    
                    if hull_area > 0:
                        solidity = area / hull_area
                        if 0.6 < solidity < 0.9:  # Leaf-like solidity
                            leaf_like_shapes += 1
            
            if leaf_like_shapes >= 3:
                return min(0.7, 0.3 + (leaf_like_shapes * 0.1))
            elif leaf_like_shapes >= 1:
                return 0.4
            
            return 0.0
            
        except Exception:
            return 0.0
    
    def _analyze_plant_texture(self, image_bgr: np.ndarray) -> float:
        """Analyze texture patterns of plant material"""
        try:
            gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)
            
            # Calculate texture complexity
            laplacian = cv2.Laplacian(gray, cv2.CV_64F)
            texture_var = laplacian.var()
            
            # Plants have complex, organic textures
            if 200 < texture_var < 2000:
                return min(0.6, texture_var / 2000)
            
            return 0.0
            
        except Exception:
            return 0.0
    
    def _detect_paraphernalia_advanced(self, image_bgr: np.ndarray) -> float:
        """Detect drug paraphernalia using object detection"""
        try:
            # Method 1: Pipe/tube detection
            pipe_confidence = self._detect_pipes(image_bgr)
            
            # Method 2: Scale detection
            scale_confidence = self._detect_scales(image_bgr)
            
            # Method 3: Syringe detection
            syringe_confidence = self._detect_syringes(image_bgr)
            
            # Method 4: Bag/container detection
            container_confidence = self._detect_drug_containers(image_bgr)
            
            # Take maximum confidence from any method
            paraphernalia_confidence = max(
                pipe_confidence,
                scale_confidence,
                syringe_confidence,
                container_confidence
            )
            
            logger.info(f"Paraphernalia detection: pipes={pipe_confidence:.3f}, "
                       f"scales={scale_confidence:.3f}, syringes={syringe_confidence:.3f}, "
                       f"containers={container_confidence:.3f}")
            
            return min(1.0, paraphernalia_confidence)
            
        except Exception as e:
            logger.error(f"Error in paraphernalia detection: {e}")
            return 0.0
    
    def _detect_pipes(self, image_bgr: np.ndarray) -> float:
        """Detect pipe-like objects"""
        try:
            gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)
            edges = cv2.Canny(gray, 50, 150)
            
            # Use HoughLinesP to detect straight lines (pipes)
            lines = cv2.HoughLinesP(edges, 1, np.pi/180, threshold=50, 
                                   minLineLength=30, maxLineGap=10)
            
            if lines is not None:
                # Look for cylindrical objects
                long_lines = 0
                for line in lines:
                    x1, y1, x2, y2 = line[0]
                    length = np.sqrt((x2-x1)**2 + (y2-y1)**2)
                    if length > 50:  # Reasonable pipe length
                        long_lines += 1
                
                if long_lines >= 2:
                    return min(0.6, 0.2 + (long_lines * 0.1))
            
            return 0.0
            
        except Exception:
            return 0.0
    
    def _detect_scales(self, image_bgr: np.ndarray) -> float:
        """Detect digital scales"""
        try:
            gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)
            
            # Look for rectangular objects with digital displays
            edges = cv2.Canny(gray, 50, 150)
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            for contour in contours:
                area = cv2.contourArea(contour)
                if area > 1000:  # Reasonable scale size
                    # Check if rectangular
                    approx = cv2.approxPolyDP(contour, 0.02 * cv2.arcLength(contour, True), True)
                    if len(approx) == 4:  # Rectangular
                        # Check aspect ratio (scales are usually wider than tall)
                        rect = cv2.boundingRect(contour)
                        aspect_ratio = rect[2] / rect[3]
                        if 1.2 < aspect_ratio < 3.0:
                            return 0.7
            
            return 0.0
            
        except Exception:
            return 0.0
    
    def _detect_syringes(self, image_bgr: np.ndarray) -> float:
        """Detect syringe-like objects"""
        try:
            gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)
            edges = cv2.Canny(gray, 50, 150)
            
            # Look for thin, elongated objects
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            for contour in contours:
                area = cv2.contourArea(contour)
                if 200 < area < 2000:  # Reasonable syringe size
                    rect = cv2.boundingRect(contour)
                    aspect_ratio = max(rect[2], rect[3]) / min(rect[2], rect[3])
                    if aspect_ratio > 5:  # Very elongated (syringe-like)
                        return 0.8
            
            return 0.0
            
        except Exception:
            return 0.0
    
    def _detect_drug_containers(self, image_bgr: np.ndarray) -> float:
        """Detect small bags or containers used for drugs"""
        try:
            # This is a placeholder for container detection
            # In a real implementation, this would use more sophisticated
            # object detection models
            return 0.0
            
        except Exception:
            return 0.0
    
    def _calculate_overall_confidence(self, detections: Dict[str, float]) -> float:
        """Calculate overall drugs confidence from individual detections"""
        try:
            # Weight different types of evidence - FIXED: More aggressive weighting
            weights = {
                'pills': 0.50,         # Pills are primary evidence (increased)
                'powder': 0.35,        # Powder is strong evidence
                'plants': 0.10,        # Plants are supporting evidence (reduced)
                'paraphernalia': 0.05  # Paraphernalia is minor evidence (reduced)
            }
            
            # Calculate weighted average
            weighted_sum = sum(detections[key] * weights[key] for key in weights)
            
            # FIXED: MUCH more aggressive confidence boosting for drug detection
            strong_indicators = sum(1 for conf in detections.values() if conf > 0.6)
            moderate_indicators = sum(1 for conf in detections.values() if 0.3 < conf <= 0.6)
            weak_indicators = sum(1 for conf in detections.values() if 0.1 < conf <= 0.3)
            
            # FIXED: Much more aggressive boosting - prioritize detection over false negatives
            if strong_indicators >= 2:
                # Multiple strong indicators - very high confidence boost
                weighted_sum *= 2.0  # Double confidence
            elif strong_indicators >= 1 and moderate_indicators >= 1:
                # One strong + one moderate - high boost
                weighted_sum *= 1.8
            elif strong_indicators >= 1:
                # One strong indicator - good boost
                weighted_sum *= 1.6
            elif moderate_indicators >= 2:
                # Multiple moderate indicators - decent boost
                weighted_sum *= 1.4
            elif moderate_indicators >= 1:
                # One moderate indicator - small boost
                weighted_sum *= 1.2
            elif weak_indicators >= 3:
                # Multiple weak indicators - tiny boost
                weighted_sum *= 1.1
            # No penalty for insufficient evidence - just use base score
                
            # Final confidence with realistic maximum
            final_confidence = min(0.98, weighted_sum)
            
            logger.debug(f"Confidence calculation: weighted_sum={weighted_sum:.3f}, "
                        f"strong={strong_indicators}, moderate={moderate_indicators}, "
                        f"final={final_confidence:.3f}")
            
            return final_confidence
            
        except Exception as e:
            logger.error(f"Error calculating overall confidence: {e}")
            return 0.05
    
    def _fallback_analysis(self) -> Dict:
        """Fallback when AI models are not available"""
        return {
            'method': 'fallback',
            'is_drugs': False,
            'confidence': 0.05,
            'detections': {
                'pills': 0.0,
                'powder': 0.0,
                'plants': 0.0,
                'paraphernalia': 0.0
            },
            'details': {
                'message': 'AI models not available, using fallback'
            }
        }

# Global instance
drugs_detector = DrugsDetector()

def detect_drugs(image_data: bytes, detailed: bool = True) -> Dict:
    """
    Convenience function for drugs detection
    
    Args:
        image_data: Raw image bytes
        detailed: Whether to use detailed analysis
        
    Returns:
        Dict with detection results
    """
    return drugs_detector.analyze_image(image_data, detailed) 