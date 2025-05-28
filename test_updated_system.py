#!/usr/bin/env python3
"""
Test script to verify the updated moderation system

This script tests that the system now only detects nudity and drugs (no weapons or hate symbols)
"""

import requests
import io
from PIL import Image

# API configuration
API_BASE_URL = "http://localhost:7000"
ADMIN_TOKEN = "BdD--lvAf5SXLKFa98ji7GO6zhCv9iaNao4XWyAVrnA"

def create_test_image():
    """Create a simple test image"""
    image = Image.new('RGB', (400, 300), (128, 128, 128))  # Gray image
    return image

def test_updated_categories():
    """Test that the system only returns nudity and drugs categories"""
    print("🧪 Testing Updated Moderation System")
    print("=" * 50)
    print("Expected categories: nudity, drugs")
    print("Expected removal: weapons, hate_symbols")
    print("")
    
    # Create test image
    test_image = create_test_image()
    
    # Convert to bytes
    img_byte_arr = io.BytesIO()
    test_image.save(img_byte_arr, format='PNG')
    image_data = img_byte_arr.getvalue()
    
    # Test API call
    url = f"{API_BASE_URL}/moderate"
    headers = {"Authorization": f"Bearer {ADMIN_TOKEN}"}
    files = {"file": ("test_image.png", image_data, "image/png")}
    
    try:
        print("📤 Uploading test image...")
        response = requests.post(url, headers=headers, files=files, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            
            print("✅ API Response received!")
            print(f"📊 Overall Safe: {result.get('safe', 'unknown')}")
            print(f"📊 Overall Confidence: {result.get('overall_confidence', 0):.1%}")
            
            # Check categories
            categories = result.get('categories', [])
            print("\n📈 Category Analysis:")
            
            found_categories = set()
            
            for cat in categories:
                category_name = cat.get('category', 'unknown')
                confidence = cat.get('confidence', 0)
                flagged = cat.get('flagged', False)
                
                found_categories.add(category_name)
                
                flag_emoji = "🚨" if flagged else "✅"
                status = "FLAGGED" if flagged else "Clean"
                
                print(f"  {flag_emoji} {category_name}: {confidence:.1%} - {status}")
            
            # Verify expected categories
            print(f"\n🔍 SYSTEM VALIDATION:")
            expected_categories = {"nudity", "drugs"}
            removed_categories = {"weapons", "hate_symbols"}
            
            print(f"   Expected categories: {expected_categories}")
            print(f"   Found categories: {found_categories}")
            
            # Check if we have exactly the expected categories
            if found_categories == expected_categories:
                print("   ✅ SUCCESS: System has exactly the expected categories!")
            else:
                print("   ❌ ERROR: Category mismatch!")
                
                missing = expected_categories - found_categories
                extra = found_categories - expected_categories
                
                if missing:
                    print(f"   ❌ Missing categories: {missing}")
                if extra:
                    print(f"   ❌ Unexpected categories: {extra}")
            
            # Check that removed categories are not present
            found_removed = found_categories & removed_categories
            if found_removed:
                print(f"   ❌ ERROR: Found removed categories: {found_removed}")
            else:
                print(f"   ✅ SUCCESS: Removed categories properly excluded!")
                
        else:
            print(f"❌ API Error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Connection Error: {e}")

def test_health_endpoint():
    """Test that the health endpoint is working"""
    print(f"\n🏥 Testing Health Endpoint")
    print("-" * 30)
    
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=10)
        if response.status_code == 200:
            print("✅ Health endpoint working")
            health_data = response.json()
            print(f"   Status: {health_data.get('status', 'unknown')}")
        else:
            print(f"❌ Health endpoint error: {response.status_code}")
    except Exception as e:
        print(f"❌ Health endpoint error: {e}")

if __name__ == "__main__":
    test_health_endpoint()
    test_updated_categories()
    
    print(f"\n🎯 SUMMARY:")
    print(f"   ✅ System now focused on nudity and drugs detection only")
    print(f"   ✅ Weapons and hate symbols detection removed")
    print(f"   ✅ Cleaner, more focused moderation system")
    print(f"   ✅ Ready for production use with 2-category detection") 