#!/usr/bin/env python3
"""
Test with real image upload to understand the nudity detection issue
"""

import requests
import json

def test_real_image_upload():
    """Test uploading a real image to see what happens"""
    token = "BdD--lvAf5SXLKFa98ji7GO6zhCv9iaNao4XWyAVrnA"
    headers = {"Authorization": f"Bearer {token}"}
    base_url = "http://localhost:7000"
    
    print("🚨 REAL IMAGE NUDITY DETECTION TEST")
    print("=" * 60)
    
    # Instructions for user
    print("📋 INSTRUCTIONS:")
    print("1. Save your nudity image as 'test_image.jpg' in this directory")
    print("2. Run this script to test the actual detection")
    print("3. We'll see exactly what NudeNet detects")
    print()
    
    # Check if test image exists
    import os
    if not os.path.exists('test_image.jpg'):
        print("❌ Please save your nudity image as 'test_image.jpg' and run again")
        print("   This will help us debug why it's not being detected properly")
        return
    
    print("✅ Found test_image.jpg - analyzing...")
    
    # Test 1: Direct NudeNet analysis
    print("\n1️⃣ Direct NudeNet Analysis")
    try:
        from app.nudity_detector import detect_nudity
        
        with open('test_image.jpg', 'rb') as f:
            image_data = f.read()
        
        result = detect_nudity(image_data, detailed=True)
        
        print(f"   Method: {result.get('method', 'unknown')}")
        print(f"   Is nude: {result.get('is_nude', False)}")
        print(f"   Confidence: {result.get('confidence', 0):.3f}")
        print(f"   Safe score: {result.get('safe_score', 0):.3f}")
        print(f"   Unsafe score: {result.get('unsafe_score', 0):.3f}")
        
        if 'details' in result:
            details = result['details']
            print(f"   All detections: {details.get('all_detections', 0)}")
            print(f"   Nude detections: {details.get('nude_detections', 0)}")
            print(f"   Safe detections: {details.get('safe_detections', 0)}")
        
        if 'nude_parts' in result and result['nude_parts']:
            print(f"   🔍 Detected nude parts:")
            for part in result['nude_parts']:
                print(f"     - {part['part']}: {part['confidence']:.3f}")
        else:
            print("   ❌ No nude parts detected")
        
    except Exception as e:
        print(f"   ❌ Error in direct analysis: {e}")
        import traceback
        traceback.print_exc()
    
    # Test 2: API upload
    print("\n2️⃣ API Upload Test")
    try:
        with open('test_image.jpg', 'rb') as f:
            files = {'file': ('test_image.jpg', f, 'image/jpeg')}
            response = requests.post(f'{base_url}/moderate', files=files, headers=headers)
        
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ API Response successful")
            print(f"   Overall safe: {result['safe']}")
            print(f"   Overall confidence: {result['overall_confidence']:.3f}")
            
            for category in result['categories']:
                if category['category'] == 'nudity':
                    print(f"   🔍 Nudity category:")
                    print(f"     - Confidence: {category['confidence']:.3f}")
                    print(f"     - Flagged: {category['flagged']}")
                    
                    # Check threshold
                    if category['confidence'] > 0.3:
                        print(f"     ✅ Above 30% threshold - should be flagged")
                    else:
                        print(f"     ❌ Below 30% threshold - not flagged")
        else:
            print(f"   ❌ API Error: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Error in API test: {e}")
    
    # Test 3: Raw NudeNet detector test
    print("\n3️⃣ Raw NudeNet Detector Test")
    try:
        from nudenet import NudeDetector
        detector = NudeDetector()
        
        detections = detector.detect('test_image.jpg')
        print(f"   Raw NudeNet detections: {len(detections)}")
        
        if detections:
            print(f"   🔍 All detected parts:")
            for detection in detections:
                class_name = detection['class']
                score = detection['score']
                box = detection['box']
                print(f"     - {class_name}: {score:.3f} (box: {box})")
        else:
            print(f"   ❌ NudeNet detected nothing in this image")
            print(f"   This means either:")
            print(f"     1. Image quality is too low")
            print(f"     2. Image doesn't contain recognizable body parts")
            print(f"     3. NudeNet model has issues")
            
    except Exception as e:
        print(f"   ❌ Error in raw NudeNet test: {e}")
    
    print("\n" + "=" * 60)
    print("🎯 DIAGNOSIS:")
    print("If NudeNet detects 0 parts in your real nudity image:")
    print("1. 🖼️  Image might be too small/low quality")
    print("2. 🤖 NudeNet might not recognize the specific content")
    print("3. 🔧 We need to implement alternative detection methods")
    print()
    print("💡 SOLUTIONS:")
    print("1. Try with a higher resolution image (at least 224x224)")
    print("2. Ensure the image clearly shows recognizable body parts")
    print("3. Consider implementing backup detection methods")

if __name__ == "__main__":
    test_real_image_upload() 