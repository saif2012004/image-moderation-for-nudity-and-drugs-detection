"""
Comprehensive Test Suite for Image Moderation API
Tests all endpoints, authentication, AI detection, and error handling
"""

import pytest
import asyncio
import io
import os
from PIL import Image
import numpy as np
from httpx import AsyncClient
from fastapi.testclient import TestClient

# Import your app
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from app.main import app
from app.database import get_database

# Test client
client = TestClient(app)

# Test configuration
TEST_TOKEN = "BdD--lvAf5SXLKFa98ji7GO6zhCv9iaNao4XWyAVrnA"
INVALID_TOKEN = "invalid_token_12345"
BASE_URL = "http://localhost:7000"

class TestHealthCheck:
    """Test health check endpoint"""
    
    def test_health_endpoint(self):
        """Test that health endpoint returns 200"""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"

class TestAuthentication:
    """Test authentication and token management"""
    
    def test_missing_token(self):
        """Test API call without token returns 401"""
        response = client.post("/moderate")
        assert response.status_code == 401
        
    def test_invalid_token(self):
        """Test API call with invalid token returns 401"""
        headers = {"Authorization": f"Bearer {INVALID_TOKEN}"}
        response = client.post("/moderate", headers=headers)
        assert response.status_code == 401
        
    def test_valid_token(self):
        """Test API call with valid token (without file should return 422)"""
        headers = {"Authorization": f"Bearer {TEST_TOKEN}"}
        response = client.post("/moderate", headers=headers)
        # Should return 422 (validation error) not 401 (auth error)
        assert response.status_code == 422
        
    def test_create_token_admin_required(self):
        """Test creating token requires admin privileges"""
        headers = {"Authorization": f"Bearer {INVALID_TOKEN}"}
        response = client.post("/auth/tokens", 
                              headers=headers,
                              json={"isAdmin": False})
        assert response.status_code == 401
        
    def test_create_token_success(self):
        """Test successful token creation"""
        headers = {"Authorization": f"Bearer {TEST_TOKEN}"}
        response = client.post("/auth/tokens", 
                              headers=headers,
                              json={"isAdmin": False})
        assert response.status_code == 200
        assert "token" in response.json()
        
    def test_list_tokens(self):
        """Test listing all tokens"""
        headers = {"Authorization": f"Bearer {TEST_TOKEN}"}
        response = client.get("/auth/tokens", headers=headers)
        assert response.status_code == 200
        assert isinstance(response.json(), list)
        
    def test_delete_nonexistent_token(self):
        """Test deleting non-existent token"""
        headers = {"Authorization": f"Bearer {TEST_TOKEN}"}
        response = client.delete(f"/auth/tokens/{INVALID_TOKEN}", headers=headers)
        assert response.status_code == 404

class TestImageGeneration:
    """Helper class for generating test images"""
    
    @staticmethod
    def create_colored_image(color, size=(100, 100)):
        """Create a solid colored image"""
        image = Image.new("RGB", size, color)
        img_byte_arr = io.BytesIO()
        image.save(img_byte_arr, format='JPEG')
        img_byte_arr.seek(0)
        return img_byte_arr
    
    @staticmethod
    def create_skin_tone_image(size=(200, 200)):
        """Create an image with skin tones"""
        # Create image with skin-like colors
        image = Image.new("RGB", size, (222, 184, 135))  # Burlywood/skin tone
        img_byte_arr = io.BytesIO()
        image.save(img_byte_arr, format='JPEG')
        img_byte_arr.seek(0)
        return img_byte_arr
    
    @staticmethod
    def create_pill_like_image(size=(150, 150)):
        """Create an image that might trigger drug detection"""
        # Create white image with circular patterns
        image = Image.new("RGB", size, (255, 255, 255))
        # Add some circular patterns
        from PIL import ImageDraw
        draw = ImageDraw.Draw(image)
        # Draw several circles that might look like pills
        for i in range(0, size[0], 30):
            for j in range(0, size[1], 30):
                draw.ellipse([i, j, i+20, j+20], fill=(240, 240, 240), outline=(200, 200, 200))
        
        img_byte_arr = io.BytesIO()
        image.save(img_byte_arr, format='JPEG')
        img_byte_arr.seek(0)
        return img_byte_arr

