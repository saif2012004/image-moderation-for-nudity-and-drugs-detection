#!/usr/bin/env python3
"""
Test script for AI-powered drugs detection

This script tests the new drugs detection system with various test images
"""

import io
import sys
import logging
from PIL import Image, ImageDraw
import numpy as np

# Add app directory to path
sys.path.append('app')

from app.drugs_detector import detect_drugs

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def create_test_image(color, size=(300, 300)):
    """Create a simple test image with solid color"""
    image = Image.new('RGB', size, color)
    return image

def create_pill_like_image(size=(300, 300)):
    """Create an image that might look like pills"""
    image = Image.new('RGB', size, 'white')
    draw = ImageDraw.Draw(image)
    
    # Draw several circular objects that might look like pills
    for i in range(5):
        x = 50 + i * 50
        y = 150
        radius = 20
        # Draw white circles with slight gray border
        draw.ellipse([x-radius, y-radius, x+radius, y+radius], fill='white', outline='lightgray', width=2)
    
    return image

def create_powder_like_image(size=(300, 300)):
    """Create an image that might look like powder"""
    # Create a white/off-white textured image
    image = Image.new('RGB', size, 'white')
    
    # Add some noise to simulate powder texture
    img_array = np.array(image)
    noise = np.random.normal(0, 10, img_array.shape).astype(np.uint8)
    img_array = np.clip(img_array.astype(int) + noise, 0, 255).astype(np.uint8)
    
    return Image.fromarray(img_array)

def create_plant_like_image(size=(300, 300)):
    """Create an image that might look like plants"""
    image = Image.new('RGB', size, 'darkgreen')
    draw = ImageDraw.Draw(image)
    
    # Draw some leaf-like shapes
    for i in range(3):
        x = 50 + i * 80
        y = 100 + i * 50
        # Draw oval leaf shapes
        draw.ellipse([x, y, x+60, y+30], fill='green', outline='darkgreen')
        draw.ellipse([x+10, y+40, x+50, y+70], fill='forestgreen', outline='darkgreen')
    
    return image

def image_to_bytes(image):
    """Convert PIL Image to bytes"""
    img_byte_arr = io.BytesIO()
    image.save(img_byte_arr, format='PNG')
    return img_byte_arr.getvalue()

def test_drugs_detection():
    """Test the drugs detection system"""
    print("🧪 Testing AI-powered drugs detection system...")
    print("=" * 60)
    
    test_cases = [
        ("Red solid color", create_test_image('red')),
        ("Blue solid color", create_test_image('blue')),
        ("White solid color", create_test_image('white')),
        ("Green solid color", create_test_image('green')),
        ("Pill-like objects", create_pill_like_image()),
        ("Powder-like texture", create_powder_like_image()),
        ("Plant-like image", create_plant_like_image()),
    ]
    
    for test_name, test_image in test_cases:
        print(f"\n🔍 Testing: {test_name}")
        print("-" * 40)
        
        try:
            # Convert image to bytes
            image_data = image_to_bytes(test_image)
            
            # Run drugs detection
            result = detect_drugs(image_data, detailed=True)
            
            # Extract results
            is_drugs = result.get('is_drugs', False)
            confidence = result.get('confidence', 0.0)
            method = result.get('method', 'unknown')
            detections = result.get('detections', {})
            
            # Print results
            print(f"📊 Results:")
            print(f"   Is drugs: {is_drugs}")
            print(f"   Confidence: {confidence:.3f} ({confidence*100:.1f}%)")
            print(f"   Method: {method}")
            
            if detections:
                print(f"   Detections:")
                for detection_type, detection_confidence in detections.items():
                    print(f"     - {detection_type}: {detection_confidence:.3f}")
            
            # Status indicator
            if is_drugs:
                status = "🚨 FLAGGED"
            else:
                status = "✅ SAFE"
            
            print(f"   Status: {status}")
            
        except Exception as e:
            print(f"❌ Error testing {test_name}: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("🏁 Drugs detection testing complete!")

if __name__ == "__main__":
    test_drugs_detection() 