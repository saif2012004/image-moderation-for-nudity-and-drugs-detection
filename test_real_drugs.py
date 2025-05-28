#!/usr/bin/env python3
"""
Test script for real drug detection with actual drug images

This script will help debug why the system isn't detecting obvious drug content
"""

import requests
import io
import sys
import base64
from PIL import Image

# Add app directory to path
sys.path.append('app')

from app.drugs_detector import detect_drugs

# API configuration
API_BASE_URL = "http://localhost:7000"
ADMIN_TOKEN = "BdD--lvAf5SXLKFa98ji7GO6zhCv9iaNao4XWyAVrnA"

def test_with_user_images():
    """Test with the actual images the user provided"""
    print("🧪 Testing Real Drug Detection")
    print("=" * 60)
    
    # Since we can't directly access the user's images, let's create representative test cases
    # and also test the API to see what's happening
    
    print("\n📤 Testing API with real drug-like scenarios...")
    
    # Test a simple case first
    test_simple_red_image()

def test_simple_red_image():
    """Test with a simple image to see baseline behavior"""
    print(f"\n🧪 Testing: Simple Red Image (Control Test)")
    print("-" * 50)
    
    # Create simple red image
    image = Image.new('RGB', (300, 300), 'red')
    img_byte_arr = io.BytesIO()
    image.save(img_byte_arr, format='PNG')
    image_data = img_byte_arr.getvalue()
    
    # Test direct detection
    print("🔍 Direct Drugs Detection:")
    try:
        result = detect_drugs(image_data, detailed=True)
        
        confidence = result.get('confidence', 0.0)
        is_drugs = result.get('is_drugs', False)
        method = result.get('method', 'unknown')
        detections = result.get('detections', {})
        
        print(f"  📊 Confidence: {confidence:.1%}")
        print(f"  🚨 Flagged as drugs: {is_drugs}")
        print(f"  🔧 Method: {method}")
        print(f"  📈 Detailed detections:")
        for detection_type, detection_conf in detections.items():
            print(f"    {detection_type}: {detection_conf:.1%}")
        
    except Exception as e:
        print(f"  ❌ Direct detection error: {e}")
    
    # Test API detection
    print(f"\n📡 API Detection:")
    test_api_call("Simple Red Image (Control)", image)

def test_api_call(test_name, test_image):
    """Test API call with given image"""
    # Convert image to bytes
    img_byte_arr = io.BytesIO()
    test_image.save(img_byte_arr, format='PNG')
    image_data = img_byte_arr.getvalue()
    
    # Test API call
    url = f"{API_BASE_URL}/moderate"
    headers = {"Authorization": f"Bearer {ADMIN_TOKEN}"}
    files = {"file": (f"{test_name.lower().replace(' ', '_')}.png", image_data, "image/png")}
    
    try:
        response = requests.post(url, headers=headers, files=files, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            
            print(f"  ✅ API Response received!")
            print(f"  📊 Overall Safe: {result.get('safe', 'unknown')}")
            print(f"  📊 Overall Confidence: {result.get('overall_confidence', 0):.1%}")
            
            # Check categories
            categories = result.get('categories', [])
            print(f"\n  📈 Category Analysis:")
            
            drugs_category = None
            for cat in categories:
                category_name = cat.get('category', 'unknown')
                confidence = cat.get('confidence', 0)
                flagged = cat.get('flagged', False)
                
                flag_emoji = "🚨" if flagged else "✅"
                status = "FLAGGED" if flagged else "Clean"
                
                print(f"    {flag_emoji} {category_name}: {confidence:.1%} - {status}")
                
                if category_name == 'drugs':
                    drugs_category = cat
            
            # Analyze drugs detection specifically
            print(f"\n  💊 DRUGS ANALYSIS:")
            if drugs_category:
                drugs_confidence = drugs_category.get('confidence', 0)
                drugs_flagged = drugs_category.get('flagged', False)
                
                print(f"     Drugs Confidence: {drugs_confidence:.1%}")
                print(f"     Current Threshold: 50%")
                print(f"     Should be flagged: {drugs_confidence > 0.5}")
                print(f"     Actually flagged: {drugs_flagged}")
                
                if drugs_confidence < 0.1:
                    print(f"     ✅ GOOD: Very low confidence for control image")
                else:
                    print(f"     ⚠️  WARNING: Unexpected confidence for simple image")
        else:
            print(f"  ❌ API Error: {response.status_code}")
            print(f"  Response: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"  ❌ Connection Error: {e}")

def debug_detection_parameters():
    """Debug the detection parameters to see what might be wrong"""
    print(f"\n🔧 DEBUGGING DETECTION PARAMETERS")
    print("=" * 60)
    
    try:
        from app.drugs_detector import DrugsDetector
        detector = DrugsDetector()
        
        print(f"📋 Current Detection Parameters:")
        print(f"  Pills detector:")
        for key, value in detector.pill_detector_params.items():
            print(f"    {key}: {value}")
        
        print(f"  Powder detector:")
        for key, value in detector.powder_detector_params.items():
            print(f"    {key}: {value}")
        
        print(f"  Plant detector:")
        for key, value in detector.plant_detector_params.items():
            print(f"    {key}: {value}")
        
        print(f"\n💡 ANALYSIS:")
        print(f"  - The validation logic might be too strict")
        print(f"  - Circle detection might be rejecting valid pills")
        print(f"  - Powder detection might need adjustment")
        print(f"  - Thresholds might be too high")
        
    except Exception as e:
        print(f"❌ Error debugging parameters: {e}")

def suggest_fixes():
    """Suggest what fixes might be needed"""
    print(f"\n🛠️  SUGGESTED FIXES FOR DRUG DETECTION")
    print("=" * 60)
    print(f"1. 🎯 RELAX VALIDATION RULES:")
    print(f"   - Make circle validation less strict")
    print(f"   - Allow more size variations for pills")
    print(f"   - Reduce edge smoothness requirements")
    
    print(f"\n2. 🔍 IMPROVE DETECTION METHODS:")
    print(f"   - Better color detection for white powders")
    print(f"   - More sensitive texture analysis")
    print(f"   - Better shape recognition for pills")
    
    print(f"\n3. ⚖️  ADJUST THRESHOLDS:")
    print(f"   - Lower confidence requirements")
    print(f"   - Reduce penalty for isolated detections")
    print(f"   - More aggressive confidence boosting")
    
    print(f"\n4. 🧪 TEST WITH REALISTIC SCENARIOS:")
    print(f"   - Create test images with multiple pills")
    print(f"   - Test with white powder patterns")
    print(f"   - Test with plant material colors")

if __name__ == "__main__":
    test_with_user_images()
    debug_detection_parameters()
    suggest_fixes()
    
    print(f"\n🎯 NEXT STEPS:")
    print(f"   1. Run this test to see current behavior")
    print(f"   2. Upload one of your drug images to the API")
    print(f"   3. Check what confidence levels we're getting")
    print(f"   4. Adjust detection parameters accordingly") 