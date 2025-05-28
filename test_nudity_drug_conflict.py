#!/usr/bin/env python3
"""
Test script to identify and fix the nudity-drugs cross-detection issue

This script will test nudity images to see why they're getting flagged for drugs
"""

import requests
import io
from PIL import Image, ImageDraw
import random

# API configuration
API_BASE_URL = "http://localhost:7000"
ADMIN_TOKEN = "BdD--lvAf5SXLKFa98ji7GO6zhCv9iaNao4XWyAVrnA"

def create_nudity_test_images():
    """Create test images that simulate nudity content"""
    
    # Test 1: Simple skin tone image
    skin_image = Image.new('RGB', (400, 600), (220, 180, 140))  # Skin tone
    
    # Test 2: Image with circular shapes (breast-like)
    circular_image = Image.new('RGB', (400, 600), (220, 180, 140))
    draw = ImageDraw.Draw(circular_image)
    
    # Draw some circular shapes that might be mistaken for pills
    draw.ellipse([150, 200, 250, 300], fill=(210, 170, 130), outline=(200, 160, 120))
    draw.ellipse([200, 350, 300, 450], fill=(210, 170, 130), outline=(200, 160, 120))
    
    # Test 3: Image with smooth gradients (body contours)
    gradient_image = Image.new('RGB', (400, 600), 'white')
    pixels = gradient_image.load()
    for x in range(400):
        for y in range(600):
            # Create smooth gradient
            intensity = int(220 - (x + y) * 0.1) % 256
            pixels[x, y] = (intensity, intensity - 20, intensity - 40)
    
    # Test 4: Image with multiple skin-colored circular areas
    multi_circle = Image.new('RGB', (400, 600), (240, 200, 160))
    draw = ImageDraw.Draw(multi_circle)
    
    # Multiple circular areas that might trigger pill detection
    for i in range(8):
        x = random.randint(50, 350)
        y = random.randint(50, 550)
        r = random.randint(15, 40)
        tone = random.randint(200, 230)
        draw.ellipse([x-r, y-r, x+r, y+r], fill=(tone, tone-20, tone-40))
    
    return [
        ("Simple Skin Tone", skin_image),
        ("Circular Shapes (Breast-like)", circular_image),
        ("Smooth Gradients (Body Contours)", gradient_image),
        ("Multiple Skin Circles", multi_circle)
    ]

def test_nudity_images():
    """Test nudity images to see drug detection issues"""
    print("🧪 Testing Nudity Images for Drug False Positives")
    print("=" * 70)
    
    test_images = create_nudity_test_images()
    
    for test_name, test_image in test_images:
        test_api_call(test_name, test_image)

def test_api_call(test_name, test_image):
    """Test API call with given image"""
    print(f"\n🧪 Testing: {test_name}")
    print("-" * 60)
    
    # Convert image to bytes
    img_byte_arr = io.BytesIO()
    test_image.save(img_byte_arr, format='PNG')
    image_data = img_byte_arr.getvalue()
    
    # Test API call
    url = f"{API_BASE_URL}/moderate"
    headers = {"Authorization": f"Bearer {ADMIN_TOKEN}"}
    files = {"file": (f"{test_name.lower().replace(' ', '_')}.png", image_data, "image/png")}
    
    try:
        print("📤 Uploading to API...")
        response = requests.post(url, headers=headers, files=files, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            
            print("✅ API Response received!")
            print(f"📊 Overall Safe: {result.get('safe', 'unknown')}")
            print(f"📊 Overall Confidence: {result.get('overall_confidence', 0):.1%}")
            
            # Check categories
            categories = result.get('categories', [])
            print("\n📈 Category Analysis:")
            
            nudity_category = None
            drugs_category = None
            
            for cat in categories:
                category_name = cat.get('category', 'unknown')
                confidence = cat.get('confidence', 0)
                flagged = cat.get('flagged', False)
                
                flag_emoji = "🚨" if flagged else "✅"
                status = "FLAGGED" if flagged else "Clean"
                
                print(f"  {flag_emoji} {category_name}: {confidence:.1%} - {status}")
                
                if category_name == 'nudity':
                    nudity_category = cat
                elif category_name == 'drugs':
                    drugs_category = cat
            
            # Analyze the conflict
            print(f"\n🔍 CROSS-DETECTION ANALYSIS:")
            
            if nudity_category and drugs_category:
                nudity_conf = nudity_category.get('confidence', 0)
                drugs_conf = drugs_category.get('confidence', 0)
                
                print(f"   Nudity Confidence: {nudity_conf:.1%}")
                print(f"   Drugs Confidence: {drugs_conf:.1%}")
                
                # Check for problematic cross-detection
                if nudity_conf > 0.3 and drugs_conf > 0.3:
                    print("   ❌ PROBLEM: Both nudity AND drugs detected!")
                    print("   🔧 Issue: Drug detector is likely detecting body parts as pills")
                elif nudity_conf > 0.5 and drugs_conf > 0.1:
                    print("   ⚠️  WARNING: Nudity image triggering some drug detection")
                    print("   🔧 Issue: Need to improve drug detector to exclude skin/body shapes")
                elif nudity_conf > 0.3 and drugs_conf < 0.1:
                    print("   ✅ GOOD: Nudity detected, drugs properly excluded")
                else:
                    print("   ✅ ACCEPTABLE: Low cross-detection")
                    
        else:
            print(f"❌ API Error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Connection Error: {e}")

def suggest_fixes():
    """Suggest fixes for the nudity-drugs cross-detection issue"""
    print(f"\n🛠️  SUGGESTED FIXES FOR CROSS-DETECTION")
    print("=" * 60)
    print(f"1. 🎯 IMPROVE SHAPE VALIDATION:")
    print(f"   - Detect skin tones and exclude from pill detection")
    print(f"   - Add body part recognition to avoid false pills")
    print(f"   - Improve circle validation to exclude breast-like shapes")
    
    print(f"\n2. 🔍 ADD CONTEXT ANALYSIS:")
    print(f"   - If nudity confidence > 50%, reduce drug confidence")
    print(f"   - Check for human body context before flagging pills")
    print(f"   - Use skin color analysis to filter out body parts")
    
    print(f"\n3. ⚖️  ADJUST DETECTION LOGIC:")
    print(f"   - Prioritize nudity detection over drug detection")
    print(f"   - Add mutual exclusion rules for conflicting categories")
    print(f"   - Improve texture analysis to distinguish skin vs. pills")
    
    print(f"\n4. 🧪 ENHANCE VALIDATION:")
    print(f"   - Check for human proportions before drug detection")
    print(f"   - Add edge analysis to distinguish body curves from pills")
    print(f"   - Implement better background context analysis")

if __name__ == "__main__":
    test_nudity_images()
    suggest_fixes()
    
    print(f"\n🎯 NEXT STEPS:")
    print(f"   1. Identify which nudity patterns trigger drug detection")
    print(f"   2. Add skin tone detection to drug validator")
    print(f"   3. Implement context-aware detection rules")
    print(f"   4. Test with real nudity images to verify fixes") 