#!/usr/bin/env python3
"""
Test script for API with AI-powered drugs detection

This script tests the full API integration with the new drugs detection system
"""

import requests
import io
from PIL import Image, ImageDraw
import numpy as np

# API configuration
API_BASE_URL = "http://localhost:7000"
ADMIN_TOKEN = "BdD--lvAf5SXLKFa98ji7GO6zhCv9iaNao4XWyAVrnA"

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

def image_to_bytes(image):
    """Convert PIL Image to bytes"""
    img_byte_arr = io.BytesIO()
    image.save(img_byte_arr, format='PNG')
    return img_byte_arr.getvalue()

def test_api_health():
    """Test API health endpoint"""
    print("🏥 Testing API health...")
    try:
        response = requests.get(f"{API_BASE_URL}/health")
        if response.status_code == 200:
            print("✅ API is healthy!")
            return True
        else:
            print(f"❌ API health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error connecting to API: {e}")
        return False

def test_moderation_endpoint(test_name, image):
    """Test the moderation endpoint with an image"""
    print(f"\n🔍 Testing: {test_name}")
    print("-" * 50)
    
    try:
        # Convert image to bytes
        image_bytes = image_to_bytes(image)
        
        # Prepare file upload
        files = {
            'file': (f"{test_name.lower().replace(' ', '_')}.png", image_bytes, 'image/png')
        }
        
        headers = {
            "Authorization": f"Bearer {ADMIN_TOKEN}"
        }
        
        # Make request
        response = requests.post(f"{API_BASE_URL}/moderate", files=files, headers=headers)
        
        if response.status_code == 200:
            result = response.json()
            
            print("📊 API Response:")
            print(f"   Safe: {result.get('safe', 'unknown')}")
            print(f"   Overall Confidence: {result.get('overall_confidence', 0):.3f}")
            
            categories = result.get('categories', [])
            for category in categories:
                cat_name = category.get('category', 'unknown')
                flagged = category.get('flagged', False)
                confidence = category.get('confidence', 0)
                status = "🚨 FLAGGED" if flagged else "✅ SAFE"
                print(f"   {cat_name}: {confidence:.3f} {status}")
            
            # Focus on drugs detection
            drugs_category = next((cat for cat in categories if cat.get('category') == 'drugs'), None)
            if drugs_category:
                print(f"\n🧪 Drugs Detection Details:")
                print(f"   Flagged: {drugs_category.get('flagged', False)}")
                print(f"   Confidence: {drugs_category.get('confidence', 0):.3f}")
                
                # Check for detailed detection info
                if 'details' in drugs_category:
                    details = drugs_category['details']
                    print(f"   Details: {details}")
            
            return True
            
        else:
            print(f"❌ API request failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing {test_name}: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_drugs_detection_api():
    """Test the drugs detection through the API"""
    print("🧪 Testing AI-powered drugs detection through API...")
    print("=" * 70)
    
    # First check API health
    if not test_api_health():
        print("❌ API is not healthy, cannot proceed with tests")
        return
    
    # Test cases
    test_cases = [
        ("Red solid color", create_test_image('red')),
        ("Blue solid color", create_test_image('blue')),
        ("White solid color", create_test_image('white')),
        ("Green solid color", create_test_image('green')),
        ("Pill-like objects", create_pill_like_image()),
        ("Powder-like texture", create_powder_like_image()),
    ]
    
    success_count = 0
    total_tests = len(test_cases)
    
    for test_name, test_image in test_cases:
        if test_moderation_endpoint(test_name, test_image):
            success_count += 1
    
    print("\n" + "=" * 70)
    print(f"🏁 API Testing Complete!")
    print(f"   Successful tests: {success_count}/{total_tests}")
    
    if success_count == total_tests:
        print("✅ All tests passed! Drugs detection API is working perfectly!")
    else:
        print(f"⚠️ {total_tests - success_count} tests failed")

if __name__ == "__main__":
    test_drugs_detection_api() 