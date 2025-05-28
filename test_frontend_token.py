#!/usr/bin/env python3
"""
Test script to verify the token works with the moderation endpoint
"""

import requests
from PIL import Image
import io

def test_moderation_with_token():
    """Test moderation endpoint with the admin token"""
    token = "BdD--lvAf5SXLKFa98ji7GO6zhCv9iaNao4XWyAVrnA"
    base_url = "http://localhost:7000"
    
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    print("🧪 Testing Moderation Endpoint with Admin Token")
    print("=" * 50)
    print(f"Token: {token}")
    print()
    
    # Create a simple test image
    img = Image.new('RGB', (100, 100), (255, 0, 0))  # Red image
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='JPEG')
    img_data = img_bytes.getvalue()
    
    # Test moderation endpoint
    print("📡 Testing: /moderate")
    try:
        files = {
            'file': ('test.jpg', img_data, 'image/jpeg')
        }
        
        response = requests.post(f"{base_url}/moderate", files=files, headers=headers)
        print(f"  Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"  ✅ Success!")
            print(f"  Safe: {result.get('safe')}")
            print(f"  Overall Confidence: {result.get('overall_confidence', 0):.3f}")
            
            categories = result.get('categories', [])
            for category in categories:
                cat_name = category.get('category')
                confidence = category.get('confidence', 0)
                flagged = category.get('flagged', False)
                status_icon = "🚩" if flagged else "✅"
                print(f"  {status_icon} {cat_name}: {confidence:.3f}")
        else:
            print(f"  ❌ Error: {response.text}")
            
    except Exception as e:
        print(f"  ❌ Exception: {e}")
    
    print()
    print("🎯 Conclusion:")
    print("If this works, the token is valid and the issue is in the frontend.")

if __name__ == "__main__":
    test_moderation_with_token() 