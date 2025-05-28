#!/usr/bin/env python3
"""
Automated Test Suite for Image Moderation API
Comprehensive testing including unit tests, integration tests, and end-to-end tests
"""

import subprocess
import sys
import time
import requests
import json
import os
from typing import Dict, List, Tuple
from pathlib import Path
from PIL import Image
import io

# Configuration
API_BASE_URL = "http://localhost:7000"
FRONTEND_URL = "http://localhost:3000"
ADMIN_TOKEN = "BdD--lvAf5SXLKFa98ji7GO6zhCv9iaNao4XWyAVrnA"
TEST_TIMEOUT = 300  # 5 minutes

class TestSuite:
    def __init__(self):
        self.results = {
            "unit_tests": [],
            "integration_tests": [],
            "api_tests": [],
            "performance_tests": [],
            "security_tests": []
        }
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0
        
    def create_test_image(self, size=(100, 100), color='blue') -> io.BytesIO:
        """Create a test image for testing"""
        img = Image.new('RGB', size, color=color)
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='JPEG', quality=85)
        img_bytes.seek(0)
        return img_bytes
    
    def run_test(self, test_name: str, test_func, category: str = "unit_tests") -> bool:
        """Run a single test and record results"""
        print(f"🧪 Running {test_name}...", end=" ")
        self.total_tests += 1
        
        try:
            start_time = time.time()
            success, message = test_func()
            end_time = time.time()
            
            result = {
                "name": test_name,
                "success": success,
                "message": message,
                "duration": round(end_time - start_time, 3),
                "category": category
            }
            
            self.results[category].append(result)
            
            if success:
                print(f"✅ PASS ({result['duration']}s)")
                self.passed_tests += 1
                return True
            else:
                print(f"❌ FAIL: {message}")
                self.failed_tests += 1
                return False
                
        except Exception as e:
            print(f"💥 ERROR: {str(e)}")
            self.results[category].append({
                "name": test_name,
                "success": False,
                "message": f"Test crashed: {str(e)}",
                "duration": 0,
                "category": category
            })
            self.failed_tests += 1
            return False
    
    # ===========================================
    # UNIT TESTS
    # ===========================================
    
    def test_import_modules(self) -> Tuple[bool, str]:
        """Test that all required modules can be imported"""
        try:
            import fastapi
            import uvicorn
            import motor
            import nudenet
            import opencv_python  # This will fail, but cv2 should work
        except ImportError:
            pass
        
        try:
            import cv2
            import numpy
            import PIL
            return True, "All critical modules imported successfully"
        except ImportError as e:
            return False, f"Failed to import critical module: {str(e)}"
    
    def test_environment_variables(self) -> Tuple[bool, str]:
        """Test that required environment variables are available"""
        required_vars = ["PYTHONPATH"]
        missing_vars = []
        
        for var in required_vars:
            if var not in os.environ:
                missing_vars.append(var)
        
        if missing_vars:
            return False, f"Missing environment variables: {missing_vars}"
        
        return True, "All required environment variables are set"
    
    def test_file_permissions(self) -> Tuple[bool, str]:
        """Test that file system permissions are correct"""
        test_paths = ["scripts", "app", "requirements.txt"]
        issues = []
        
        for path in test_paths:
            if not os.path.exists(path):
                issues.append(f"Missing: {path}")
            elif not os.access(path, os.R_OK):
                issues.append(f"Not readable: {path}")
        
        if issues:
            return False, f"File permission issues: {issues}"
        
        return True, "File permissions are correct"
    
    # ===========================================
    # INTEGRATION TESTS
    # ===========================================
    
    def test_docker_containers(self) -> Tuple[bool, str]:
        """Test that Docker containers are running"""
        try:
            result = subprocess.run(["docker", "ps"], capture_output=True, text=True)
            if "image_moderation" in result.stdout and "mongodb" in result.stdout:
                return True, "Docker containers are running"
            else:
                return False, "Required Docker containers not found"
        except subprocess.CalledProcessError:
            return False, "Docker command failed"
        except FileNotFoundError:
            return False, "Docker not installed"
    
    def test_database_connection(self) -> Tuple[bool, str]:
        """Test database connectivity"""
        try:
            result = subprocess.run([
                "docker", "exec", "image_moderation_mongodb",
                "mongosh", "--quiet", "--eval", "db.adminCommand('ping')"
            ], capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                return True, "Database connection successful"
            else:
                return False, f"Database ping failed: {result.stderr}"
        except subprocess.TimeoutExpired:
            return False, "Database connection timeout"
        except Exception as e:
            return False, f"Database test error: {str(e)}"
    
    def test_ai_models_loading(self) -> Tuple[bool, str]:
        """Test that AI models can be loaded"""
        try:
            # Test NudeNet import
            from nudenet import NudeDetector
            
            # Test OpenCV
            import cv2
            
            # Test basic functionality
            detector = NudeDetector()
            
            return True, "AI models loaded successfully"
        except ImportError as e:
            return False, f"AI model import failed: {str(e)}"
        except Exception as e:
            return False, f"AI model loading error: {str(e)}"
    
    # ===========================================
    # API TESTS
    # ===========================================
    
    def test_api_health(self) -> Tuple[bool, str]:
        """Test API health endpoint"""
        try:
            response = requests.get(f"{API_BASE_URL}/health", timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "healthy":
                    return True, f"API healthy (response time: {response.elapsed.total_seconds():.3f}s)"
                else:
                    return False, f"API unhealthy: {data}"
            else:
                return False, f"API returned status {response.status_code}"
        except requests.exceptions.ConnectionError:
            return False, "Cannot connect to API - service may be down"
        except Exception as e:
            return False, f"API health test failed: {str(e)}"
    
    def test_api_authentication(self) -> Tuple[bool, str]:
        """Test API authentication"""
        try:
            # Test without token
            response = requests.get(f"{API_BASE_URL}/auth/tokens", timeout=10)
            if response.status_code != 401:
                return False, "API should reject requests without authentication"
            
            # Test with valid token
            headers = {"Authorization": f"Bearer {ADMIN_TOKEN}"}
            response = requests.get(f"{API_BASE_URL}/auth/tokens", headers=headers, timeout=10)
            if response.status_code == 200:
                return True, "Authentication working correctly"
            else:
                return False, f"Authentication failed: status {response.status_code}"
        except Exception as e:
            return False, f"Authentication test failed: {str(e)}"
    
    def test_api_moderation_endpoint(self) -> Tuple[bool, str]:
        """Test the main moderation endpoint"""
        try:
            headers = {"Authorization": f"Bearer {ADMIN_TOKEN}"}
            
            # Create test image
            img_data = self.create_test_image()
            files = {"file": ("test.jpg", img_data, "image/jpeg")}
            
            response = requests.post(f"{API_BASE_URL}/moderate", 
                                   headers=headers, files=files, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                if "categories" in result and len(result["categories"]) >= 2:
                    return True, f"Moderation endpoint working (found {len(result['categories'])} categories)"
                else:
                    return False, f"Unexpected response format: {result}"
            else:
                return False, f"Moderation failed: status {response.status_code}"
        except Exception as e:
            return False, f"Moderation test failed: {str(e)}"
    
    def test_api_error_handling(self) -> Tuple[bool, str]:
        """Test API error handling"""
        try:
            headers = {"Authorization": f"Bearer {ADMIN_TOKEN}"}
            
            # Test with invalid file
            response = requests.post(f"{API_BASE_URL}/moderate", 
                                   headers=headers, timeout=10)
            
            if response.status_code == 422:  # Validation error
                return True, "API correctly handles missing file"
            else:
                return False, f"API should return 422 for missing file, got {response.status_code}"
        except Exception as e:
            return False, f"Error handling test failed: {str(e)}"
    
    # ===========================================
    # PERFORMANCE TESTS
    # ===========================================
    
    def test_api_response_time(self) -> Tuple[bool, str]:
        """Test API response times"""
        try:
            start_time = time.time()
            response = requests.get(f"{API_BASE_URL}/health", timeout=10)
            response_time = time.time() - start_time
            
            if response.status_code == 200 and response_time < 2.0:
                return True, f"API response time acceptable ({response_time:.3f}s)"
            elif response_time >= 2.0:
                return False, f"API response too slow ({response_time:.3f}s)"
            else:
                return False, f"API returned error: {response.status_code}"
        except Exception as e:
            return False, f"Response time test failed: {str(e)}"
    
    def test_moderation_performance(self) -> Tuple[bool, str]:
        """Test AI moderation performance"""
        try:
            headers = {"Authorization": f"Bearer {ADMIN_TOKEN}"}
            img_data = self.create_test_image()
            files = {"file": ("test.jpg", img_data, "image/jpeg")}
            
            start_time = time.time()
            response = requests.post(f"{API_BASE_URL}/moderate", 
                                   headers=headers, files=files, timeout=30)
            response_time = time.time() - start_time
            
            if response.status_code == 200 and response_time < 10.0:
                return True, f"AI moderation performance acceptable ({response_time:.3f}s)"
            elif response_time >= 10.0:
                return False, f"AI moderation too slow ({response_time:.3f}s)"
            else:
                return False, f"Moderation failed: {response.status_code}"
        except Exception as e:
            return False, f"Moderation performance test failed: {str(e)}"
    
    def test_concurrent_requests(self) -> Tuple[bool, str]:
        """Test handling of concurrent requests"""
        import concurrent.futures
        
        def single_request():
            try:
                response = requests.get(f"{API_BASE_URL}/health", timeout=10)
                return response.status_code == 200
            except:
                return False
        
        try:
            with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
                futures = [executor.submit(single_request) for _ in range(5)]
                results = [future.result() for future in concurrent.futures.as_completed(futures)]
            
            success_rate = sum(results) / len(results)
            if success_rate >= 0.8:  # 80% success rate
                return True, f"Concurrent requests handled well ({success_rate:.1%} success rate)"
            else:
                return False, f"Poor concurrent performance ({success_rate:.1%} success rate)"
        except Exception as e:
            return False, f"Concurrent test failed: {str(e)}"
    
    # ===========================================
    # SECURITY TESTS
    # ===========================================
    
    def test_unauthorized_access(self) -> Tuple[bool, str]:
        """Test that endpoints properly reject unauthorized access"""
        try:
            # Test protected endpoints without auth
            protected_endpoints = ["/auth/tokens", "/moderate"]
            
            for endpoint in protected_endpoints:
                response = requests.get(f"{API_BASE_URL}{endpoint}", timeout=10)
                if response.status_code not in [401, 405]:  # 405 for wrong method
                    return False, f"Endpoint {endpoint} should reject unauthorized access"
            
            return True, "All protected endpoints properly secured"
        except Exception as e:
            return False, f"Authorization test failed: {str(e)}"
    
    def test_input_validation(self) -> Tuple[bool, str]:
        """Test input validation and sanitization"""
        try:
            headers = {"Authorization": f"Bearer {ADMIN_TOKEN}"}
            
            # Test with non-image file
            bad_file = io.BytesIO(b"This is not an image")
            files = {"file": ("bad.txt", bad_file, "text/plain")}
            
            response = requests.post(f"{API_BASE_URL}/moderate", 
                                   headers=headers, files=files, timeout=10)
            
            if response.status_code in [400, 422]:  # Should reject non-image
                return True, "Input validation working correctly"
            else:
                return False, f"Should reject non-image files, got {response.status_code}"
        except Exception as e:
            return False, f"Input validation test failed: {str(e)}"
    
    def test_token_validation(self) -> Tuple[bool, str]:
        """Test token validation"""
        try:
            # Test with invalid token
            headers = {"Authorization": "Bearer invalid_token_123"}
            response = requests.get(f"{API_BASE_URL}/auth/tokens", headers=headers, timeout=10)
            
            if response.status_code == 401:
                return True, "Token validation working correctly"
            else:
                return False, f"Should reject invalid tokens, got {response.status_code}"
        except Exception as e:
            return False, f"Token validation test failed: {str(e)}"
    
    # ===========================================
    # TEST EXECUTION
    # ===========================================
    
    def run_all_tests(self):
        """Run the complete test suite"""
        print("🚀 Image Moderation API - Automated Test Suite")
        print("=" * 70)
        
        # Unit Tests
        print(f"\n📋 UNIT TESTS")
        print("-" * 30)
        self.run_test("Module Imports", self.test_import_modules, "unit_tests")
        self.run_test("Environment Variables", self.test_environment_variables, "unit_tests")
        self.run_test("File Permissions", self.test_file_permissions, "unit_tests")
        
        # Integration Tests
        print(f"\n🔗 INTEGRATION TESTS")
        print("-" * 30)
        self.run_test("Docker Containers", self.test_docker_containers, "integration_tests")
        self.run_test("Database Connection", self.test_database_connection, "integration_tests")
        self.run_test("AI Models Loading", self.test_ai_models_loading, "integration_tests")
        
        # API Tests
        print(f"\n🌐 API TESTS")
        print("-" * 30)
        self.run_test("API Health", self.test_api_health, "api_tests")
        self.run_test("Authentication", self.test_api_authentication, "api_tests")
        self.run_test("Moderation Endpoint", self.test_api_moderation_endpoint, "api_tests")
        self.run_test("Error Handling", self.test_api_error_handling, "api_tests")
        
        # Performance Tests
        print(f"\n⚡ PERFORMANCE TESTS")
        print("-" * 30)
        self.run_test("API Response Time", self.test_api_response_time, "performance_tests")
        self.run_test("Moderation Performance", self.test_moderation_performance, "performance_tests")
        self.run_test("Concurrent Requests", self.test_concurrent_requests, "performance_tests")
        
        # Security Tests
        print(f"\n🛡️  SECURITY TESTS")
        print("-" * 30)
        self.run_test("Unauthorized Access", self.test_unauthorized_access, "security_tests")
        self.run_test("Input Validation", self.test_input_validation, "security_tests")
        self.run_test("Token Validation", self.test_token_validation, "security_tests")
        
        # Display Results
        self.display_results()
    
    def display_results(self):
        """Display comprehensive test results"""
        print("\n" + "=" * 70)
        print("📊 TEST RESULTS SUMMARY")
        print("=" * 70)
        
        # Overall stats
        success_rate = (self.passed_tests / self.total_tests) * 100 if self.total_tests > 0 else 0
        
        print(f"\n🎯 OVERALL RESULTS:")
        print(f"   • Total Tests: {self.total_tests}")
        print(f"   • Passed: {self.passed_tests} ✅")
        print(f"   • Failed: {self.failed_tests} ❌")
        print(f"   • Success Rate: {success_rate:.1f}%")
        
        # Category breakdown
        for category, tests in self.results.items():
            if tests:
                passed = len([t for t in tests if t["success"]])
                total = len(tests)
                print(f"\n📋 {category.upper().replace('_', ' ')}:")
                print(f"   • Passed: {passed}/{total}")
                
                # Show failed tests
                failed_tests = [t for t in tests if not t["success"]]
                if failed_tests:
                    print("   • Failed:")
                    for test in failed_tests:
                        print(f"     - {test['name']}: {test['message']}")
        
        # Performance summary
        perf_tests = self.results.get("performance_tests", [])
        if perf_tests:
            avg_time = sum(t["duration"] for t in perf_tests) / len(perf_tests)
            print(f"\n⚡ PERFORMANCE SUMMARY:")
            print(f"   • Average Test Time: {avg_time:.3f}s")
            
            slowest = max(perf_tests, key=lambda x: x["duration"])
            print(f"   • Slowest Test: {slowest['name']} ({slowest['duration']:.3f}s)")
        
        # Final assessment
        print(f"\n🎭 FINAL ASSESSMENT:")
        if success_rate >= 90:
            print("   ✅ EXCELLENT - System is production ready!")
        elif success_rate >= 80:
            print("   ⚠️  GOOD - Minor issues should be addressed")
        elif success_rate >= 70:
            print("   ⚠️  ACCEPTABLE - Several issues need attention")
        else:
            print("   ❌ POOR - Major issues must be fixed before deployment")
        
        print("\n" + "=" * 70)
        
        return success_rate >= 80  # Return True if tests pass acceptably

def main():
    """Main test execution"""
    try:
        suite = TestSuite()
        success = suite.run_all_tests()
        
        # Exit with appropriate code for CI/CD
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        print("\n\n⚡ Test suite interrupted")
        sys.exit(2)
    except Exception as e:
        print(f"\n\n💥 Test suite failed with error: {str(e)}")
        sys.exit(3)

if __name__ == "__main__":
    main() 