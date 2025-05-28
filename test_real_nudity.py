#!/usr/bin/env python3
"""
Test real nudity detection to understand why it's failing
"""

import requests
import io
from PIL import Image
import os

def test_real_nudity_detection():
    """Test with various image types to understand the issue"""
    token = "BdD--lvAf5SXLKFa98ji7GO6zhCv9iaNao4XWyAVrnA"
    headers = {"Authorization": f"Bearer {token}"}
    base_url = "http://localhost:7000"
    
    print("🚨 CRITICAL NUDITY DETECTION TEST")
    print("=" * 60)
    
    # Test 1: Check if we can test with a known nudity image
    print("1️⃣ Testing NudeNet with different image types")
    
    try:
        from app.nudity_detector import detect_nudity
        
        # Create a more realistic skin-toned image with body-like shapes
        print("\n📸 Creating body-like test image...")
        body_img = Image.new('RGB', (400, 600), (222, 184, 135))  # Skin color
        pixels = body_img.load()
        
        # Create body-like shapes
        # Torso area
        for i in range(150, 250):
            for j in range(200, 400):
                pixels[i, j] = (200, 160, 120)  # Darker skin
        
        # Breast-like areas
        for i in range(120, 160):
            for j in range(220, 260):
                pixels[i, j] = (180, 140, 100)  # Even darker
        for i in range(120, 160):
            for j in range(340, 380):
                pixels[i, j] = (180, 140, 100)  # Even darker
        
        # Lower body area
        for i in range(180, 220):
            for j in range(280, 320):
                pixels[i, j] = (160, 120, 80)  # Darkest
        
        body_img.save('test_body.jpg', 'JPEG', quality=95)
        print("✅ Created body-like test image")
        
        # Test with NudeNet
        with open('test_body.jpg', 'rb') as f:
            body_data = f.read()
        
        result = detect_nudity(body_data, detailed=True)
        print(f"\n🔍 Body-like image results:")
        print(f"   Method: {result.get('method', 'unknown')}")
        print(f"   Is nude: {result.get('is_nude', False)}")
        print(f"   Confidence: {result.get('confidence', 0):.3f}")
        
        if 'details' in result:
            details = result['details']
            print(f"   All detections: {details.get('all_detections', 0)}")
            print(f"   Nude detections: {details.get('nude_detections', 0)}")
            print(f"   Safe detections: {details.get('safe_detections', 0)}")
        
        if 'nude_parts' in result and result['nude_parts']:
            print(f"   Detected parts:")
            for part in result['nude_parts']:
                print(f"     - {part['part']}: {part['confidence']:.3f}")
        
        # Clean up
        if os.path.exists('test_body.jpg'):
            os.remove('test_body.jpg')
        
    except Exception as e:
        print(f"❌ Error testing body-like image: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("🎯 ANALYSIS OF THE PROBLEM:")
    print()
    print("Based on your report that an obvious nudity image got 5% confidence,")
    print("the issue is likely one of these:")
    print()
    print("1. 🖼️  IMAGE QUALITY/FORMAT:")
    print("   - NudeNet might need higher resolution images")
    print("   - JPEG compression might be affecting detection")
    print("   - Image might be too small/large for the model")
    print()
    print("2. 🤖 MODEL THRESHOLD:")
    print("   - NudeNet might have very high internal thresholds")
    print("   - Individual body part detection might be failing")
    print("   - Model might be too conservative")
    print()
    print("3. 🔧 IMPLEMENTATION ISSUE:")
    print("   - Image preprocessing might be wrong")
    print("   - Model loading might have failed silently")
    print("   - Detection logic might have bugs")
    print()
    print("🚨 IMMEDIATE FIXES NEEDED:")
    print("1. Lower the nudity flagging threshold from 60% to 30%")
    print("2. Add better logging to see what NudeNet actually detects")
    print("3. Test with known nudity images from NudeNet examples")
    print("4. Consider using NudeClassifier instead of NudeDetector")

if __name__ == "__main__":
    test_real_nudity_detection() 