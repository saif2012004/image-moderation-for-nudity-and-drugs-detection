#!/usr/bin/env python3
"""
Test script to verify the fixed threshold configuration

This script tests that 71.3% drugs confidence now properly flags images
"""

import requests
import io
from PIL import Image, ImageDraw

# API configuration
API_BASE_URL = "http://localhost:7000"
ADMIN_TOKEN = "BdD--lvAf5SXLKFa98ji7GO6zhCv9iaNao4XWyAVrnA"

def create_drugs_image():
    """Create the same image that produced 71.3% confidence"""
    image = Image.new('RGB', (400, 400), 'white')
    draw = ImageDraw.Draw(image)
    
    # Draw many pill-like circles (white pills) similar to the user's image
    for i in range(8):
        for j in range(3):
            x = 50 + i * 40
            y = 100 + j * 60
            radius = 15
            # Draw white circles with borders (pills)
            draw.ellipse([x-radius, y-radius, x+radius, y+radius], 
                        fill='white', outline='gray', width=3)
    
    # Add some powder-like texture areas
    for i in range(5):
        x = 30 + i * 60
        y = 300
        # Draw irregular powder piles
        draw.ellipse([x, y, x+40, y+20], fill='lightgray', outline='darkgray')
    
    # Add syringe-like objects
    for i in range(3):
        x = 80 + i * 100
        y = 350
        # Draw thin elongated rectangles (syringes)
        draw.rectangle([x, y, x+60, y+8], fill='silver', outline='black')
        draw.circle([x+60, y+4], 3, fill='red')  # needle tip
    
    return image

def test_threshold_fix():
    """Test that the fixed threshold properly flags drugs content"""
    print("🧪 Testing Fixed Threshold Configuration")
    print("=" * 50)
    
    # Create test image
    test_image = create_drugs_image()
    
    # Convert to bytes
    img_byte_arr = io.BytesIO()
    test_image.save(img_byte_arr, format='PNG')
    image_data = img_byte_arr.getvalue()
    
    # Test API call
    url = f"{API_BASE_URL}/moderate"
    headers = {"Authorization": f"Bearer {ADMIN_TOKEN}"}
    files = {"file": ("test_drugs.png", image_data, "image/png")}
    
    try:
        print("📤 Uploading test image to API...")
        response = requests.post(url, headers=headers, files=files, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            
            print("✅ API Response received!")
            print(f"📊 Overall Safe: {result.get('safe', 'unknown')}")
            print(f"📊 Overall Confidence: {result.get('overall_confidence', 0):.1%}")
            
            # Check categories
            categories = result.get('categories', [])
            print("\n📈 Category Analysis:")
            
            drugs_category = None
            for cat in categories:
                category_name = cat.get('category', 'unknown')
                confidence = cat.get('confidence', 0)
                flagged = cat.get('flagged', False)
                
                flag_emoji = "🚨" if flagged else "✅"
                status = "FLAGGED" if flagged else "Clean"
                
                print(f"  {flag_emoji} {category_name}: {confidence:.1%} - {status}")
                
                if category_name == 'drugs':
                    drugs_category = cat
            
            # Analyze the fix
            print(f"\n🎯 THRESHOLD FIX ANALYSIS:")
            if drugs_category:
                drugs_confidence = drugs_category.get('confidence', 0)
                drugs_flagged = drugs_category.get('flagged', False)
                
                print(f"   Drugs Confidence: {drugs_confidence:.1%}")
                print(f"   Current Threshold: 50%")
                print(f"   Should be flagged: {drugs_confidence > 0.5}")
                print(f"   Actually flagged: {drugs_flagged}")
                
                if drugs_confidence > 0.5 and drugs_flagged:
                    print("   ✅ THRESHOLD FIX SUCCESSFUL!")
                    print("   🎉 System now properly flags high-confidence drugs content!")
                elif drugs_confidence > 0.5 and not drugs_flagged:
                    print("   ❌ THRESHOLD FIX FAILED!")
                    print("   🚨 High confidence drugs still not being flagged!")
                else:
                    print(f"   ⚠️ Low confidence ({drugs_confidence:.1%}) - test inconclusive")
            
            # Overall result analysis
            overall_safe = result.get('safe', True)
            if not overall_safe:
                print(f"\n🚨 OVERALL RESULT: Image properly flagged as UNSAFE!")
                print(f"   ✅ The system is now working correctly!")
            else:
                print(f"\n⚠️ OVERALL RESULT: Image still marked as Safe")
                print(f"   This could be due to low confidence or other issues")
                
        else:
            print(f"❌ API Error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Connection Error: {e}")
        print("Make sure the API is running on localhost:7000")

if __name__ == "__main__":
    test_threshold_fix()
    
    print(f"\n🎯 EXPECTED BEHAVIOR:")
    print(f"   - Drugs confidence should be ~70%+ (high)")
    print(f"   - With 50% threshold, it should be FLAGGED")
    print(f"   - Overall image should be marked as UNSAFE")
    print(f"   - This fixes the previous issue where 71.3% was not flagged") 