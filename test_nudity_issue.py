#!/usr/bin/env python3
"""
Test script to debug nudity detection issues
"""

import requests
import io
from PIL import Image

def test_nudity_detection():
    """Test the nudity detection with different images"""
    token = "BdD--lvAf5SXLKFa98ji7GO6zhCv9iaNao4XWyAVrnA"
    headers = {"Authorization": f"Bearer {token}"}
    base_url = "http://localhost:7000"
    
    print("🔍 Testing Nudity Detection")
    print("=" * 50)
    
    # Test 1: Simple red image (should be safe)
    print("1️⃣ Testing Simple Red Image via API")
    img = Image.new('RGB', (100, 100), 'red')
    buffer = io.BytesIO()
    img.save(buffer, format='JPEG')
    image_data = buffer.getvalue()
    
    # Fix: Use 'file' not 'image' for the API
    files = {'file': ('red_test.jpg', image_data, 'image/jpeg')}
    response = requests.post(f'{base_url}/moderate', files=files, headers=headers)
    
    if response.status_code == 200:
        result = response.json()
        nudity_cat = next((cat for cat in result['categories'] if cat['category'] == 'nudity'), None)
        if nudity_cat:
            print(f"   Nudity confidence: {nudity_cat['confidence']:.3f}")
            print(f"   Flagged: {nudity_cat['flagged']}")
        print(f"   Overall safe: {result['safe']}")
    else:
        print(f"   Error: {response.text}")
    
    print()
    
    # Test 2: Check if NudeNet is actually working
    print("2️⃣ Testing NudeNet Directly")
    try:
        from app.nudity_detector import detect_nudity
        
        # Test with red image
        result = detect_nudity(image_data, detailed=True)
        print(f"   Method: {result.get('method', 'unknown')}")
        print(f"   Is nude: {result.get('is_nude', False)}")
        print(f"   Confidence: {result.get('confidence', 0):.3f}")
        print(f"   Safe score: {result.get('safe_score', 0):.3f}")
        print(f"   Unsafe score: {result.get('unsafe_score', 0):.3f}")
        
        if 'nude_parts_count' in result:
            print(f"   Nude parts detected: {result['nude_parts_count']}")
            
        if 'details' in result:
            details = result['details']
            print(f"   All detections: {details.get('all_detections', 0)}")
            print(f"   Nude detections: {details.get('nude_detections', 0)}")
            print(f"   Safe detections: {details.get('safe_detections', 0)}")
        
    except Exception as e:
        print(f"   Error testing NudeNet directly: {e}")
        import traceback
        traceback.print_exc()
    
    print()
    
    # Test 3: Check thresholds
    print("3️⃣ Checking Flagging Thresholds")
    try:
        from app.moderation import ModerationService
        service = ModerationService()
        
        # Test different confidence levels
        test_confidences = [0.05, 0.3, 0.5, 0.6, 0.7, 0.8]
        for conf in test_confidences:
            flagged = service._should_flag('nudity', conf)
            print(f"   Confidence {conf:.2f}: {'FLAGGED' if flagged else 'safe'}")
            
    except Exception as e:
        print(f"   Error checking thresholds: {e}")
    
    print()
    
    # Test 4: Test with a skin-colored image (more realistic)
    print("4️⃣ Testing Skin-Colored Image")
    try:
        # Create a skin-colored image
        skin_img = Image.new('RGB', (200, 200), (222, 184, 135))  # Skin color
        skin_buffer = io.BytesIO()
        skin_img.save(skin_buffer, format='JPEG')
        skin_data = skin_buffer.getvalue()
        
        # Test with NudeNet directly
        skin_result = detect_nudity(skin_data, detailed=True)
        print(f"   Skin image - Method: {skin_result.get('method', 'unknown')}")
        print(f"   Skin image - Is nude: {skin_result.get('is_nude', False)}")
        print(f"   Skin image - Confidence: {skin_result.get('confidence', 0):.3f}")
        
        if 'details' in skin_result:
            details = skin_result['details']
            print(f"   Skin image - All detections: {details.get('all_detections', 0)}")
        
    except Exception as e:
        print(f"   Error testing skin image: {e}")
    
    print()
    print("🚨 CRITICAL ISSUE ANALYSIS:")
    print("If NudeNet is working but giving 0.000 confidence for obvious nudity,")
    print("there might be an issue with:")
    print("1. Image preprocessing/format")
    print("2. NudeNet model loading")
    print("3. Detection threshold too high")
    print("4. Image resolution/quality issues")

if __name__ == "__main__":
    test_nudity_detection() 