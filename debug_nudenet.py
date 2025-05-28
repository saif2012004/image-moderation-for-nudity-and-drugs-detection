#!/usr/bin/env python3
"""
Debug NudeNet directly to see what's happening
"""

import io
import os
from PIL import Image

def test_nudenet_directly():
    """Test NudeNet directly to debug issues"""
    print("🔍 Testing NudeNet Directly")
    print("=" * 50)
    
    try:
        from nudenet import NudeDetector
        print("✅ NudeNet imported successfully")
        
        # Initialize detector
        print("🔄 Initializing NudeDetector...")
        detector = NudeDetector()
        print("✅ NudeDetector initialized")
        
        # Create test images
        print("\n📸 Creating test images...")
        
        # Test 1: Simple red image
        red_img = Image.new('RGB', (224, 224), 'red')
        red_img.save('test_red.jpg', 'JPEG')
        print("✅ Created red test image")
        
        # Test 2: Skin-colored image
        skin_img = Image.new('RGB', (224, 224), (222, 184, 135))
        skin_img.save('test_skin.jpg', 'JPEG')
        print("✅ Created skin test image")
        
        # Test 3: More complex skin pattern
        complex_img = Image.new('RGB', (224, 224), (222, 184, 135))
        # Add some variation
        pixels = complex_img.load()
        for i in range(50, 150):
            for j in range(50, 150):
                pixels[i, j] = (200, 160, 120)  # Darker skin tone
        complex_img.save('test_complex.jpg', 'JPEG')
        print("✅ Created complex test image")
        
        # Test detection on each image
        test_images = ['test_red.jpg', 'test_skin.jpg', 'test_complex.jpg']
        
        for img_path in test_images:
            print(f"\n🔍 Testing {img_path}:")
            try:
                detections = detector.detect(img_path)
                print(f"   Raw detections: {len(detections)} items")
                
                if detections:
                    for i, detection in enumerate(detections):
                        class_name = detection.get('class', 'unknown')
                        score = detection.get('score', 0)
                        box = detection.get('box', [])
                        print(f"   Detection {i+1}: {class_name} (score: {score:.3f}, box: {box})")
                else:
                    print("   ❌ No detections found")
                    
            except Exception as e:
                print(f"   ❌ Error detecting {img_path}: {e}")
                import traceback
                traceback.print_exc()
        
        # Test with a real photo-like image
        print(f"\n🔍 Testing with gradient image (more photo-like):")
        try:
            # Create gradient image that might look more like a photo
            gradient_img = Image.new('RGB', (224, 224))
            pixels = gradient_img.load()
            for i in range(224):
                for j in range(224):
                    # Create a gradient from skin to darker
                    r = int(222 - (i * 50 / 224))
                    g = int(184 - (i * 30 / 224))
                    b = int(135 - (i * 20 / 224))
                    pixels[i, j] = (max(0, r), max(0, g), max(0, b))
            
            gradient_img.save('test_gradient.jpg', 'JPEG')
            
            detections = detector.detect('test_gradient.jpg')
            print(f"   Gradient detections: {len(detections)} items")
            
            if detections:
                for detection in detections:
                    class_name = detection.get('class', 'unknown')
                    score = detection.get('score', 0)
                    print(f"   - {class_name}: {score:.3f}")
            else:
                print("   ❌ No detections in gradient image")
                
        except Exception as e:
            print(f"   ❌ Error with gradient: {e}")
        
        # Clean up test files
        print(f"\n🧹 Cleaning up test files...")
        for img_path in ['test_red.jpg', 'test_skin.jpg', 'test_complex.jpg', 'test_gradient.jpg']:
            if os.path.exists(img_path):
                os.remove(img_path)
                print(f"   Removed {img_path}")
        
        print(f"\n🎯 DIAGNOSIS:")
        print("If NudeNet finds 0 detections in all images, possible issues:")
        print("1. Model not loading properly")
        print("2. Input image format/size issues")
        print("3. Detection thresholds too high")
        print("4. Model files corrupted/missing")
        
    except ImportError as e:
        print(f"❌ Cannot import NudeNet: {e}")
    except Exception as e:
        print(f"❌ Error testing NudeNet: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_nudenet_directly() 