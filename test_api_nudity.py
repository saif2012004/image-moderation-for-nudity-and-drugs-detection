#!/usr/bin/env python3
"""
Test script to verify NudeNet nudity detection in the containerized API
"""

import requests
from PIL import Image
import io

def create_test_image(color=(255, 0, 0), size=(224, 224)):
    """Create a simple test image"""
    img = Image.new('RGB', size, color)
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='JPEG')
    return img_bytes.getvalue()

def test_nudity_api():
    """Test the nudity detection API"""
    print("🧪 Testing NudeNet Integration in Containerized API")
    print("=" * 60)
    
    # Test with different colored images
    test_cases = [
        ("red_image", (255, 0, 0)),
        ("blue_image", (0, 0, 255)),
        ("green_image", (0, 255, 0)),
        ("white_image", (255, 255, 255)),
        ("black_image", (0, 0, 0))
    ]
    
    api_url = "http://localhost:7000/moderate"
    headers = {
        "Authorization": "Bearer BdD--lvAf5SXLKFa98ji7GO6zhCv9iaNao4XWyAVrnA"
    }
    
    for test_name, color in test_cases:
        print(f"\n📸 Testing: {test_name} {color}")
        
        try:
            # Create test image
            image_data = create_test_image(color)
            
            # Prepare multipart form data
            files = {
                'file': (f'{test_name}.jpg', image_data, 'image/jpeg')
            }
            
            # Make API request
            response = requests.post(api_url, files=files, headers=headers)
            
            if response.status_code == 200:
                result = response.json()
                
                print(f"  ✅ Status: {response.status_code}")
                print(f"  Overall Safe: {result.get('safe', 'unknown')}")
                print(f"  Overall Confidence: {result.get('overall_confidence', 0):.3f}")
                
                # Show category results
                categories = result.get('categories', [])
                for category in categories:
                    flag_status = "🚩" if category.get('flagged', False) else "✅"
                    cat_name = category.get('category', 'unknown')
                    confidence = category.get('confidence', 0)
                    print(f"  {flag_status} {cat_name}: {confidence:.3f}")
                    
            else:
                print(f"  ❌ Error: {response.status_code}")
                print(f"  Response: {response.text}")
                
        except Exception as e:
            print(f"  ❌ Exception: {e}")
    
    print(f"\n🎉 Testing completed!")
    print("\nExpected results with NudeNet:")
    print("• All simple colored images should be safe")
    print("• Nudity confidence should be very low (0.000)")
    print("• Other categories should also be low")
    print("• No false positives on simple images")

if __name__ == "__main__":
    test_nudity_api() 