class TestImageModeration:
    """Test image moderation functionality"""
    
    def test_moderate_without_file(self):
        """Test moderation without file returns validation error"""
        headers = {"Authorization": f"Bearer {TEST_TOKEN}"}
        response = client.post("/moderate", headers=headers)
        assert response.status_code == 422
        
    def test_moderate_safe_image(self):
        """Test moderation of safe colored image"""
        headers = {"Authorization": f"Bearer {TEST_TOKEN}"}
        
        # Create a safe blue image
        image_data = TestImageGeneration.create_colored_image((0, 0, 255))  # Blue
        
        files = {"file": ("test_blue.jpg", image_data, "image/jpeg")}
        response = client.post("/moderate", headers=headers, files=files)
        
        assert response.status_code == 200
        result = response.json()
        
        # Verify response structure
        assert "filename" in result
        assert "safe" in result
        assert "categories" in result
        assert "overall_confidence" in result
        assert "timestamp" in result
        
        # Should have exactly 2 categories
        assert len(result["categories"]) == 2
        category_names = [cat["category"] for cat in result["categories"]]
        assert "nudity" in category_names
        assert "drugs" in category_names
        
        # Safe image should be marked as safe
        assert result["safe"] is True
        
    def test_moderate_skin_tone_image(self):
        """Test moderation of image with skin tones"""
        headers = {"Authorization": f"Bearer {TEST_TOKEN}"}
        
        # Create image with skin tones
        image_data = TestImageGeneration.create_skin_tone_image()
        
        files = {"file": ("test_skin.jpg", image_data, "image/jpeg")}
        response = client.post("/moderate", headers=headers, files=files)
        
        assert response.status_code == 200
        result = response.json()
        
        # Should still be safe but might have higher nudity confidence
        nudity_category = next(cat for cat in result["categories"] if cat["category"] == "nudity")
        assert nudity_category["confidence"] >= 0.0
        
    def test_moderate_pill_like_image(self):
        """Test moderation of image that might trigger drug detection"""
        headers = {"Authorization": f"Bearer {TEST_TOKEN}"}
        
        # Create image with pill-like patterns
        image_data = TestImageGeneration.create_pill_like_image()
        
        files = {"file": ("test_pills.jpg", image_data, "image/jpeg")}
        response = client.post("/moderate", headers=headers, files=files)
        
        assert response.status_code == 200
        result = response.json()
        
        # Check drugs detection
        drugs_category = next(cat for cat in result["categories"] if cat["category"] == "drugs")
        assert drugs_category["confidence"] >= 0.0
        
    def test_moderate_invalid_file_type(self):
        """Test moderation with invalid file type"""
        headers = {"Authorization": f"Bearer {TEST_TOKEN}"}
        
        # Create a text file instead of image
        text_data = io.BytesIO(b"This is not an image")
        files = {"file": ("test.txt", text_data, "text/plain")}
        
        response = client.post("/moderate", headers=headers, files=files)
        # Should return error for invalid image
        assert response.status_code in [400, 422]
        
    def test_moderate_large_image(self):
        """Test moderation of large image"""
        headers = {"Authorization": f"Bearer {TEST_TOKEN}"}
        
        # Create a larger image
        image_data = TestImageGeneration.create_colored_image((128, 255, 0), (500, 500))  # Green
        
        files = {"file": ("test_large.jpg", image_data, "image/jpeg")}
        response = client.post("/moderate", headers=headers, files=files)
        
        assert response.status_code == 200
        result = response.json()
        assert result["safe"] is True

class TestAIDetection:
    """Test AI detection systems"""
    
    def test_nudity_detection_baseline(self):
        """Test nudity detection on simple images"""
        headers = {"Authorization": f"Bearer {TEST_TOKEN}"}
        
        # Test with different colored images
        colors = [
            (255, 0, 0),    # Red
            (0, 255, 0),    # Green
            (0, 0, 255),    # Blue
            (255, 255, 255), # White
            (0, 0, 0),      # Black
        ]
        
        for color in colors:
            image_data = TestImageGeneration.create_colored_image(color)
            files = {"file": ("test_color.jpg", image_data, "image/jpeg")}
            response = client.post("/moderate", headers=headers, files=files)
            
            assert response.status_code == 200
            result = response.json()
            
            nudity_category = next(cat for cat in result["categories"] if cat["category"] == "nudity")
            # Simple colored images should have very low nudity confidence
            assert nudity_category["confidence"] < 0.1
            
    def test_drugs_detection_baseline(self):
        """Test drugs detection on simple images"""
        headers = {"Authorization": f"Bearer {TEST_TOKEN}"}
        
        # Simple colored image should have low drug confidence
        image_data = TestImageGeneration.create_colored_image((100, 150, 200))
        files = {"file": ("test_color.jpg", image_data, "image/jpeg")}
        response = client.post("/moderate", headers=headers, files=files)
        
        assert response.status_code == 200
        result = response.json()
        
        drugs_category = next(cat for cat in result["categories"] if cat["category"] == "drugs")
        # Simple images should have low drug confidence
        assert drugs_category["confidence"] < 0.2

