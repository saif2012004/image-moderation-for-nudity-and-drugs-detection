#!/usr/bin/env python3
"""
Debug script for real drugs detection

This script will help us understand why the drugs detection is giving low confidence
for obvious drug images
"""

import io
import sys
import logging
import requests
from PIL import Image, ImageDraw
import numpy as np

# Add app directory to path
sys.path.append('app')

from app.drugs_detector import detect_drugs

# Set up detailed logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def create_obvious_drugs_image(size=(400, 400)):
    """Create an image that obviously contains drug-related content"""
    image = Image.new('RGB', size, 'white')
    draw = ImageDraw.Draw(image)
    
    # Draw many pill-like circles (white pills)
    for i in range(8):
        for j in range(3):
            x = 50 + i * 40
            y = 100 + j * 60
            radius = 15
            # Draw white circles with borders (pills)
            draw.ellipse([x-radius, y-radius, x+radius, y+radius], 
                        fill='white', outline='gray', width=3)
    
    # Add some powder-like texture areas
    for i in range(5):
        x = 30 + i * 60
        y = 300
        # Draw irregular powder piles
        draw.ellipse([x, y, x+40, y+20], fill='lightgray', outline='darkgray')
    
    # Add syringe-like objects
    for i in range(3):
        x = 80 + i * 100
        y = 350
        # Draw thin elongated rectangles (syringes)
        draw.rectangle([x, y, x+60, y+8], fill='silver', outline='black')
        draw.circle([x+60, y+4], 3, fill='red')  # needle tip
    
    return image

def test_obvious_drugs():
    """Test with an obvious drugs image"""
    print("🧪 Testing AI drugs detection with OBVIOUS drugs content...")
    print("=" * 70)
    
    # Create obvious drugs image
    drugs_image = create_obvious_drugs_image()
    
    # Convert to bytes
    img_byte_arr = io.BytesIO()
    drugs_image.save(img_byte_arr, format='PNG')
    image_data = img_byte_arr.getvalue()
    
    print("📊 Testing with image containing:")
    print("   - 24 white pill-like circles")
    print("   - 5 powder-like gray areas")
    print("   - 3 syringe-like objects")
    print("\nThis should be FLAGGED with HIGH confidence!")
    print("-" * 50)
    
    try:
        # Run drugs detection with detailed analysis
        result = detect_drugs(image_data, detailed=True)
        
        # Extract results
        is_drugs = result.get('is_drugs', False)
        confidence = result.get('confidence', 0.0)
        method = result.get('method', 'unknown')
        detections = result.get('detections', {})
        details = result.get('details', {})
        
        print(f"🔍 DRUGS DETECTION RESULTS:")
        print(f"   Method: {method}")
        print(f"   Is drugs: {is_drugs}")
        print(f"   Overall Confidence: {confidence:.3f} ({confidence*100:.1f}%)")
        print(f"   Expected: TRUE with >60% confidence")
        
        if detections:
            print(f"\n📈 Individual Detections:")
            for detection_type, detection_confidence in detections.items():
                status = "✅" if detection_confidence > 0.5 else "⚠️"
                print(f"   {status} {detection_type}: {detection_confidence:.3f} ({detection_confidence*100:.1f}%)")
        
        if details:
            print(f"\n🔬 Detection Details:")
            for key, value in details.items():
                print(f"   - {key}: {value}")
        
        # Analysis
        print(f"\n🎯 ANALYSIS:")
        if is_drugs and confidence > 0.6:
            print("✅ CORRECT: System properly flagged obvious drugs content!")
        elif is_drugs and confidence <= 0.6:
            print("⚠️ PARTIAL: Detected as drugs but confidence too low")
            print(f"   Current: {confidence:.1%}, Should be: >60%")
        else:
            print("❌ INCORRECT: System failed to detect obvious drugs content!")
            print("   This is a serious detection failure")
        
        # Threshold analysis
        print(f"\n🎚️ THRESHOLD ANALYSIS:")
        print(f"   Current confidence: {confidence:.1%}")
        print(f"   Detection threshold: 60%")
        print(f"   Would be flagged: {'YES' if confidence > 0.6 else 'NO'}")
        
        return is_drugs, confidence
        
    except Exception as e:
        print(f"❌ Error in drugs detection: {e}")
        import traceback
        traceback.print_exc()
        return False, 0.0

def test_detection_components():
    """Test individual detection components"""
    print("\n" + "="*70)
    print("🔧 TESTING INDIVIDUAL DETECTION COMPONENTS")
    print("="*70)
    
    # Create test image
    drugs_image = create_obvious_drugs_image()
    img_byte_arr = io.BytesIO()
    drugs_image.save(img_byte_arr, format='PNG')
    image_data = img_byte_arr.getvalue()
    
    try:
        from app.drugs_detector import drugs_detector
        
        # Load image for component testing
        image = Image.open(io.BytesIO(image_data))
        image_array = np.array(image)
        
        # Convert to BGR for OpenCV
        import cv2
        image_bgr = cv2.cvtColor(image_array, cv2.COLOR_RGB2BGR)
        
        print("🧩 Testing individual components:")
        
        # Test pill detection
        pill_confidence = drugs_detector._detect_pills_advanced(image_bgr)
        print(f"   💊 Pills: {pill_confidence:.3f} ({pill_confidence*100:.1f}%)")
        
        # Test powder detection  
        powder_confidence = drugs_detector._detect_powder_advanced(image_bgr)
        print(f"   🥄 Powder: {powder_confidence:.3f} ({powder_confidence*100:.1f}%)")
        
        # Test plant detection
        plant_confidence = drugs_detector._detect_plants_advanced(image_bgr)
        print(f"   🌿 Plants: {plant_confidence:.3f} ({plant_confidence*100:.1f}%)")
        
        # Test paraphernalia detection
        para_confidence = drugs_detector._detect_paraphernalia_advanced(image_bgr)
        print(f"   💉 Paraphernalia: {para_confidence:.3f} ({para_confidence*100:.1f}%)")
        
        # Calculate expected overall
        detections = {
            'pills': pill_confidence,
            'powder': powder_confidence,
            'plants': plant_confidence,
            'paraphernalia': para_confidence
        }
        
        overall = drugs_detector._calculate_overall_confidence(detections)
        print(f"\n🎯 Expected Overall: {overall:.3f} ({overall*100:.1f}%)")
        
        # Analysis
        if pill_confidence > 0.5:
            print("✅ Pills detection working correctly")
        else:
            print("❌ Pills detection failed - should detect 24 pill-like circles!")
            
        if para_confidence > 0.5:
            print("✅ Paraphernalia detection working correctly")
        else:
            print("❌ Paraphernalia detection failed - should detect syringe-like objects!")
            
    except Exception as e:
        print(f"❌ Error testing components: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    is_drugs, confidence = test_obvious_drugs()
    test_detection_components()
    
    print("\n" + "="*70)
    print("🏁 DRUGS DETECTION DEBUG COMPLETE")
    print("="*70)
    
    if not is_drugs or confidence < 0.6:
        print("🚨 CRITICAL ISSUE: Drugs detection is not working correctly!")
        print("   The system should flag obvious drug content with high confidence.")
        print("   This needs immediate investigation and fixing.")
    else:
        print("✅ Drugs detection appears to be working correctly.") 