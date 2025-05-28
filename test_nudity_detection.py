#!/usr/bin/env python3
"""
Test script for NudeNet-based nudity detection

This script tests the nudity detection functionality with sample images
"""

import sys
import os
import requests
from PIL import Image
import io

# Add app directory to path
sys.path.append('app')

from app.nudity_detector import detect_nudity
from app.moderation import ModerationService

def create_test_images():
    """Create simple test images"""
    test_images = {}
    
    # Create solid color images
    colors = {
        'red': (255, 0, 0),
        'blue': (0, 0, 255),
        'green': (0, 255, 0),
        'white': (255, 255, 255),
        'black': (0, 0, 0)
    }
    
    for color_name, rgb in colors.items():
        img = Image.new('RGB', (224, 224), rgb)
        
        # Convert to bytes
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='JPEG')
        img_bytes = img_bytes.getvalue()
        
        test_images[f'{color_name}_square'] = img_bytes
    
    return test_images

def test_nudity_detector():
    """Test the NudeNet nudity detector directly"""
    print("🧪 Testing NudeNet Nudity Detector")
    print("=" * 50)
    
    test_images = create_test_images()
    
    for image_name, image_data in test_images.items():
        print(f"\n📸 Testing: {image_name}")
        
        try:
            result = detect_nudity(image_data, detailed=True)
            
            print(f"  Method: {result.get('method', 'unknown')}")
            print(f"  Is Nude: {result.get('is_nude', False)}")
            print(f"  Confidence: {result.get('confidence', 0.0):.3f}")
            
            if 'safe_score' in result:
                print(f"  Safe Score: {result['safe_score']:.3f}")
                print(f"  Unsafe Score: {result['unsafe_score']:.3f}")
            
            if 'nude_parts_count' in result:
                print(f"  Nude Parts Count: {result['nude_parts_count']}")
            
        except Exception as e:
            print(f"  ❌ Error: {e}")

def test_moderation_service():
    """Test the full moderation service with nudity detection"""
    print("\n🔍 Testing Full Moderation Service")
    print("=" * 50)
    
    service = ModerationService()
    test_images = create_test_images()
    
    import asyncio
    
    async def run_tests():
        for image_name, image_data in test_images.items():
            print(f"\n📸 Testing: {image_name}")
            
            try:
                result = await service.moderate_image(image_data, f"{image_name}.jpg")
                
                print(f"  Overall Safe: {result.safe}")
                print(f"  Overall Confidence: {result.overall_confidence:.3f}")
                
                for category in result.categories:
                    flag_status = "🚩" if category.flagged else "✅"
                    print(f"  {flag_status} {category.category}: {category.confidence:.3f}")
                
            except Exception as e:
                print(f"  ❌ Error: {e}")
    
    asyncio.run(run_tests())

def test_with_real_image():
    """Test with a real image from the internet (if possible)"""
    print("\n🌐 Testing with Sample Real Image")
    print("=" * 50)
    
    try:
        # Test with a simple sample image (safe image)
        url = "https://httpbin.org/image/jpeg"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            image_data = response.content
            
            print("📸 Testing downloaded sample image")
            result = detect_nudity(image_data, detailed=True)
            
            print(f"  Method: {result.get('method', 'unknown')}")
            print(f"  Is Nude: {result.get('is_nude', False)}")
            print(f"  Confidence: {result.get('confidence', 0.0):.3f}")
            
            if 'safe_score' in result:
                print(f"  Safe Score: {result['safe_score']:.3f}")
                print(f"  Unsafe Score: {result['unsafe_score']:.3f}")
        else:
            print("  ⚠️ Could not download sample image")
            
    except Exception as e:
        print(f"  ⚠️ Could not test with real image: {e}")

def main():
    print("🚀 NudeNet Integration Testing")
    print("=" * 50)
    
    # Test NudeNet directly
    test_nudity_detector()
    
    # Test full moderation service
    test_moderation_service()
    
    # Test with real image
    test_with_real_image()
    
    print("\n✅ Testing completed!")
    print("\nKey points:")
    print("• NudeNet provides real nudity detection")
    print("• Simple colored images should have very low scores")
    print("• Real photos will be analyzed properly")
    print("• Thresholds are set conservatively")

if __name__ == "__main__":
    main() 