class TestErrorHandling:
    """Test error handling and edge cases"""
    
    def test_empty_file(self):
        """Test handling of empty file"""
        headers = {"Authorization": f"Bearer {TEST_TOKEN}"}
        
        empty_data = io.BytesIO(b"")
        files = {"file": ("empty.jpg", empty_data, "image/jpeg")}
        
        response = client.post("/moderate", headers=headers, files=files)
        # Should handle empty file gracefully
        assert response.status_code in [400, 422]
        
    def test_corrupted_image(self):
        """Test handling of corrupted image data"""
        headers = {"Authorization": f"Bearer {TEST_TOKEN}"}
        
        # Create corrupted image data
        corrupted_data = io.BytesIO(b"JFIF\x00\x01\x01\x01corrupted")
        files = {"file": ("corrupted.jpg", corrupted_data, "image/jpeg")}
        
        response = client.post("/moderate", headers=headers, files=files)
        # Should handle corrupted image gracefully
        assert response.status_code in [400, 422]

class TestResponseValidation:
    """Test response format validation"""
    
    def test_response_format_consistency(self):
        """Test that all responses follow the same format"""
        headers = {"Authorization": f"Bearer {TEST_TOKEN}"}
        
        # Test with multiple different images
        test_images = [
            TestImageGeneration.create_colored_image((255, 0, 0)),    # Red
            TestImageGeneration.create_colored_image((0, 255, 0)),    # Green
            TestImageGeneration.create_skin_tone_image(),             # Skin tone
        ]
        
        for i, image_data in enumerate(test_images):
            files = {"file": (f"test_{i}.jpg", image_data, "image/jpeg")}
            response = client.post("/moderate", headers=headers, files=files)
            
            assert response.status_code == 200
            result = response.json()
            
            # Validate response structure
            required_fields = ["filename", "safe", "categories", "overall_confidence", "timestamp"]
            for field in required_fields:
                assert field in result, f"Missing field: {field}"
            
            # Validate categories structure
            assert len(result["categories"]) == 2
            for category in result["categories"]:
                assert "category" in category
                assert "confidence" in category
                assert "flagged" in category
                assert 0.0 <= category["confidence"] <= 1.0
                assert isinstance(category["flagged"], bool)

class TestConcurrency:
    """Test concurrent requests"""
    
    @pytest.mark.asyncio
    async def test_concurrent_requests(self):
        """Test handling of concurrent moderation requests"""
        headers = {"Authorization": f"Bearer {TEST_TOKEN}"}
        
        async with AsyncClient(app=app, base_url=BASE_URL) as ac:
            # Create multiple concurrent requests
            tasks = []
            for i in range(5):
                image_data = TestImageGeneration.create_colored_image((i*50, 100, 150))
                files = {"file": (f"test_concurrent_{i}.jpg", image_data.getvalue(), "image/jpeg")}
                task = ac.post("/moderate", headers=headers, files=files)
                tasks.append(task)
            
            # Execute all requests concurrently
            responses = await asyncio.gather(*tasks)
            
            # All should succeed
            for response in responses:
                assert response.status_code == 200
                result = response.json()
                assert "safe" in result

class TestPerformance:
    """Test performance characteristics"""
    
    def test_response_time_reasonable(self):
        """Test that response times are reasonable"""
        import time
        
        headers = {"Authorization": f"Bearer {TEST_TOKEN}"}
        image_data = TestImageGeneration.create_colored_image((128, 128, 128))
        files = {"file": ("test_perf.jpg", image_data, "image/jpeg")}
        
        start_time = time.time()
        response = client.post("/moderate", headers=headers, files=files)
        end_time = time.time()
        
        assert response.status_code == 200
        # Response should be reasonably fast (under 10 seconds)
        assert (end_time - start_time) < 10.0

if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"]) 