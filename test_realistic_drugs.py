#!/usr/bin/env python3
"""
Test script for realistic drug scenarios

This script creates test images similar to what the user showed us
"""

import requests
import io
import numpy as np
from PIL import Image, ImageDraw
import random

# API configuration
API_BASE_URL = "http://localhost:7000"
ADMIN_TOKEN = "BdD--lvAf5SXLKFa98ji7GO6zhCv9iaNao4XWyAVrnA"

def create_pills_scattered_image(size=(600, 400)):
    """Create an image with many scattered pills like the user's first image"""
    image = Image.new('RGB', size, 'darkgray')  # Dark background like wooden table
    draw = ImageDraw.Draw(image)
    
    # Create many pills of different colors and sizes
    pill_colors = ['white', 'red', 'blue', 'yellow', 'orange', 'pink', 'lightblue', 'lightgreen']
    
    for i in range(40):  # Many pills like in the user's image
        # Random position
        x = random.randint(20, size[0] - 20)
        y = random.randint(20, size[1] - 20)
        
        # Random size (realistic pill sizes)
        radius = random.randint(8, 25)
        
        # Random color
        color = random.choice(pill_colors)
        
        # Draw pill as circle
        draw.ellipse([x-radius, y-radius, x+radius, y+radius], fill=color, outline='gray')
        
        # Add some pills as capsules (elongated)
        if random.random() < 0.3:  # 30% chance of capsule
            width = random.randint(12, 20)
            height = random.randint(6, 10)
            draw.ellipse([x-width, y-height, x+width, y+height], fill=color, outline='gray')
    
    return image

def create_white_powder_image(size=(600, 400)):
    """Create an image with white powder like the user's skull image"""
    image = Image.new('RGB', size, 'black')  # Dark background
    draw = ImageDraw.Draw(image)
    
    # Create white powder areas
    # Main powder area
    draw.ellipse([100, 100, 500, 300], fill='white', outline='lightgray')
    
    # Additional powder scattered around
    for i in range(20):
        x = random.randint(50, size[0] - 50)
        y = random.randint(50, size[1] - 50)
        radius = random.randint(5, 20)
        draw.ellipse([x-radius, y-radius, x+radius, y+radius], fill='white')
    
    # Draw some lines like in cocaine images
    for i in range(4):
        y = 350 + i * 10
        draw.rectangle([100, y, 500, y+3], fill='white')
    
    return image

def create_cannabis_image(size=(600, 400)):
    """Create an image simulating cannabis plant material"""
    image = Image.new('RGB', size, 'darkgreen')
    draw = ImageDraw.Draw(image)
    
    # Create green plant-like textures
    for i in range(50):
        x = random.randint(50, size[0] - 50)
        y = random.randint(50, size[1] - 50)
        
        # Draw irregular green shapes
        points = []
        for j in range(6):
            angle = j * 60 + random.randint(-20, 20)
            radius = random.randint(10, 30)
            px = x + radius * np.cos(np.radians(angle))
            py = y + radius * np.sin(np.radians(angle))
            points.append((px, py))
        
        draw.polygon(points, fill='green', outline='darkgreen')
    
    # Add some brown/dried areas
    for i in range(10):
        x = random.randint(50, size[0] - 50)
        y = random.randint(50, size[1] - 50)
        radius = random.randint(15, 40)
        draw.ellipse([x-radius, y-radius, x+radius, y+radius], fill='brown')
    
    return image

def create_mixed_pills_image(size=(600, 400)):
    """Create an image with many different pills and capsules"""
    image = Image.new('RGB', size, 'lightgray')
    draw = ImageDraw.Draw(image)
    
    # Different pill types
    colors = ['white', 'red', 'blue', 'yellow', 'orange', 'pink', 'lightblue', 'green', 'purple']
    
    for i in range(60):  # Lots of pills
        x = random.randint(30, size[0] - 30)
        y = random.randint(30, size[1] - 30)
        
        pill_type = random.choice(['circle', 'oval', 'capsule'])
        color = random.choice(colors)
        
        if pill_type == 'circle':
            radius = random.randint(8, 20)
            draw.ellipse([x-radius, y-radius, x+radius, y+radius], fill=color, outline='gray')
        elif pill_type == 'oval':
            w = random.randint(12, 25)
            h = random.randint(8, 15)
            draw.ellipse([x-w, y-h, x+w, y+h], fill=color, outline='gray')
        else:  # capsule
            w = random.randint(15, 30)
            h = random.randint(6, 12)
            # Capsule with two colors
            color2 = random.choice(colors)
            draw.ellipse([x-w, y-h, x+w, y+h], fill=color, outline='gray')
            draw.ellipse([x-w//2, y-h, x+w, y+h], fill=color2, outline='gray')
    
    return image

def test_realistic_drug_scenarios():
    """Test with realistic drug scenarios"""
    print("🧪 Testing Realistic Drug Detection Scenarios")
    print("=" * 70)
    
    test_cases = [
        ("Scattered Pills (Like Image 1)", create_pills_scattered_image()),
        ("White Powder (Like Image 2)", create_white_powder_image()),
        ("Cannabis Material (Like Image 3)", create_cannabis_image()),
        ("Mixed Pills (Like Image 4)", create_mixed_pills_image()),
    ]
    
    for test_name, test_image in test_cases:
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
            
            # Analyze drugs detection specifically
            print(f"\n💊 DRUGS ANALYSIS:")
            if drugs_category:
                drugs_confidence = drugs_category.get('confidence', 0)
                drugs_flagged = drugs_category.get('flagged', False)
                
                print(f"   Drugs Confidence: {drugs_confidence:.1%}")
                print(f"   Current Threshold: 50%")
                print(f"   Should be flagged: {drugs_confidence > 0.5}")
                print(f"   Actually flagged: {drugs_flagged}")
                
                if test_name.startswith("Scattered Pills") or test_name.startswith("White Powder") or test_name.startswith("Cannabis") or test_name.startswith("Mixed Pills"):
                    if drugs_confidence > 0.7:
                        print("   🎉 EXCELLENT: High confidence for obvious drug content!")
                    elif drugs_confidence > 0.5:
                        print("   ✅ GOOD: Moderate confidence, properly flagged")
                    elif drugs_confidence > 0.3:
                        print("   ⚠️  ISSUE: Detected but confidence too low (not flagged)")
                    else:
                        print("   ❌ PROBLEM: Very low confidence for obvious drugs")
        else:
            print(f"❌ API Error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Connection Error: {e}")

if __name__ == "__main__":
    test_realistic_drug_scenarios()
    
    print(f"\n🎯 DRUG DETECTION ANALYSIS:")
    print(f"   📊 Expected Results for Drug Images:")
    print(f"     - Scattered Pills: Should be 70-90% confidence")
    print(f"     - White Powder: Should be 80-95% confidence") 
    print(f"     - Cannabis Material: Should be 60-80% confidence")
    print(f"     - Mixed Pills: Should be 75-90% confidence")
    print(f"   🚨 If confidence is below 50%, detection needs improvement") 