#!/usr/bin/env python3
import requests
import json
from PIL import Image
import io

# Create a simple test image
def create_test_image():
    """Create a simple test image"""
    img = Image.new('RGB', (100, 100), color='white')
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='JPEG')
    img_bytes.seek(0)
    return img_bytes

def test_moderation_categories():
    """Test that the moderation API returns only the 4 expected categories"""
    
    # Admin token (replace with actual token)
    admin_token = "BdD--lvAf5SXLKFa98ji7GO6zhCv9iaNao4XWyAVrnA"
    
    # Expected categories
    expected_categories = {"nudity", "drugs", "weapons", "hate_symbols"}
    
    print("Testing moderation API with updated categories...")
    
    # Create test image
    test_image = create_test_image()
    
    # Test moderation endpoint
    url = "http://localhost:7000/moderate"
    headers = {"Authorization": f"Bearer {admin_token}"}
    files = {"file": ("test.jpg", test_image, "image/jpeg")}
    
    try:
        response = requests.post(url, headers=headers, files=files)
        
        if response.status_code == 200:
            result = response.json()
            print("\n✅ Moderation API Response:")
            print(json.dumps(result, indent=2))
            
            # Check categories
            actual_categories = {cat["category"] for cat in result["categories"]}
            print(f"\n📊 Expected categories: {sorted(expected_categories)}")
            print(f"📊 Actual categories: {sorted(actual_categories)}")
            
            if actual_categories == expected_categories:
                print("\n✅ SUCCESS: Categories match expected values!")
                return True
            else:
                print("\n❌ ERROR: Categories don't match!")
                missing = expected_categories - actual_categories
                extra = actual_categories - expected_categories
                if missing:
                    print(f"Missing categories: {missing}")
                if extra:
                    print(f"Extra categories: {extra}")
                return False
        else:
            print(f"\n❌ ERROR: HTTP {response.status_code}")
            print(response.text)
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"\n❌ ERROR: Failed to connect to API: {e}")
        return False

if __name__ == "__main__":
    test_moderation_categories() 